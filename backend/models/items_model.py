from sqlalchemy import Column, String, Float
from core.config import DBBaseModel


class ItemModel(DBBaseModel):
    """An item of the game (catalogue). What a character carries lives in CharacterItemModel, and which monsters
    drop it in MonsterDropModel"""
    __tablename__ = "items"

    id: str = Column(String(64), primary_key=True)
    name: str = Column(String(255), nullable=False)
    type: str = Column(String(30), nullable=False, default="Misc")     # Misc for now; later Helmet, Armor, Sword...
    description: str = Column(String, nullable=False, default="")
    drop_rate: float = Column(Float, nullable=False, default=0.0)        # chance in percent (70 = 70%)
    icon: str | None = Column(String, nullable=True)                     # inventory icon, path under assets/
    collection: str | None = Column(String, nullable=True)               # picture of the details pop up
