from sqlalchemy import Column, Integer, String
from core.config import DBBaseModel


class MonsterModel(DBBaseModel):
    __tablename__ = "monsters"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)
    image: str = Column(String, nullable=False)