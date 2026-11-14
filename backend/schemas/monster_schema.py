from pydantic import BaseModel


class MonsterSchema(BaseModel):
    name: str
    sheet: str
    level: int
    spawn_rate: int
