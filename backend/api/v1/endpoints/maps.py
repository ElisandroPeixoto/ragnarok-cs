from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, cast
from models.maps_model import MapModel
from schemas.map_schema import MapSchemaResponse, MapSchemaSummary
from core.deps import get_session
from sqlalchemy.orm import selectinload

router = APIRouter()


def to_response(map_model: MapModel) -> dict:
    """Flatten ORM relations into the shape the frontend already consumes"""
    return {
        "id": map_model.id,
        "name": map_model.name,
        "level_range": map_model.level_range,
        "image": map_model.image,
        "about": map_model.about,
        "npcs": [{"name": npc.name, "image": npc.image} for npc in map_model.npcs],
        "monsters": [{"name": monster_spawn.monster.name,
                      "image": monster_spawn.monster.image,
                     "spawn_rate": monster_spawn.spawn_rate} for monster_spawn in map_model.monster_spawns],
        "navigation":[{"name": connection.to_map.name,
                       "image": connection.to_map.image,
                       "map_id": connection.to_map.id} for connection in map_model.connections],

    }


"""Retrieve all the maps (id + name)"""
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[MapSchemaSummary])
async def get_maps(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(MapModel))
    return result.scalars().all()


"""Retrieve a map with its NPCs, monsters and navigation"""
@router.get("/{map_id}", status_code=status.HTTP_200_OK, response_model=MapSchemaResponse)  # TODO: ENDPOINT NOT WORKING
async def get_map_by_id(map_id: str, db: AsyncSession = Depends(get_session)):
    game_map = cast(MapModel | None,await db.get(MapModel, map_id))  # cast: Type checker only

    if game_map is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

    return to_response(game_map)