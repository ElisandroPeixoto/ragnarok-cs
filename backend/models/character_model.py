from core.config import DBBaseModel
from sqlalchemy import Column, Integer, String, ForeignKey


class CharacterModel(DBBaseModel):
    """Database model for characters"""
    __tablename__ = "characters"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False)
    job: str = Column(String(255), ForeignKey("jobs.name"), nullable=False, default="Novice")
    level: int = Column(Integer, nullable=False, default=1)
    exp: int = Column(Integer, nullable=False, default=0)
    hp: int = Column(Integer, nullable=False, default=50)
    current_map: str = Column(String, default="Novice Island", nullable=False)
    current_map_id: str = Column(String, default="novice_academy", nullable=False)
    zeny: int = Column(Integer, nullable=False, default=0)   # whole zeny, no decimals
    max_hp: int = Column(Integer, nullable=False, default=50)
    max_sp: int = Column(Integer, nullable=False, default=10)
