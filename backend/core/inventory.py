"""Inventory operations that touch the database (the pure rules are in core/inventory_rules.py)"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.character_item_model import CharacterItemModel
from models.items_model import ItemModel
from core.inventory_rules import STACKABLE_TYPES, free_bag_slot


async def give_item(db: AsyncSession, character_id: int, item: ItemModel, amount: int) -> int:
    """Puts `amount` units of the item in the character's bag: stackable items join a pile the bag already has,
    everything else takes the first free slots. Returns how many units did not fit (bag full)"""
    entries = list((await db.execute(select(CharacterItemModel)
                                     .where(CharacterItemModel.character_id == character_id))).scalars().all())
    if item.type in STACKABLE_TYPES:
        pile = next((entry for entry in entries if entry.item_id == item.id and entry.slot.startswith("bag_")), None)
        if pile is not None:
            pile.amount += amount
            return 0
        slot = free_bag_slot({entry.slot for entry in entries})
        if slot is None:
            return amount
        db.add(CharacterItemModel(character_id=character_id, item_id=item.id, slot=slot, amount=amount))
        await db.flush()   # the next item given in this session must see this slot as taken
        return 0

    occupied = {entry.slot for entry in entries}
    for given in range(amount):
        slot = free_bag_slot(occupied)
        if slot is None:
            return amount - given
        occupied.add(slot)
        db.add(CharacterItemModel(character_id=character_id, item_id=item.id, slot=slot, amount=1))
    await db.flush()
    return 0
