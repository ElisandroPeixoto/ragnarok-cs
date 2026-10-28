from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class MonsterSkillModel(DBBaseModel):
    __tablename__ = "monster_skills"

    monster_id: int = Column(Integer, ForeignKey("monsters.id"), primary_key=True)
    skill_id: int = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    slot: int = Column(Integer, nullable=False, default=0)  # slot 0 = the AI's main skill

    skill = relationship("SkillModel", lazy="selectin")
