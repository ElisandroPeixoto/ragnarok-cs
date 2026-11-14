from pydantic import BaseModel, Field
from decimal import Decimal


class CharacterSchemaBase(BaseModel):
    name: str


class CharacterSchemaCreate(CharacterSchemaBase):
    pass

class CharacterSchemaPlaceUpdate(BaseModel):
    map_id: str


class CharacterSchemaBattleResult(BaseModel):
    """What the client reports when a hunt ends; the backend works out the EXP from it"""
    kills: list[str] = Field(default_factory=list, max_length=1000)   # monster names, one per kill
    defeated: bool = False                                           # the hero died


class CharacterSchemaResponse(CharacterSchemaBase):
    id: int
    job: str
    level: int
    exp: int
    hp: int
    current_map: str
    current_map_id: str
    zeny: Decimal
    max_hp: int
    max_sp: int

    class Config:
        from_attributes = True


class BattleResultResponse(BaseModel):
    character: CharacterSchemaResponse
    exp_gained: int
    exp_lost: int
