from core.config import DBBaseModel
from sqlalchemy import Column, Integer, String, Numeric
from decimal import Decimal


class CharacterModel(DBBaseModel):
    """Database model for characters"""
    __tablename__ = "characters"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False)
    job: str = Column(String(255), nullable=False, default="Novice")
    level: int = Column(Integer, nullable=False, default=1)
    exp: int = Column(Integer, nullable=False, default=0)
    hp: int = Column(Integer, nullable=False, default=50)
    sp: int = Column(Integer, nullable=False, default=10)
    current_map: str = Column(String, default="Novice Academy", nullable=False)
    zeny: int = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    max_hp: int = Column(Integer, nullable=False, default=50)
    max_sp: int = Column(Integer, nullable=False, default=10)
