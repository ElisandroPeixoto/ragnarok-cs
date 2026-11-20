from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class MapModel(DBBaseModel):
    __tablename__ = "maps"

    id: str = Column(String, primary_key=True)
    name: str = Column(String(255), nullable=False)
    level_range: str = Column(String(30), nullable=False, default="-")
    background_image: str | None = Column(String, nullable=True)   # faded picture behind the map screen (assets/maps/backgrounds)
    town_image: str | None = Column(String, nullable=True)    # the town map with the place markers; None = empty square
    parent_map_id: str | None = Column(ForeignKey("maps.id"), nullable=True)   # set = this map is a building inside that map
    about: str = Column(Text, nullable=False, default="")
    zone: str = Column(String(30), nullable=False, default="safe")   # "safe", "hostile_passive" or "hostile_aggressive"

    parent_map = relationship("MapModel", remote_side=[id], lazy="selectin")
    npcs = relationship("NpcModel", lazy="selectin")
    places = relationship("MapPlaceModel", foreign_keys="MapPlaceModel.map_id", order_by="MapPlaceModel.slot",
                          lazy="selectin")
    monster_spawns = relationship("MapMonsterModel", lazy="selectin")
    connections = relationship("MapConnectionModel", foreign_keys="MapConnectionModel.from_map_id", lazy="selectin")
