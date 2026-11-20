import asyncio
from sqlalchemy import delete
from sqlalchemy.future import select
from core.config import DBBaseModel
from core.database import engine, Session
from models.maps_model import MapModel
from models.npcs_model import NpcModel
from models.monsters_model import MonsterModel
from models.map_monster_model import MapMonsterModel
from models.map_connection_model import MapConnectionModel
from models.map_place_model import MapPlaceModel
from models.skills_model import SkillModel
from models.jobs_model import JobModel
from models.job_skill_model import JobSkillModel
from models.monster_skill_model import MonsterSkillModel
from models.character_model import CharacterModel
from core.level_progression import MAX_EXP, level_for_exp


"""
THIS FILE IS ONLY TO INSERT NEW DATA ON THE DATABASE, STILL THERE IS NO ADMIN INTERFACE
"""


SKILLS = {
    "Basic Attack": {"ap_cost": 1, "damage": 10, "range": 1, "icon": "skills/Basic Attack.png"},
}

JOBS = {
    "Novice": {
        "sheet": "novice", "avatar": "characters_badges/0_novice_badge.png",
        "max_ap": 5, "offset_x": 0, "offset_y": 0,
        "skills": ["Basic Attack"],
    },
}

# "sheet" is the folder in assets/sprites: used in battle and as the monster's picture on maps
MONSTERS = {
    "Poring": {
        "sheet": "poring", "level": 1, "base_exp": 6, "max_hp": 50, "max_ap": 2, "ai": "approach_and_attack",
        "offset_x": 0, "offset_y": 0,
        "skills": ["Basic Attack"],
    },
    "Lunatic": {
        "sheet": "lunatic", "level": 1, "base_exp": 8, "max_hp": 50, "max_ap": 2, "ai": "approach_and_attack",
        "offset_x": 0, "offset_y": 0,
        "skills": ["Basic Attack"],
    },
    "Wilow": {
        "sheet": "wilow", "level": 1, "base_exp": 10, "max_hp": 50, "max_ap": 2, "ai": "approach_and_attack",
        "offset_x": 0, "offset_y": 0,
        "skills": ["Basic Attack"],
    },
}

# zone: "safe", "hostile_passive" or "hostile_aggressive" (only "safe" shows a label, "Safe Zone", on the map header and on routes to the map)
# town_image: the town map the markers are drawn over (assets/maps; None = an empty square)
# background_image: the faded picture behind the map screen (assets/maps/backgrounds)
# places: markers over the town map, in display order. x/y = marker center as a fraction of the town image size.
#   kind "area" holds NPCs, "building" is a place to enter (link comes later), "exit" leads to the "target"
#   map in "direction" (keep that map in "navigation" too). "icon" is a key the frontend turns into an icon
# npcs: (name, image, area name, greeting); the area must be a place of kind "area" with a unique name
MAPS = {
    "novice_academy": {
        "name": "Novice Academy", "level_range": "1 - 10", "zone": "safe",
        "about": "Lorem ipsum dolor sit amet...",
        "town_image": "maps/novice_academy.jpg",   # provisional town map
        "background_image": "maps/backgrounds/forest.jpg",
        "places": [
            {"name": "Main Square", "kind": "area", "icon": "square", "x": 0.55, "y": 0.595},
            {"name": "Port", "kind": "area", "icon": "port", "x": 0.26, "y": 0.775},
            {"name": "House", "kind": "area", "icon": "house", "x": 0.25, "y": 0.395},
            {"name": "House", "kind": "area", "icon": "house", "x": 0.59, "y": 0.711},
            {"name": "Academy", "kind": "exit", "icon": "building", "x": 0.56, "y": 0.45,
             "target": "academy", "direction": "Building"},
            {"name": "Training Camp", "kind": "exit", "icon": "exit", "x": 0.36, "y": 0.115,
             "target": "training_field_1", "direction": "Northwest"},
        ],
        "npcs": [
            ("Hostess", "npcs/hostess.gif", "Main Square", "Welcome Adventurer! Here is the beginning of a great journey."),
            ("Sailor", "npcs/sailor.gif", "Port", "Let's go somewhere?"),
        ],
        "monsters": [],
        "navigation": ["training_field_1", "academy"],
    },
    "training_field_1": {
        "name": "Training Field 1", "level_range": "1 - 10", "zone": "hostile_passive",
        "about": "...",
        "town_image": "maps/training_field_1.jpg",
        "background_image": "maps/backgrounds/forest.jpg",
        "places": [
            {"name": "Training Grounds", "kind": "area", "icon": "training", "x": 0.45, "y": 0.36},
            {"name": "Novice Academy", "kind": "exit", "icon": "exit", "x": 0.47, "y": 0.92,
             "target": "novice_academy", "direction": "Southeast"},
            # no map behind it yet: shows up in Routes without a link
            {"name": "Training Field 2", "kind": "exit", "icon": "exit", "x": 0.875, "y": 0.21,
             "direction": "Northeast"},
        ],
        "npcs": [
            ("Trainer", "npcs/trainer.gif", "Training Grounds", "Ready to train? Monsters roam these woods."),
        ],
        "monsters": [("Poring", 40), ("Lunatic", 40), ("Wilow", 20)],
        "navigation": ["novice_academy"],
    },
    "academy": {   # inside the Academy building: only the picture for now (no places, NPCs or monsters yet)
        "name": "Academy", "level_range": "1 - 10", "zone": "safe",
        "about": "...",
        "town_image": "maps/academy.jpg",
        "background_image": "maps/backgrounds/forest.jpg",
        "places": [],
        "npcs": [],
        "monsters": [],
        "navigation": ["novice_academy"],
    },
}


def upsert(instance, values: dict) -> None:
    for field, value in values.items():
        setattr(instance, field, value)


async def seed() -> None:
    import models.__all_models
    async with engine.begin() as conn:
        await conn.run_sync(DBBaseModel.metadata.create_all)
        # monsters used to store a GIF in "image"; drop it from older databases (keeps characters)
        columns = [row[1] for row in (await conn.exec_driver_sql("PRAGMA table_info(monsters)")).fetchall()]
        if "image" in columns:
            await conn.exec_driver_sql("ALTER TABLE monsters DROP COLUMN image")
        if "level" not in columns:
            await conn.exec_driver_sql("ALTER TABLE monsters ADD COLUMN level INTEGER NOT NULL DEFAULT 1")
        if "base_exp" not in columns:
            await conn.exec_driver_sql("ALTER TABLE monsters ADD COLUMN base_exp INTEGER NOT NULL DEFAULT 0")
        # maps gained "town_image" (the town map under the location's art)
        if "town_image" not in [row[1] for row in (await conn.exec_driver_sql("PRAGMA table_info(maps)")).fetchall()]:
            await conn.exec_driver_sql("ALTER TABLE maps ADD COLUMN town_image VARCHAR")
        # maps gained "background_image" (the picture behind the map screen)
        if "background_image" not in [row[1] for row in (await conn.exec_driver_sql("PRAGMA table_info(maps)")).fetchall()]:
            await conn.exec_driver_sql("ALTER TABLE maps ADD COLUMN background_image VARCHAR")
        # the map screen has no cover art any more: drop its columns from older databases
        for old_column in ("art_position_y", "image"):
            if old_column in [row[1] for row in (await conn.exec_driver_sql("PRAGMA table_info(maps)")).fetchall()]:
                await conn.exec_driver_sql(f"ALTER TABLE maps DROP COLUMN {old_column}")
        # the number of monsters of a hunt is now rolled for every hunt (core/battle_rules.py): drop the per-map column
        map_columns = [row[1] for row in (await conn.exec_driver_sql("PRAGMA table_info(maps)")).fetchall()]
        if "spawn_rate" in map_columns:
            await conn.exec_driver_sql("ALTER TABLE maps DROP COLUMN spawn_rate")
        # maps gained "zone"; npcs gained their area ("place_id") and a "greeting"
        if "zone" not in map_columns:
            await conn.exec_driver_sql("ALTER TABLE maps ADD COLUMN zone VARCHAR(30) NOT NULL DEFAULT 'safe'")
        npc_columns = [row[1] for row in (await conn.exec_driver_sql("PRAGMA table_info(npcs)")).fetchall()]
        if "place_id" not in npc_columns:
            await conn.exec_driver_sql("ALTER TABLE npcs ADD COLUMN place_id INTEGER REFERENCES map_places(id)")
        if "greeting" not in npc_columns:
            await conn.exec_driver_sql("ALTER TABLE npcs ADD COLUMN greeting TEXT NOT NULL DEFAULT ''")

    async with Session() as db:
        # 1) skills
        skill_ids = {}
        for name, data in SKILLS.items():
            skill = (await db.execute(select(SkillModel).where(SkillModel.name == name))).scalar_one_or_none()
            if skill is None:
                skill = SkillModel(name=name)
                db.add(skill)
            upsert(skill, data)
            await db.flush()
            skill_ids[name] = skill.id

        # 2) jobs (the skill list is always rewritten)
        for name, data in JOBS.items():
            data = dict(data)
            skills = data.pop("skills")
            job = await db.get(JobModel, name)
            if job is None:
                job = JobModel(name=name)
                db.add(job)
            upsert(job, data)
            await db.execute(delete(JobSkillModel).where(JobSkillModel.job_name == name))
            for slot, skill_name in enumerate(skills):
                db.add(JobSkillModel(job_name=name, skill_id=skill_ids[skill_name], slot=slot))
        await db.flush()

        # 3) monsters
        monster_ids = {}
        for name, data in MONSTERS.items():
            data = dict(data)
            skills = data.pop("skills", [])
            monster = (await db.execute(select(MonsterModel).where(MonsterModel.name == name))).scalar_one_or_none()
            if monster is None:
                monster = MonsterModel(name=name)
                db.add(monster)
            upsert(monster, data)
            await db.flush()
            monster_ids[name] = monster.id
            await db.execute(delete(MonsterSkillModel).where(MonsterSkillModel.monster_id == monster.id))
            for slot, skill_name in enumerate(skills):
                db.add(MonsterSkillModel(monster_id=monster.id, skill_id=skill_ids[skill_name], slot=slot))
        await db.flush()

        # 4) maps and monster spawns
        for map_id, data in MAPS.items():
            values = {"name": data["name"], "level_range": data["level_range"], "about": data["about"],
                      "zone": data.get("zone", "safe"), "town_image": data.get("town_image"),
                      "background_image": data.get("background_image")}
            existing = await db.get(MapModel, map_id)
            if existing:  # map already exists: only update its basic data (monster spawns are not duplicated)
                upsert(existing, values)
                continue
            db.add(MapModel(id=map_id, **values))
            for name, rate in data["monsters"]:
                db.add(MapMonsterModel(map_id=map_id, monster_id=monster_ids[name], spawn_rate=rate))
        await db.flush()

        # 5) places and npcs, always rewritten (after all maps exist: exits point to other maps)
        for map_id, data in MAPS.items():
            await db.execute(delete(NpcModel).where(NpcModel.map_id == map_id))
            await db.execute(delete(MapPlaceModel).where(MapPlaceModel.map_id == map_id))
            area_ids = {}
            for slot, place in enumerate(data.get("places", [])):
                row = MapPlaceModel(map_id=map_id, name=place["name"], kind=place["kind"], icon=place["icon"],
                                    x=place["x"], y=place["y"], slot=slot, direction=place.get("direction"),
                                    target_map_id=place.get("target"))
                db.add(row)
                await db.flush()
                if place["kind"] == "area":
                    area_ids.setdefault(place["name"], row.id)
            for name, image, area, greeting in data["npcs"]:
                db.add(NpcModel(map_id=map_id, name=name, image=image, place_id=area_ids[area], greeting=greeting))
        await db.flush()

        # 6) connections (after all maps exist)
        for map_id, data in MAPS.items():
            for target in data["navigation"]:
                if await db.get(MapConnectionModel, (map_id, target)) is None:
                    db.add(MapConnectionModel(from_map_id=map_id, to_map_id=target))

        # 7) characters: their level follows their total EXP (the level table may have changed)
        for character in (await db.execute(select(CharacterModel))).scalars().all():
            character.exp = min(character.exp, MAX_EXP)
            character.level = level_for_exp(character.exp)

        await db.commit()
    print("Skills, jobs, monsters and maps seeded.")


if __name__ == "__main__":
    asyncio.run(seed())
