from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class MonsterModel(DBBaseModel):
    __tablename__ = "monsters"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)
    image: str = Column(String, nullable=False)

    # Battle data; monsters without a sheet can't be hunted yet
    sheet: str | None = Column(String, nullable=True)
    max_hp: int = Column(Integer, nullable=False, default=50)
    max_ap: int = Column(Integer, nullable=False, default=2)
    ai: str = Column(String(50), nullable=False, default="passive")
    offset_x: int = Column(Integer, nullable=False, default=0)
    offset_y: int = Column(Integer, nullable=False, default=0)

    skill_links = relationship("MonsterSkillModel", order_by="MonsterSkillModel.slot", lazy="selectin")
