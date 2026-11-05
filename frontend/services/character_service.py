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

    @staticmethod
    async def change_place(character_id: int, map_id: str) -> dict:
        """Registers the character's new place; returns the updated character"""
        return await api.patch(f"{API_PREFIX}/{character_id}/place", json={"map_id": map_id})

    @staticmethod
    async def delete_character(character_id: int) -> None:
        await api.delete(f"{API_PREFIX}/{character_id}")
