from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class MapConnectionModel(DBBaseModel):
    __tablename__ = "map_connections"

    from_map_id: str = Column(String, ForeignKey("maps.id"), primary_key=True)
    to_map_id: str = Column(String, ForeignKey("maps.id"), primary_key=True)

    to_map = relationship("MapModel", foreign_keys="MapConnectionModel.to_map_id", lazy="selectin")
