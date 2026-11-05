from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class MapModel(DBBaseModel):
    __tablename__ = "maps"

    id: str = Column(String, primary_key=True)
    name: str = Column(String(255), nullable=False)
    level_range: str = Column(String(30), nullable=False, default="-")
    image: str = Column(String, nullable=False, default="")
    about: str = Column(Text, nullable=False, default="")
    spawn_rate: int = Column(Integer, nullable=False, default=1)   # monsters per spawn wave in a hunt

    npcs = relationship("NpcModel", lazy="selectin")
    monster_spawns = relationship("MapMonsterModel", lazy="selectin")
    connections = relationship("MapConnectionModel", foreign_keys="MapConnectionModel.from_map_id", lazy="selectin")
