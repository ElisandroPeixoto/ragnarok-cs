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
    avatar: str
    ai: str | None = None
    offset_x: int
    offset_y: int
    hp: int
    max_hp: int
    ap: int
    max_ap: int
    skills: List[str]


class BattleSchemaResponse(BaseModel):
    units: Dict[str, UnitSchema]
    skills: Dict[str, SkillSchema]
