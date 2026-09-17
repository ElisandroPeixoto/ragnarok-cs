from pydantic import BaseModel
from decimal import Decimal


class CharacterSchemaBase(BaseModel):
    name: str


class CharacterSchemaCreate(CharacterSchemaBase):
    pass

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
