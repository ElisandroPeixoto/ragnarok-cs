from services.api_client import api


API_PREFIX = "/api/v1/battles"


class BattleService:
    """Handles battle-related API calls"""

    @staticmethod
    async def start_battle(character_id: int, map_id: str) -> dict:
        """Returns {"units": {...}, "skills": {...}}; units come without board position"""
        return await api.post(f"{API_PREFIX}/", json={"character_id": character_id, "map_id": map_id})
