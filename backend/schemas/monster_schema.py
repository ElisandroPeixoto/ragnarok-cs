from pydantic import BaseModel


class MonsterSchema(BaseModel):
    name: str
    sheet: str
    level: int
    base_exp: int
    spawn_rate: int
