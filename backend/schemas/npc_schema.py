from pydantic import BaseModel


class NpcSchema(BaseModel):
    name: str
    image: str
