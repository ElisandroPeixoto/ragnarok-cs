from sqlalchemy import Column, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class MapModel(DBBaseModel):
    __tablename__ = "maps"

    id: str = Column(String, primary_key=True)
    name: str = Column(String(255), nullable=False)
    level_range: str = Column(String(30), nullable=False, default="-")
    image: str = Column(String, nullable=False, default="")   # the location's art (banner on top of the map screen)
    art_position_y: float = Column(Float, nullable=False, default=0.5)   # where the banner crops the cover: 0 top, 0.5 center, 1 bottom
    town_image: str | None = Column(String, nullable=True)    # the town map with the place markers; None = empty square
    about: str = Column(Text, nullable=False, default="")
    zone: str = Column(String(30), nullable=False, default="safe")   # "safe", "hostile_passive" or "hostile_aggressive"

    npcs = relationship("NpcModel", lazy="selectin")
    places = relationship("MapPlaceModel", foreign_keys="MapPlaceModel.map_id", order_by="MapPlaceModel.slot",
                          lazy="selectin")
    monster_spawns = relationship("MapMonsterModel", lazy="selectin")
    connections = relationship("MapConnectionModel", foreign_keys="MapConnectionModel.from_map_id", lazy="selectin")
