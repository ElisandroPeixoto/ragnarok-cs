# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Ragnarok Chaos Saga: a Ragnarok Online–themed desktop RPG. Two Python processes:

- `backend/` — FastAPI + async SQLAlchemy (SQLite via aiosqlite), serves `/api/v1/characters` and `/api/v1/maps` on port **8001**.
- `frontend/` — Flet 0.86 desktop app (declarative `@ft.component` / `ft.use_state` style with `ft.Router`), talks to the backend over httpx.

There is no test suite, linter config, or build step. Comments/docstrings are a mix of English and Portuguese.

## Commands

`requirements.txt` is UTF-16 encoded (pip handles it). The `tools/` scripts additionally need Pillow and numpy, which are not listed.

Both apps use imports relative to their own folder (`from core.config import ...`, `from services.x import ...`), so run them **from inside that folder**:

```bash
pip install -r requirements.txt
```

```bash
cd backend && python seed_data.py   # creates tables + inserts maps/NPCs/monsters (idempotent); creates ./ragnarokcs.db
```

```bash
cd backend && python main.py        # uvicorn on 0.0.0.0:8001
```

```bash
cd frontend && python main.py       # Flet desktop window; assets served from ../assets
```

Start the backend **before** the frontend: `frontend/routes.py` calls `MapService.get_map_ids_sync()` at import time to register one `/map/<map_id>` route per map; if the backend is down, no map routes exist (it silently returns `[]`).

Sprite pipeline (RO `.spr`/`.act` sources live in the git-ignored `art_source/`):

```bash
python tools/ro_to_sheet.py art_source/novice novice --head art_source/novice_head --weapon art_source/weapon --preview preview.png
```

Outputs `assets/sprites/<name>/<name>_sheet.png` + `<name>.json`: frame size, anchor = feet position, and `clips` keyed `<anim>_<facing>` (combat clips on se/sw/nw/ne; players also get `stand_s`, the front-facing out-of-combat pose with head turns), each with a `box` of its drawn area. The battle uses `idle_*` etc.; character selection/creation/profile use `stand_s` via `components/job_sprite.py`, falling back to a GIF in `services/sprite_selector.py` for jobs without a sheet. `tools/spr_to_frames.py` holds the `.spr`/`.act` readers and can dump raw frames (`--stand` dumps only the stand pose's).

## Architecture

### Backend
- `core/config.py` holds `Settings` (pydantic-settings, reads `.env`) **and** `DBBaseModel` (the declarative base). `DEBUG=True` selects `DB_URL_DEV`.
- `models/__all_models.py` must import every model so `metadata.create_all` sees them; `main.py`/`create_tables.py`/`seed_data.py` import it. Add new models there.
- `api/v1/api.py` mounts endpoint routers; endpoints use `Depends(get_session)` from `core/deps.py`.
- Map endpoint (`endpoints/maps.py`) eager-loads NPCs, monster spawns and connections, then flattens them with `to_response()` into the dict shape the frontend consumes — keep that shape stable when changing models.
- No admin UI or migrations: new game data goes into `seed_data.py`; schema changes require deleting `ragnarokcs.db` and reseeding.

### Frontend
- `main.py` → `ft.Router(routes)`; `routes.py` wraps each page component in a `ft.View` via `view_wrapper`. Navigation uses `ft.context.page.navigate(route)`; helpers live in `services/map_router_manager.py`.
- `services/session_state.py` is a module-level global store (current character, route to return to after battle).
- `services/api_client.py` exposes a shared `api` (`ApiClient`, raises `ApiError`); per-domain wrappers are `CharacterService`, `MapService`.
- `themes.py` holds all colors; `config.ASSETS_DIR` points at the repo-root `assets/`. Asset paths in data/DB are relative to that folder.

### Battle system (currently mocked)
Battle runs entirely client-side; units come from `frontend/mockup.py` (`INITIAL_UNITS`) and skills from `SKILLS` in `services/battle_actions.py` (marked TODO to move to the backend).

- `services/battle_state.py` — `BattleState`: plain-dict units, turn order, AP, turn timer, winner, `BattleLog`. Mutated in place; `state.version` is bumped to force re-renders.
- `services/battle_geometry.py` — `BoardConfig` (fixed 1100×700 stage, 10×10 isometric grid, 96×48 tiles) and tile↔pixel conversions.
- `services/battle_actions.py` — validation (`can_attack`, `can_move`) + execution (`perform_*`). Attacks require the target on the same row/column within range. Movement costs 1 AP per tile of the shortest 4-direction path (`find_path`, BFS around blocked tiles and living units); the player clicks a tile (hover previews the path).
- `services/battle_ai.py` — `iter_ai_turn` is a generator yielding after each enemy action so the page can re-render and pause between steps.
- `services/battle_animation.py` — loads sprite-sheet JSON (`get_sheet`, cached) and computes the current frame purely from `unit["anim"]`, `unit["anim_started"]` and `time.monotonic()`. Walking: `start_walk` moves `col`/`row` to the destination immediately and stores `walk_path`; while the `walk` clip plays, `board_position`/`walk_pose` interpolate the drawn position and facing tile by tile. Input and the enemy AI wait on `walk_remaining`.
- `pages/battle_page.py` — owns the `BattleState` via `use_state` and starts two async loops on mount: `turn_loop` (1s turn clock, drives enemy AI, locks input) and `anim_loop` (~12 fps re-render). Both stop when `state.closed` is set on unmount/leave. Any state change must call `refresh()`.
