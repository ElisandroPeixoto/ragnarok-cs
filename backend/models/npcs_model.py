from sqlalchemy import Column, Integer, String, ForeignKey
from core.config import DBBaseModel


class NpcModel(DBBaseModel):
    __tablename__ = "npcs"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    map_id: str = Column(String, ForeignKey("maps.id"), nullable=False)
    name: str = Column(String(255), nullable=False)
    image: str = Column(String, nullable=False, default="")
