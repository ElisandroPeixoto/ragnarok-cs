from pydantic import BaseModel
from typing import List
from npc_schema import NpcSchema
from monster_schema import MonsterSchema

class NavigationSchema(BaseModel):
    name: str
    image: str
    map_id: str


class MapSchemaSummary(BaseModel):
    id: str
    name: str


class MapSchemaResponse(BaseModel):
    id: str
    name: str
    level_range: str
    image: str
    about: str
    npcs: List[NpcSchema]
    monsters: List[MonsterSchema]
    navigation: List[NavigationSchema]