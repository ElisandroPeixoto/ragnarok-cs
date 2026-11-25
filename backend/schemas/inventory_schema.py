from typing import Optional
from pydantic import BaseModel


class ItemSchema(BaseModel):
    id: str
    name: str
    kind: str
    equip_type: Optional[str] = None
    icon: Optional[str] = None
    description: str = ""

    class Config:
        from_attributes = True


class InventoryEntrySchema(BaseModel):
    id: int
    slot: str
    amount: int
    item: ItemSchema

    class Config:
        from_attributes = True


class InventoryMoveSchema(BaseModel):
    """Drag of the item in `from_slot` onto `to_slot`; an item already there swaps places with it"""
    from_slot: str
    to_slot: str
