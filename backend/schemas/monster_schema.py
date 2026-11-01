from pydantic import BaseModel


class MonsterSchema(BaseModel):
    name: str
    sheet: str
    spawn_rate: int
