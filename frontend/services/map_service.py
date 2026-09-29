import httpx
from services.api_client import api, BASE_URL

API_PREFIX = "/api/v1/maps"


class MapService:
    """Handles map-related API calls"""

    @staticmethod
    async def get_map(map_id: str) -> dict:
        return await api.get(f"{API_PREFIX}/{map_id}")

    @staticmethod
    def get_map_ids_sync() -> list[str]:
        """Sync on purpose: routes are registered at import time, before the event loop"""
        try:
            response = httpx.get(f"{BASE_URL}{API_PREFIX}/", timeout=5)
            response.raise_for_status()
            return [m["id"] for m in response.json()]
        except httpx.HTTPError:
            return []