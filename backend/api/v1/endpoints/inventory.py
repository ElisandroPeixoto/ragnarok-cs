from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.character_model import CharacterModel
from models.character_item_model import CharacterItemModel
from schemas.inventory_schema import InventoryEntrySchema, InventoryMoveSchema
from core.inventory_rules import is_valid_slot, can_hold
from core.deps import get_session
from typing import List


router = APIRouter()


async def load_inventory(db: AsyncSession, character_id: int) -> list[CharacterItemModel]:
    if await db.get(CharacterModel, character_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    query = select(CharacterItemModel).where(CharacterItemModel.character_id == character_id)  # noqa
    return list((await db.execute(query)).scalars().all())


# GET Character inventory
"""Every item the character carries, bag and equipment, each with its slot"""
@router.get("/{character_id}/inventory", status_code=status.HTTP_200_OK, response_model=List[InventoryEntrySchema])
async def get_inventory(character_id: int, db: AsyncSession = Depends(get_session)):
    return await load_inventory(db, character_id)


# POST Character inventory move
"""Moves the item in from_slot to to_slot (bag <-> bag, bag <-> equipment). If to_slot holds an item, the two swap.
Equipment slots only take items of a matching equip type, in both directions of a swap"""
@router.post("/{character_id}/inventory/move", status_code=status.HTTP_200_OK, response_model=List[InventoryEntrySchema])
async def move_item(character_id: int, move: InventoryMoveSchema, db: AsyncSession = Depends(get_session)):
    entries = await load_inventory(db, character_id)
    if not (is_valid_slot(move.from_slot) and is_valid_slot(move.to_slot)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid slot")
    by_slot = {entry.slot: entry for entry in entries}
    moving = by_slot.get(move.from_slot)
    if moving is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No item in that slot")
    if move.from_slot == move.to_slot:
        return entries
    other = by_slot.get(move.to_slot)
    if not can_hold(move.to_slot, moving.item.equip_type) or \
            (other is not None and not can_hold(move.from_slot, other.item.equip_type)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Item does not fit that slot")

    if other is None:
        moving.slot = move.to_slot
    else:   # swap through a free name: (character_id, slot) is unique
        other.slot = "_swap"
        await db.flush()
        moving.slot = move.to_slot
        await db.flush()
        other.slot = move.from_slot
    await db.commit()
    return await load_inventory(db, character_id)
