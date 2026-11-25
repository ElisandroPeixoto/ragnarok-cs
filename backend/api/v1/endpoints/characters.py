from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.character_model import CharacterModel
from models.maps_model import MapModel
from models.character_item_model import CharacterItemModel
from core.inventory_rules import STARTER_ITEMS, bag_slot
from sqlalchemy import delete
from schemas.character_schema import CharacterSchemaCreate, CharacterSchemaResponse, CharacterSchemaPlaceUpdate, CharacterSchemaBattleResult, BattleResultResponse
from models.monsters_model import MonsterModel
from core.exp_rule import exp_gain, exp_after_death
from core.battle_rules import MIN_MONSTERS, MAX_MONSTERS
from core.level_progression import MAX_EXP, level_for_exp, total_exp_for_level, exp_progress
from core.deps import get_session
from typing import List


router = APIRouter()


# POST Character
"""Create a new character"""
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CharacterSchemaResponse)
async def post_character(character: CharacterSchemaCreate, db: AsyncSession = Depends(get_session)):
    new_character : CharacterModel = CharacterModel(
        name=character.name
    )

    db.add(new_character)
    await db.flush()
    for index, (item_id, amount) in enumerate(STARTER_ITEMS):
        db.add(CharacterItemModel(character_id=new_character.id, item_id=item_id, slot=bag_slot(index), amount=amount))
    await db.commit()
    await db.refresh(new_character)

    return new_character


# GET Character
"""Retrieve all the characters"""
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[CharacterSchemaResponse])
async def get_characters(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(CharacterModel)
        result = await session.execute(query)
        characters: List[CharacterModel] = result.scalars().unique().all()  # noqa

        return characters


# GET Character by ID
@router.get("/{character_id}", status_code=status.HTTP_200_OK, response_model=CharacterSchemaResponse)
async def get_character_by_id(character_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(CharacterModel).where(CharacterModel.id == character_id)  # noqa
        result = await session.execute(query)
        character: CharacterModel | None = result.scalars().unique().one_or_none()

        if character is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )

        return character


# DELETE Character
"""Delete a character by ID"""
@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: int, db: AsyncSession = Depends(get_session)):
    character = await db.get(CharacterModel, character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    await db.execute(delete(CharacterItemModel).where(CharacterItemModel.character_id == character_id))
    await db.delete(character)
    await db.commit()


# POST Character battle result
"""Settle a finished hunt (docs/regra-de-experiencia.md). Victory (every monster killed): the EXP of all the monsters
by level difference, plus level-ups (docs/progressao-de-level.md). Defeat: -20% of the EXP accumulated in the current
level and no EXP for the kills. Leaving a hunt is never reported: it costs nothing and pays nothing"""
@router.post("/{character_id}/battle-result", status_code=status.HTTP_200_OK, response_model=BattleResultResponse)
async def post_battle_result(character_id: int, result: CharacterSchemaBattleResult,
                             db: AsyncSession = Depends(get_session)):
    character = await db.get(CharacterModel, character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    gained = 0
    if result.victory:
        if not MIN_MONSTERS <= len(result.kills) <= MAX_MONSTERS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"A hunt has {MIN_MONSTERS} to {MAX_MONSTERS} monsters")
        monsters = {}
        for name in set(result.kills):
            monster = (await db.execute(select(MonsterModel).where(MonsterModel.name == name))).scalar_one_or_none()
            if monster is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Monster '{name}' not found")
            monsters[name] = monster
        gained = sum(exp_gain(character.level, monsters[name].level, monsters[name].base_exp) for name in result.kills)
    total = min(character.exp + gained, MAX_EXP)
    level = level_for_exp(total)
    lost = 0
    if not result.victory:   # only the progress inside the level is penalized: the level never drops
        progress = exp_progress(level, total)
        lost = progress - exp_after_death(progress)
    character.exp = total - lost
    character.level = level
    await db.commit()
    await db.refresh(character)

    return {"character": character, "exp_gained": gained, "exp_lost": lost}


# PATCH Character place
"""Register that the character moved to another map (updates current_map / current_map_id)"""
@router.patch("/{character_id}/place", status_code=status.HTTP_200_OK, response_model=CharacterSchemaResponse)
async def patch_character_place(character_id: int, place: CharacterSchemaPlaceUpdate,
                                db: AsyncSession = Depends(get_session)):
    character = await db.get(CharacterModel, character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    game_map = await db.get(MapModel, place.map_id)
    if game_map is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

    character.current_map = game_map.name
    character.current_map_id = game_map.id
    await db.commit()
    await db.refresh(character)

    return character
