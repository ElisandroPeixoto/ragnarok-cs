from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class JobModel(DBBaseModel):
    """Battle data shared by every character of a job (name is what CharacterModel.job stores)"""
    __tablename__ = "jobs"

    name: str = Column(String(255), primary_key=True)
    sheet: str = Column(String, nullable=False)       # assets/sprites/<sheet>/
    avatar: str = Column(String, nullable=False, default="")
    max_ap: int = Column(Integer, nullable=False, default=5)
    offset_x: int = Column(Integer, nullable=False, default=0)
    offset_y: int = Column(Integer, nullable=False, default=0)

    skill_links = relationship("JobSkillModel", order_by="JobSkillModel.slot", lazy="selectin")
