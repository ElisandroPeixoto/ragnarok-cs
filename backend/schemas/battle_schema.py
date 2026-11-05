from pydantic import BaseModel
from typing import Dict, List


class BattleSchemaCreate(BaseModel):
    character_id: int
    map_id: str


class SkillSchema(BaseModel):
    ap_cost: int
    damage: int
    range: int
    icon: str


class UnitSchema(BaseModel):
    """Battle unit without board position: the client places it when the battle starts"""
    name: str
    job: str | None = None
    team: str
    sheet: str
    avatar: str | None = None   # badge image; monsters use their sheet instead
    ai: str | None = None
    offset_x: int
    offset_y: int
    hp: int
    max_hp: int
    ap: int
    max_ap: int
    skills: List[str]


class SpawnEntrySchema(BaseModel):
    """A monster that can appear in the hunt; weight = its chance relative to the others"""
    weight: int
    unit: UnitSchema


class BattleSchemaResponse(BaseModel):
    units: Dict[str, UnitSchema]        # only the hero: monsters come from spawn_pool, wave by wave
    skills: Dict[str, SkillSchema]
    spawn_rate: int                     # monsters per spawn wave
    spawn_pool: List[SpawnEntrySchema]
