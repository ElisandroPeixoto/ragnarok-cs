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
from models.skills_model import SkillModel
from models.jobs_model import JobModel
from models.job_skill_model import JobSkillModel
from models.monster_skill_model import MonsterSkillModel


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

# Monsters without "sheet" only show up on maps; they can't be hunted until they get battle data
MONSTERS = {
    "Poring": {
        "image": "monsters/poring.gif",
        "sheet": "poring", "max_hp": 50, "max_ap": 2, "ai": "approach_and_attack",
        "offset_x": 0, "offset_y": 0,
        "skills": ["Basic Attack"],
    },
    "Lunatic": {"image": "monsters/lunatic.gif"},
    "Wilow": {"image": "monsters/wilow.gif"},
}

MAPS = {
    "novice_academy": {
        "name": "Novice Academy", "level_range": "1 - 10",
        "image": "maps/novice_academy.jpg", "about": "Lorem ipsum dolor sit amet...",
        "npcs": [("Hostess", "npcs/hostess.gif"), ("Sailor", "npcs/sailor.gif")],
        "monsters": [],
        "navigation": ["training_field_1"],
    },
    "training_field_1": {
        "name": "Training Field 1", "level_range": "1 - 10",
        "image": "maps/training_field_1.jpg", "about": "...",
        "npcs": [("Trainer", "npcs/trainer.gif")],
        "monsters": [("Poring", 40), ("Lunatic", 40), ("Wilow", 20)],
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

        # 2) jobs (a lista de skills é sempre regravada)
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

        # 4) maps, npcs, monster spawns
        for map_id, data in MAPS.items():
            existing = await db.get(MapModel, map_id)
            if existing:  # mapa já existe: só atualiza os dados básicos (NPCs/monstros não são duplicados)
                existing.name, existing.level_range = data["name"], data["level_range"]
                existing.image, existing.about = data["image"], data["about"]
                continue
            db.add(MapModel(id=map_id, name=data["name"], level_range=data["level_range"],
                            image=data["image"], about=data["about"]))
            for name, image in data["npcs"]:
                db.add(NpcModel(map_id=map_id, name=name, image=image))
            for name, rate in data["monsters"]:
                db.add(MapMonsterModel(map_id=map_id, monster_id=monster_ids[name], spawn_rate=rate))
        await db.flush()

        # 5) connections (after all maps exist)
        for map_id, data in MAPS.items():
            for target in data["navigation"]:
                if await db.get(MapConnectionModel, (map_id, target)) is None:
                    db.add(MapConnectionModel(from_map_id=map_id, to_map_id=target))

        await db.commit()
    print("Skills, jobs, monsters and maps seeded.")


if __name__ == "__main__":
    asyncio.run(seed())
