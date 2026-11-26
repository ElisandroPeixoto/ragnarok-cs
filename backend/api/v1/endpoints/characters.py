from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.character_model import CharacterModel
from models.maps_model import MapModel
from models.character_item_model import CharacterItemModel
from models.items_model import ItemModel
from models.monster_drop_model import MonsterDropModel
from core.drop_rules import roll_drops
from core.inventory import give_item
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
level and no EXP for the kills. Leaving a hunt is never reported: it costs nothing and pays nothing.
Victory also rolls the drops of every monster killed (core/drop_rules.py) and puts them in the bag"""
@router.post("/{character_id}/battle-result", status_code=status.HTTP_200_OK, response_model=BattleResultResponse)
async def post_battle_result(character_id: int, result: CharacterSchemaBattleResult,
                             db: AsyncSession = Depends(get_session)):
    character = await db.get(CharacterModel, character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    gained = 0
    drops, drops_lost = [], []
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
        drops, drops_lost = await drop_items(db, character.id, [monsters[name] for name in result.kills])
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

    return {"character": character, "exp_gained": gained, "exp_lost": lost, "drops": drops, "drops_lost": drops_lost}


async def drop_items(db: AsyncSession, character_id: int, killed: list[MonsterModel]) -> tuple[list, list]:
    """Rolls the drops of the monsters killed and gives them to the character. Returns (dropped, did not fit)"""
    rows = (await db.execute(select(MonsterDropModel.monster_id, ItemModel)
                             .join(ItemModel, ItemModel.id == MonsterDropModel.item_id)
                             .where(MonsterDropModel.monster_id.in_({monster.id for monster in killed})))).all()
    tables: dict[int, list[tuple[str, float]]] = {}
    items = {}
    for monster_id, item in rows:
        tables.setdefault(monster_id, []).append((item.id, item.drop_rate))
        items[item.id] = item
    dropped = roll_drops([tables.get(monster.id, []) for monster in killed])
    drops, drops_lost = [], []
    for item_id, amount in dropped.items():
        item = items[item_id]
        left_out = await give_item(db, character_id, item, amount)
        if amount - left_out:
            drops.append({"item_id": item.id, "name": item.name, "icon": item.icon, "amount": amount - left_out})
        if left_out:
            drops_lost.append({"item_id": item.id, "name": item.name, "icon": item.icon, "amount": left_out})
    return drops, drops_lost


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
