from sqlalchemy import Column, String
from core.config import DBBaseModel


class ItemModel(DBBaseModel):
    """An item of the game (catalogue). What a character carries lives in CharacterItemModel"""
    __tablename__ = "items"

    id: str = Column(String(64), primary_key=True)
    name: str = Column(String(255), nullable=False)
    kind: str = Column(String(30), nullable=False, default="etc")          # equipment / usable / etc
    equip_type: str | None = Column(String(30), nullable=True)             # head/armor/weapon/shield/garment/shoes/accessory
    icon: str | None = Column(String, nullable=True)                       # path under assets/; NULL = generic icon
    description: str = Column(String, nullable=False, default="")
