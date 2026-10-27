from fastapi import APIRouter
from api.v1.endpoints.characters import router as characters_router  # noqa
from api.v1.endpoints.maps import router as maps_router  # noqa
from api.v1.endpoints.battles import router as battles_router  # noqa


api_router = APIRouter()

api_router.include_router(characters_router, prefix="/characters", tags=["characters"])
api_router.include_router(maps_router, prefix="/maps", tags=["maps"])
api_router.include_router(battles_router, prefix="/battles", tags=["battles"])
