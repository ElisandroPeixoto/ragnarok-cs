from pydantic import BaseModel


class MonsterSchema(BaseModel):
    name: str
    image: str
    spawn_rate: int
