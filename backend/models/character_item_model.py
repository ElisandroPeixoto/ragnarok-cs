from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class CharacterItemModel(DBBaseModel):
    """An item a character carries and where it is: a bag slot ("bag_0".."bag_39") or an equipment slot
    ("head", "armor", "right_hand", ...), see core/inventory_rules.py"""
    __tablename__ = "character_items"
    __table_args__ = (UniqueConstraint("character_id", "slot"),)

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    character_id: int = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id: str = Column(String(64), ForeignKey("items.id"), nullable=False)
    slot: str = Column(String(30), nullable=False)
    amount: int = Column(Integer, nullable=False, default=1)

    item = relationship("ItemModel", lazy="selectin")
