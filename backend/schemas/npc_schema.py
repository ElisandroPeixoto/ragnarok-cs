from pydantic import BaseModel


class NpcSchema(BaseModel):
    name: str
    image: str
    place_id: int | None = None
    greeting: str = ""
