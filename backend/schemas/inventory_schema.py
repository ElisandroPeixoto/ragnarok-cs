from typing import Optional
from pydantic import BaseModel


class ItemSchema(BaseModel):
    id: str
    name: str
    type: str
    description: str = ""
    drop_rate: float = 0.0
    icon: Optional[str] = None
    collection: Optional[str] = None

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
