from sqlalchemy import Column, Integer, String, Text, ForeignKey
from core.config import DBBaseModel


class NpcModel(DBBaseModel):
    __tablename__ = "npcs"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    map_id: str = Column(String, ForeignKey("maps.id"), nullable=False)
    name: str = Column(String(255), nullable=False)
    image: str = Column(String, nullable=False, default="")
    place_id: int | None = Column(Integer, ForeignKey("map_places.id"), nullable=True)   # area of the map it stands in
    greeting: str = Column(Text, nullable=False, default="")   # base line shown on the NPC's card
