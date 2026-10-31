from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class JobSkillModel(DBBaseModel):
    __tablename__ = "job_skills"

    job_name: str = Column(String, ForeignKey("jobs.name"), primary_key=True)
    skill_id: int = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    slot: int = Column(Integer, nullable=False, default=0)  # order in the skills bar

    skill = relationship("SkillModel", lazy="selectin")
