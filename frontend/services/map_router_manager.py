import flet as ft
from services.api_client import ApiError
from services.character_service import CharacterService
from services.session_state import (
    set_battle_return_route, get_battle_return_route, set_battle_setup, set_current_character,
)


MAP_ROUTE_PREFIX = "/map"
BATTLE_ROUTE = "/battle"


def map_route(map_id: str) -> str:
    """Builds a map's route from its id."""
    return f"{MAP_ROUTE_PREFIX}/{map_id}"


def navigate_to_map(map_id: str) -> None:
    ft.context.page.navigate(map_route(map_id))


def change_place(character: dict, map_id: str) -> None:
    """Moves the character to another map: saves the new place on the backend, then opens the map."""
    async def move():
        try:
            set_current_character(await CharacterService.change_place(character["id"], map_id))
        except ApiError as error:
            print(f"Failed to register the new place: {error.detail}")
            return
        navigate_to_map(map_id)

    ft.context.page.run_task(move)


def navigate_to_battle(return_route: str, setup: dict) -> None:
    """setup = the BattleService.start_battle response"""
    set_battle_return_route(return_route)
    set_battle_setup(setup)
    ft.context.page.navigate(BATTLE_ROUTE)


def navigate_back_from_battle() -> None:
    ft.context.page.navigate(get_battle_return_route() or "/profile_page")
