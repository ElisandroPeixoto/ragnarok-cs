from pydantic import BaseModel
from typing import List, Optional
from schemas.npc_schema import NpcSchema
from schemas.monster_schema import MonsterSchema

class NavigationSchema(BaseModel):
    name: str
    image: str
    map_id: str
    level_range: str


class PlaceTargetSchema(BaseModel):
    map_id: str
    name: str
    level_range: str
    zone: str


class PlaceSchema(BaseModel):
    id: int
    name: str
    kind: str
    icon: str
    x: float
    y: float
    direction: Optional[str] = None
    target: Optional[PlaceTargetSchema] = None


class MapSchemaSummary(BaseModel):
    id: str
    name: str


class MapSchemaResponse(BaseModel):
    id: str
    name: str
    level_range: str
    image: str
    about: str
    zone: str
    places: List[PlaceSchema]
    npcs: List[NpcSchema]
    monsters: List[MonsterSchema]
    navigation: List[NavigationSchema]