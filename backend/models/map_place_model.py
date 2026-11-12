from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.config import DBBaseModel


class MapPlaceModel(DBBaseModel):
    """A point of interest drawn as a marker over the map image.

    kind: "area" (has NPCs; shown as a tab under "In the area"), "building" (a place to enter, link comes later)
    or "exit" (a route to another map, `target_map_id`). x/y are the marker's center as a fraction (0-1) of
    the image's width/height."""
    __tablename__ = "map_places"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    map_id: str = Column(String, ForeignKey("maps.id"), nullable=False)
    name: str = Column(String(255), nullable=False)
    kind: str = Column(String(20), nullable=False, default="area")
    icon: str = Column(String(50), nullable=False, default="")   # icon key; the frontend maps it to an image/icon
    x: float = Column(Float, nullable=False, default=0.5)
    y: float = Column(Float, nullable=False, default=0.5)
    slot: int = Column(Integer, nullable=False, default=0)        # display order
    direction: str | None = Column(String(30), nullable=True)     # exits: compass direction, e.g. "Northwest"
    target_map_id: str | None = Column(String, ForeignKey("maps.id"), nullable=True)

    target_map = relationship("MapModel", foreign_keys="MapPlaceModel.target_map_id", lazy="selectin")
