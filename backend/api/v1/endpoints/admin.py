"""Management API used by the admin panel in management/ (docs/gerenciamento.md).
It has no login: it is meant for the game's own machine. Everything here edits the database directly; running
seed_data.py again puts back the seed's values for monsters, classes, items and drops."""
import base64
import binascii
import json
import re
from pathlib import Path
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.character_model import CharacterModel
from models.monsters_model import MonsterModel
from models.jobs_model import JobModel
from models.items_model import ItemModel
from models.maps_model import MapModel
from models.monster_drop_model import MonsterDropModel
from schemas.admin_schema import (AdminCharacterUpdate, AdminMonsterUpdate, AdminJobUpdate, AdminItemUpdate,
                                  SpriteUpload)
from schemas.character_schema import CharacterSchemaResponse
from core.level_progression import MAX_EXP, level_for_exp, total_exp_for_level
from core.deps import get_session


router = APIRouter()

ASSETS_DIR = Path(__file__).resolve().parents[4] / "assets"
SPRITE_GROUPS = ("characters", "monsters")   # assets/sprites/<group>/<name>/

# monster combat modes: the keys of BEHAVIORS in frontend/services/battle_ai.py
AI_MODES = [
    {"id": "approach_and_attack", "label": "Approach and attack",
     "description": "Walks towards the nearest enemy and attacks when it is in range."},
    {"id": "attack_every_turn", "label": "Attack only",
     "description": "Never moves; attacks the nearest enemy when it is in range."},
    {"id": "passive", "label": "Passive", "description": "Does nothing."},
]
ITEM_TYPES = ["Misc"]   # the only type in the game for now (later Helmet, Armor, Cape, Boots, Sword, Rod, Axe...)
SHEET_NAME = re.compile(r"^[a-z0-9_]+$")


def not_found(what: str):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{what} not found")


def invalid(detail: str):
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)


def list_sheets(group: str) -> list[str]:
    folder = ASSETS_DIR / "sprites" / group
    if not folder.is_dir():
        return []
    return sorted(path.name for path in folder.iterdir() if (path / f"{path.name}.json").is_file())


def check_sheet(group: str, sheet: str) -> None:
    if sheet not in list_sheets(group):
        raise invalid(f"Sprite sheet '{sheet}' not found in assets/sprites/{group}/")


# ---------- options for the forms ----------
@router.get("/options")
async def get_options(db: AsyncSession = Depends(get_session)):
    """Lists the panel's selects need: AI modes, item types, classes, maps and the sprite sheets on disk"""
    jobs = (await db.execute(select(JobModel.name).order_by(JobModel.name))).scalars().all()
    maps = (await db.execute(select(MapModel.id, MapModel.name).order_by(MapModel.name))).all()
    return {
        "ai_modes": AI_MODES,
        "item_types": ITEM_TYPES,
        "jobs": list(jobs),
        "maps": [{"id": map_id, "name": name} for map_id, name in maps],
        "sheets": {group: list_sheets(group) for group in SPRITE_GROUPS},
    }


# ---------- characters ----------
@router.get("/characters", response_model=list[CharacterSchemaResponse])
async def admin_characters(db: AsyncSession = Depends(get_session)):
    return (await db.execute(select(CharacterModel).order_by(CharacterModel.id))).scalars().all()


@router.patch("/characters/{character_id}", response_model=CharacterSchemaResponse)
async def admin_update_character(character_id: int, update: AdminCharacterUpdate,
                                 db: AsyncSession = Depends(get_session)):
    character = await db.get(CharacterModel, character_id)
    if character is None:
        raise not_found("Character")
    values = update.model_dump(exclude_unset=True)
    if "job" in values and await db.get(JobModel, values["job"]) is None:
        raise invalid(f"Class '{values['job']}' does not exist")
    if "current_map_id" in values:
        game_map = await db.get(MapModel, values["current_map_id"])
        if game_map is None:
            raise invalid(f"Map '{values['current_map_id']}' does not exist")
        character.current_map = game_map.name
    # the level derives from the total EXP: a new level moves the EXP to that level's start
    if "level" in values:
        values["exp"] = total_exp_for_level(values.pop("level"))
    if "exp" in values:
        values["exp"] = min(values["exp"], MAX_EXP)
        character.level = level_for_exp(values["exp"])
    for field, value in values.items():
        setattr(character, field, value)
    if character.hp > character.max_hp:
        character.hp = character.max_hp
    await db.commit()
    await db.refresh(character)
    return character


# ---------- monsters ----------
async def monster_response(db: AsyncSession, monster: MonsterModel) -> dict:
    drops = (await db.execute(select(MonsterDropModel.item_id)
                              .where(MonsterDropModel.monster_id == monster.id))).scalars().all()
    return {"id": monster.id, "name": monster.name, "sheet": monster.sheet, "ai": monster.ai,
            "level": monster.level, "base_exp": monster.base_exp, "max_hp": monster.max_hp,
            "max_ap": monster.max_ap, "drops": sorted(drops)}


@router.get("/monsters")
async def admin_monsters(db: AsyncSession = Depends(get_session)):
    monsters = (await db.execute(select(MonsterModel).order_by(MonsterModel.name))).scalars().all()
    return [await monster_response(db, monster) for monster in monsters]


@router.patch("/monsters/{monster_id}")
async def admin_update_monster(monster_id: int, update: AdminMonsterUpdate, db: AsyncSession = Depends(get_session)):
    monster = await db.get(MonsterModel, monster_id)
    if monster is None:
        raise not_found("Monster")
    values = update.model_dump(exclude_unset=True)
    if "ai" in values and values["ai"] not in {mode["id"] for mode in AI_MODES}:
        raise invalid(f"Unknown combat mode '{values['ai']}'")
    if "sheet" in values:
        check_sheet("monsters", values["sheet"])
    drops = values.pop("drops", None)
    if drops is not None:
        known = set((await db.execute(select(ItemModel.id))).scalars().all())
        unknown = sorted(set(drops) - known)
        if unknown:
            raise invalid(f"Unknown items: {', '.join(unknown)}")
        await db.execute(delete(MonsterDropModel).where(MonsterDropModel.monster_id == monster.id))
        for item_id in sorted(set(drops)):
            db.add(MonsterDropModel(monster_id=monster.id, item_id=item_id))
    for field, value in values.items():
        setattr(monster, field, value)
    await db.commit()
    await db.refresh(monster)
    return await monster_response(db, monster)


# ---------- classes (jobs) ----------
def job_response(job: JobModel) -> dict:
    return {"name": job.name, "sheet": job.sheet, "avatar": job.avatar, "max_ap": job.max_ap}


@router.get("/jobs")
async def admin_jobs(db: AsyncSession = Depends(get_session)):
    return [job_response(job) for job in (await db.execute(select(JobModel).order_by(JobModel.name))).scalars()]


@router.patch("/jobs/{name}")
async def admin_update_job(name: str, update: AdminJobUpdate, db: AsyncSession = Depends(get_session)):
    job = await db.get(JobModel, name)
    if job is None:
        raise not_found("Class")
    values = update.model_dump(exclude_unset=True)
    if "sheet" in values:
        check_sheet("characters", values["sheet"])
    for field, value in values.items():
        setattr(job, field, value)
    await db.commit()
    await db.refresh(job)
    return job_response(job)


# ---------- items ----------
def item_response(item: ItemModel, dropped_by: list[str]) -> dict:
    return {"id": item.id, "name": item.name, "type": item.type, "description": item.description,
            "drop_rate": item.drop_rate, "icon": item.icon, "collection": item.collection,
            "dropped_by": dropped_by}


async def dropped_by_map(db: AsyncSession) -> dict[str, list[str]]:
    rows = (await db.execute(select(MonsterDropModel.item_id, MonsterModel.name)
                             .join(MonsterModel, MonsterModel.id == MonsterDropModel.monster_id))).all()
    result: dict[str, list[str]] = {}
    for item_id, monster_name in rows:
        result.setdefault(item_id, []).append(monster_name)
    return {item_id: sorted(names) for item_id, names in result.items()}


@router.get("/items")
async def admin_items(db: AsyncSession = Depends(get_session)):
    dropped_by = await dropped_by_map(db)
    items = (await db.execute(select(ItemModel).order_by(ItemModel.name))).scalars().all()
    return [item_response(item, dropped_by.get(item.id, [])) for item in items]


@router.patch("/items/{item_id}")
async def admin_update_item(item_id: str, update: AdminItemUpdate, db: AsyncSession = Depends(get_session)):
    item = await db.get(ItemModel, item_id)
    if item is None:
        raise not_found("Item")
    values = update.model_dump(exclude_unset=True)
    if "type" in values and values["type"] not in ITEM_TYPES:
        raise invalid(f"Unknown item type '{values['type']}'")
    for field, value in values.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item_response(item, (await dropped_by_map(db)).get(item.id, []))


# ---------- sprite sheets ----------
@router.get("/sprites")
async def admin_sprites():
    """Every sheet on disk with its JSON (frame size, anchor, clips), for the previews"""
    sheets = []
    for group in SPRITE_GROUPS:
        for name in list_sheets(group):
            data = json.loads((ASSETS_DIR / "sprites" / group / name / f"{name}.json").read_text(encoding="utf-8"))
            sheets.append({"group": group, "name": name, "json": data})
    return sheets


@router.post("/sprites/{group}/{name}", status_code=status.HTTP_201_CREATED)
async def admin_upload_sprite(group: str, name: str, upload: SpriteUpload):
    """Saves (or replaces) assets/sprites/<group>/<name>/<name>_sheet.png and <name>.json"""
    if group not in SPRITE_GROUPS:
        raise invalid(f"Group must be one of: {', '.join(SPRITE_GROUPS)}")
    if not SHEET_NAME.match(name):
        raise invalid("The sheet name may only have lowercase letters, digits and _")
    try:
        png = base64.b64decode(upload.sheet_png_base64, validate=True)
    except (binascii.Error, ValueError):
        raise invalid("The PNG is not valid base64")
    if not png.startswith(b"\x89PNG"):
        raise invalid("The sheet must be a PNG file")
    data = dict(upload.sheet_json)
    missing = [key for key in ("frame_w", "frame_h", "anchor_x", "anchor_y", "clips") if key not in data]
    if missing:
        raise invalid(f"The JSON is missing: {', '.join(missing)}")
    data["src"] = f"sprites/{group}/{name}/{name}_sheet.png"
    folder = ASSETS_DIR / "sprites" / group / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}_sheet.png").write_bytes(png)
    (folder / f"{name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"group": group, "name": name, "json": data}
