from sqlalchemy import Column, Integer, String, ForeignKey
from core.config import DBBaseModel


class MonsterDropModel(DBBaseModel):
    """An item a monster can drop when killed; the chance is the item's drop_rate"""
    __tablename__ = "monster_drops"

    monster_id: int = Column(Integer, ForeignKey("monsters.id"), primary_key=True)
    item_id: str = Column(String(64), ForeignKey("items.id"), primary_key=True)
