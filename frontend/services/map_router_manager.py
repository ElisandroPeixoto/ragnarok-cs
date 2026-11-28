import asyncio
import flet as ft
from services.api_client import ApiError
from services.character_service import CharacterService
from services.session_state import (
    set_battle_return_route, get_battle_return_route, set_battle_setup, set_current_character,
)


MAP_ROUTE_PREFIX = "/map"
BATTLE_ROUTE = "/battle"
TRAVEL_SECONDS = 5   # how long the character walks before the new map opens (placeholder duration)


def map_route(map_id: str) -> str:
    """Builds a map's route from its id."""
    return f"{MAP_ROUTE_PREFIX}/{map_id}"


def navigate_to_map(map_id: str) -> None:
    ft.context.page.navigate(map_route(map_id))


async def move_to(character: dict, map_id: str) -> bool:
    """Saves the character's new place on the backend and opens that map. False if the backend refused it."""
    try:
        updated = await CharacterService.change_place(character["id"], map_id)
    except ApiError as error:
        print(f"Failed to register the new place: {error.detail}")
        return False
    set_current_character(updated)
    navigate_to_map(map_id)
    return True


async def walk_to(character: dict, map_id: str, stopped: asyncio.Event) -> bool:
    """The trip to another map: waits TRAVEL_SECONDS (the map screen shows the character walking meanwhile), then
    moves the character there. Setting `stopped` before that (the Stop button) ends the trip: nothing is saved and
    the character stays where he is. Returns True only if the character arrived."""
    try:
        await asyncio.wait_for(stopped.wait(), TRAVEL_SECONDS)   # returns early only if the trip is stopped
        return False
    except asyncio.TimeoutError:
        pass   # the trip lasted its whole duration
    return await move_to(character, map_id)


def change_place(character: dict, map_id: str) -> None:
    """Instant move, with no walk (going in or out of a building)."""
    ft.context.page.run_task(move_to, character, map_id)


def navigate_to_battle(return_route: str, setup: dict) -> None:
    """setup = the BattleService.start_battle response"""
    set_battle_return_route(return_route)
    set_battle_setup(setup)
    ft.context.page.navigate(BATTLE_ROUTE)


def navigate_back_from_battle() -> None:
    ft.context.page.navigate(get_battle_return_route() or "/profile_page")
