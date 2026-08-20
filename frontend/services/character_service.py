from services.api_client import api


API_PREFIX = "/api/v1/characters"


class CharacterService:
    """Handles character-related API calls"""

    @staticmethod
    async def get_characters() -> list[dict]:
        return await api.get(f"{API_PREFIX}/")

    @staticmethod
    async def create_character(name: str) -> dict:
        return await api.post(f"{API_PREFIX}/", json={"name": name})
