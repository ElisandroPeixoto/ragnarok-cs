from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.character_model import CharacterModel
from models.jobs_model import JobModel
from models.map_monster_model import MapMonsterModel
from models.monsters_model import MonsterModel
from schemas.battle_schema import BattleSchemaCreate, BattleSchemaResponse
from core.deps import get_session

router = APIRouter()


def skill_to_dict(skill) -> dict:
    return {"ap_cost": skill.ap_cost, "damage": skill.damage, "range": skill.range, "icon": skill.icon}


def hero_unit(character: CharacterModel, job: JobModel) -> dict:
    return {
        "name": character.name, "job": job.name, "team": "player",
        "sheet": job.sheet, "avatar": job.avatar,
        "offset_x": job.offset_x, "offset_y": job.offset_y,
        "hp": character.hp, "max_hp": character.max_hp,
        "ap": job.max_ap, "max_ap": job.max_ap,
        "skills": [link.skill.name for link in job.skill_links],
    }


def monster_unit(monster: MonsterModel) -> dict:
    return {
        "name": monster.name, "team": "enemy",
        "sheet": monster.sheet, "ai": monster.ai,
        "offset_x": monster.offset_x, "offset_y": monster.offset_y,
        "hp": monster.max_hp, "max_hp": monster.max_hp,
        "ap": monster.max_ap, "max_ap": monster.max_ap,
        "skills": [link.skill.name for link in monster.skill_links],
    }


"""Start a hunt: the character against every monster spawned on the map (monster_1, monster_2, ...)"""
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BattleSchemaResponse)
async def start_battle(battle: BattleSchemaCreate, db: AsyncSession = Depends(get_session)):
    character = await db.get(CharacterModel, battle.character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    job = await db.get(JobModel, character.job)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{character.job}' not found")

    result = await db.execute(select(MapMonsterModel).where(MapMonsterModel.map_id == battle.map_id)
                              .order_by(MapMonsterModel.monster_id))
    monsters = [spawn.monster for spawn in result.scalars().all()]
    if not monsters:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No monsters to hunt on this map")

    units = {"hero": hero_unit(character, job)}   # the hero comes first: it plays first
    units.update({f"monster_{index}": monster_unit(monster) for index, monster in enumerate(monsters, start=1)})
    skills = {link.skill.name: skill_to_dict(link.skill)
              for owner in (job, *monsters) for link in owner.skill_links}
    return {"units": units, "skills": skills}
