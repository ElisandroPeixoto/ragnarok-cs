import asyncio
from sqlalchemy.future import select
from core.config import DBBaseModel
from core.database import engine, Session
from models.maps_model import MapModel
from models.npcs_model import NpcModel
from models.monsters_model import MonsterModel
from models.map_monster_model import MapMonsterModel
from models.map_connection_model import MapConnectionModel


"""
THIS FILE IS ONLY TO INSERT NEW DATA ON THE DATABASE, STILL THERE IS NO ADMIN INTERFACE
"""


MAPS = {
    "novice_academy": {
        "name": "Novice Academy", "level_range": "1 - 10",
        "image": "maps/novice_academy.jpg", "about": "Lorem ipsum dolor sit amet...",
        "npcs": [("Hostess", "npcs/hostess.gif"), ("Sailor", "npcs/sailor.gif")],
        "monsters": [],
        "navigation": ["training_field_1"],
    },
    "training_field_1": {
        "name": "Training Field 1", "level_range": "5 - 15",
        "image": "maps/training_field_1.jpg", "about": "...",
        "npcs": [("Trainer", "npcs/trainer.gif")],
        "monsters": [("Poring", 40), ("Lunatic", 40), ("Wilow", 20)],
        "navigation": ["novice_academy"],
    },
}

MONSTER_IMAGES = {
    "Poring": "monsters/poring.gif",
    "Lunatic": "monsters/lunatic.gif",
    "Wilow": "monsters/wilow.gif",
}


async def seed() -> None:
    import models.__all_models
    async with engine.begin() as conn:
        await conn.run_sync(DBBaseModel.metadata.create_all)

    async with Session() as db:
        # 1) maps, npcs, monsters
        for map_id, data in MAPS.items():
            if await db.get(MapModel, map_id):
                continue
            db.add(MapModel(id=map_id, name=data["name"], level_range=data["level_range"],
                            image=data["image"], about=data["about"]))
            for name, image in data["npcs"]:
                db.add(NpcModel(map_id=map_id, name=name, image=image))
            for name, rate in data["monsters"]:
                result = await db.execute(select(MonsterModel).where(MonsterModel.name == name))
                monster = result.scalar_one_or_none()
                if monster is None:
                    monster = MonsterModel(name=name, image=MONSTER_IMAGES[name])
                    db.add(monster)
                    await db.flush()
                db.add(MapMonsterModel(map_id=map_id, monster_id=monster.id, spawn_rate=rate))
        await db.flush()

        # 2) connections (after all maps exist)
        for map_id, data in MAPS.items():
            for target in data["navigation"]:
                if await db.get(MapConnectionModel, (map_id, target)) is None:
                    db.add(MapConnectionModel(from_map_id=map_id, to_map_id=target))

        await db.commit()
    print("Maps seeded.")


if __name__ == "__main__":
    asyncio.run(seed())