from sqlalchemy import Column, Integer, String
from core.config import DBBaseModel


class SkillModel(DBBaseModel):
    __tablename__ = "skills"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)
    ap_cost: int = Column(Integer, nullable=False, default=1)
    damage: int = Column(Integer, nullable=False, default=0)
    range: int = Column(Integer, nullable=False, default=1)
    icon: str = Column(String, nullable=False, default="")
