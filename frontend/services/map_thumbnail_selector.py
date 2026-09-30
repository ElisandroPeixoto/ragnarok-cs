from services.map_service import MapService
from services.api_client import ApiError


async def map_thumbnail_selector(map_id: str) -> str | None:
    try:
        map_data = await MapService.get_map(map_id)
        return map_data.get("image")
    except ApiError:
        return None