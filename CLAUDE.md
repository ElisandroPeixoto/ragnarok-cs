# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Ragnarok Chaos Saga: a Ragnarok Online–themed desktop RPG. Two Python processes:

- `backend/` — FastAPI + async SQLAlchemy (SQLite via aiosqlite), serves `/api/v1/characters` and `/api/v1/maps` on port **8001**.
- `frontend/` — Flet 0.86 desktop app (declarative `@ft.component` / `ft.use_state` style with `ft.Router`), talks to the backend over httpx.

There is no test suite, linter config, or build step. Comments and docstrings are written in English. Detailed, human-oriented docs (in Portuguese) live in `docs/`; keep them in sync when changing behavior they describe.

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

Outputs `assets/sprites/<name>/<name>_sheet.png` + `<name>.json`: frame size, anchor = feet position, and `clips` keyed `<anim>_<facing>` (combat clips on se/sw/nw/ne; players also get `stand_s`, the front-facing out-of-combat pose with head turns), each with a `box` of its drawn area. The battle uses `idle_*` etc.; character selection/creation/profile use `stand_s` via `components/job_sprite.py`, falling back to a GIF in `services/sprite_selector.py` for jobs without a sheet. Monsters have no GIF: `components/sheet_sprite.py` `monster_sprite` loops their `idle_sw` clip on map cards and battle unit cards. Always pass `--kind monster` for monsters. `tools/spr_to_frames.py` holds the `.spr`/`.act` readers and can dump raw frames (`--stand` dumps only the stand pose's).

## Architecture

### Backend
- `core/config.py` holds `Settings` (pydantic-settings, reads `.env`) **and** `DBBaseModel` (the declarative base). `DEBUG=True` selects `DB_URL_DEV`.
- `models/__all_models.py` must import every model so `metadata.create_all` sees them; `main.py`/`create_tables.py`/`seed_data.py` import it. Add new models there.
- `api/v1/api.py` mounts endpoint routers; endpoints use `Depends(get_session)` from `core/deps.py`.
- Map endpoint (`endpoints/maps.py`) eager-loads places, NPCs, monster spawns and connections, then flattens them with `to_response()` into the dict shape the frontend consumes — keep that shape stable when changing models. `map_places` are the markers drawn over the town map (`maps.town_image`, 4:3; `NULL` = the screen shows an empty square) below the location's cover art (`maps.image`, the banner, cropped by `maps.art_position_y`; cover art lives in `assets/maps/covers/`, town maps in `assets/maps/towns/`) — `kind` area/building/exit, `x`/`y` as fractions of the town image; the town map zooms 1×–3× with the wheel, +/- buttons and drag (`services/map_zoom.py`, pure functions; labels keep their size); NPCs stand in an area (`place_id`) and have a `greeting`; maps have a `zone` (safe/hostile). The seed rewrites places and NPCs on every run.
- No admin UI or migrations: new game data goes into `seed_data.py`; schema changes require deleting `ragnarokcs.db` and reseeding.

### Frontend
- `main.py` → `ft.Router(routes)`; `routes.py` wraps each page component in a `ft.View` via `view_wrapper`. Navigation uses `ft.context.page.navigate(route)`; helpers live in `services/map_router_manager.py`.
- Travelling between maps (`map_router_manager.change_place`) shows `components/travel_dialog.py` — the character's `walk_se` clip looping in a modal pop up with a Cancel button below it — for `TRAVEL_SECONDS` (5), then saves the new place and opens the map; Cancel closes the pop up and nothing is saved. The dialog is built outside a render, so its animation is an async loop updating a container, not an `@ft.component`.
- `services/session_state.py` is a module-level global store (current character, route to return to after battle).
- `services/api_client.py` exposes a shared `api` (`ApiClient`, raises `ApiError`); per-domain wrappers are `CharacterService`, `MapService`.
- `themes.py` holds all colors; `config.ASSETS_DIR` points at the repo-root `assets/`. Asset paths in data/DB are relative to that folder.

### Battle system
Battle runs client-side, but its data comes from the backend. The map's Hunt button calls `POST /api/v1/battles/` (`endpoints/battles.py`) with `character_id` + `map_id`. The backend returns `{"units": {"hero"}, "skills": {...}, "monsters": [unit, ...]}`: the hunt is finite — the backend rolls 3 to 6 monsters (`core/battle_rules.py`), drawn from the map weighted by each monster's `MapMonsterModel.spawn_rate` (repeats allowed) — and ends when the hero kills them all (victory) or dies (defeat); the Leave button ends it with no result. The hero always plays first (`BattleState.turn_order`). Player battle data (sheet, avatar, AP, offsets, skills) lives on `JobModel`, enemy data on `MonsterModel`; skills are `SkillModel` rows linked through `job_skills`/`monster_skills` (`slot` 0 = the AI's main skill). The setup is stored in `session_state` and read by `battle_page`.

- `services/battle_state.py` — `BattleState(units, skills, board, monsters)`: plain-dict units, `state.skills`, turn order, AP, turn timer, winner, `BattleLog`. `place_unit` picks starting tiles (player column 0, enemies columns 7–9, random row); `spawn_monsters` places the hunt's monsters and `begin_round` drops dead ones at the start of a round; `check_battle_end` sets `winner` to `victory` or `defeat`, and `state.kills`/`monster_damage`/`damage_taken` feed the result pop up. Mutated in place; `state.version` is bumped to force re-renders.
- `services/battle_geometry.py` — `BoardConfig` (fixed 1100×700 stage, 10×10 isometric grid, 96×48 tiles) and tile↔pixel conversions.
- `services/battle_actions.py` — validation (`can_attack`, `can_move`) + execution (`perform_*`). Attacks require the target on the same row/column within range. Movement costs 1 AP per tile of the shortest 4-direction path (`find_path`, BFS around blocked tiles and living units); the player clicks a tile (hover previews the path).
- `services/battle_ai.py` — `iter_ai_turn` is a generator yielding after each enemy action so the page can re-render and pause between steps.
- `services/battle_animation.py` — loads sprite-sheet JSON (`get_sheet`, cached) and computes the current frame purely from `unit["anim"]`, `unit["anim_started"]` and `time.monotonic()`. Walking: `start_walk` moves `col`/`row` to the destination immediately and stores `walk_path`; while the `walk` clip plays, `board_position`/`walk_pose` interpolate the drawn position and facing tile by tile. Input and the enemy AI wait on `walk_remaining`. Damage popups: `perform_attack` appends `damage_popup(...)` to `state.damage_popups` (white when the hero hits, red when a monster does) and logs a `kind="attack"` entry; `popup_pose` gives the jump as a pure function of time and `battle_board` draws it above the sprites. EXP: the rule lives only in the backend (`backend/core/exp_rule.py`, see `docs/regra-de-experiencia.md`). When the hero kills a monster, `perform_attack` records it in `state.kills` and logs the monster's `exp_reward` (only for the log: nothing is saved yet). When a winner appears, `battle_page.finish_battle` (started once by `anim_loop`) POSTs `{victory, kills}` to `/characters/{id}/battle-result`, stores the report with `set_battle_result` and goes back to the map, where `map_screen` shows `battle_result_dialog` ("Victory!" gold / "Defeat" red, damage dealt per monster, damage received, EXP). Victory pays the EXP of all the monsters; defeat pays nothing and takes 20%; Leave does neither. The backend computes the EXP, level-ups (`backend/core/level_progression.py`, `docs/progressao-de-level.md`: `characters.exp` is the TOTAL EXP and the level derives from it) and the 20% death penalty (only on the EXP inside the current level, so no level is lost), and returns the character with `exp_progress`/`exp_needed` for the profile's EXP bar.
- Skill hotkeys: the hero's 1st–5th skill are bound to Q/W/E/R/T (`skills_panel.SKILL_KEYS`) and Space presses Turn End; `battle_page.handle_key` is assigned to `page.on_keyboard_event` on every render and cleared on unmount.
- `pages/battle_page.py` — owns the `BattleState` via `use_state` and starts two async loops on mount: `turn_loop` (1s turn clock, drives enemy AI, locks input) and `anim_loop` (~12 fps re-render). Both stop when `state.closed` is set on unmount/leave. Any state change must call `refresh()`.
