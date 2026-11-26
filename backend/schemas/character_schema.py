from pydantic import BaseModel, Field, computed_field
from core.level_progression import exp_progress, exp_to_next
from core.battle_rules import MAX_MONSTERS
from decimal import Decimal


class CharacterSchemaBase(BaseModel):
    name: str


class CharacterSchemaCreate(CharacterSchemaBase):
    pass

class CharacterSchemaPlaceUpdate(BaseModel):
    map_id: str


class CharacterSchemaBattleResult(BaseModel):
    """What the client reports when a hunt ends; the backend works out the EXP from it.
    Victory: `kills` has every monster of the hunt (names). Defeat: the kills are ignored"""
    victory: bool
    kills: list[str] = Field(default_factory=list, max_length=MAX_MONSTERS)   # monster names, one per monster


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

    @computed_field
    @property
    def exp_progress(self) -> int:
        """EXP accumulated inside the current level (the EXP bar's value)"""
        return exp_progress(self.level, self.exp)

    @computed_field
    @property
    def exp_needed(self) -> int:
        """EXP the current level asks for to go up (the EXP bar's maximum); 0 at the maximum level"""
        return exp_to_next(self.level) or 0


class DropSchema(BaseModel):
    """An item a won hunt dropped, with how many units"""
    item_id: str
    name: str
    icon: str | None = None
    amount: int


class BattleResultResponse(BaseModel):
    character: CharacterSchemaResponse
    exp_gained: int
    exp_lost: int
    drops: list[DropSchema] = Field(default_factory=list)        # went into the bag
    drops_lost: list[DropSchema] = Field(default_factory=list)   # did not fit: the bag was full
