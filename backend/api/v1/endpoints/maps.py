from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, cast
from models.maps_model import MapModel
from schemas.map_schema import MapSchemaResponse, MapSchemaSummary
from core.deps import get_session
from sqlalchemy.orm import selectinload
from models.map_monster_model import MapMonsterModel
from models.map_connection_model import MapConnectionModel
from models.map_place_model import MapPlaceModel

router = APIRouter()


def place_to_dict(place: MapPlaceModel) -> dict:
    target = place.target_map
    return {
        "id": place.id, "name": place.name, "kind": place.kind, "icon": place.icon,
        "x": place.x, "y": place.y, "direction": place.direction,
        "target": {"map_id": target.id, "name": target.name, "level_range": target.level_range,
                   "zone": target.zone} if target else None,
    }


def to_response(map_model: MapModel) -> dict:
    """Flatten ORM relations into the shape the frontend already consumes"""
    return {
        "id": map_model.id,
        "name": map_model.name,
        "level_range": map_model.level_range,
        "image": map_model.image,
        "about": map_model.about,
        "zone": map_model.zone,
        "places": [place_to_dict(place) for place in map_model.places],
        "npcs": [{"name": npc.name, "image": npc.image, "place_id": npc.place_id, "greeting": npc.greeting}
                 for npc in map_model.npcs],
        "monsters": [{"name": monster_spawn.monster.name,
                      "sheet": monster_spawn.monster.sheet,
                     "spawn_rate": monster_spawn.spawn_rate} for monster_spawn in map_model.monster_spawns],
        "navigation":[{"name": connection.to_map.name,
                       "image": connection.to_map.image,
                       "map_id": connection.to_map.id,
                       "level_range": connection.to_map.level_range} for connection in map_model.connections],

    }


"""Retrieve all the maps (id + name)"""
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[MapSchemaSummary])
async def get_maps(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(MapModel))
    return result.scalars().all()


"""Retrieve a map with its NPCs, monsters and navigation"""
@router.get("/{map_id}", status_code=status.HTTP_200_OK, response_model=MapSchemaResponse)
async def get_map_by_id(map_id: str, db: AsyncSession = Depends(get_session)):
    query = (
        select(MapModel)
        .where(MapModel.id == map_id)
        .options(
            selectinload(MapModel.npcs),
            selectinload(MapModel.places).selectinload(MapPlaceModel.target_map),
            selectinload(MapModel.monster_spawns).selectinload(MapMonsterModel.monster),
            selectinload(MapModel.connections).selectinload(MapConnectionModel.to_map),
        )
    )
    result = await db.execute(query)
    game_map = result.scalar_one_or_none()

    if game_map is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

    return to_response(game_map)
