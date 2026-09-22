from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class MapMonsterModel(DBBaseModel):
    __tablename__ = "map_monsters"

    map_id: str = Column(String, ForeignKey("maps.id"), primary_key=True)
    monster_id: int = Column(Integer, ForeignKey("monsters.id"), primary_key=True)
    spawn_rate: int = Column(Integer, nullable=False, default=0)

    monster = relationship("MonsterModel", lazy="selectin")
