import asyncio
import flet as ft
from services.api_client import ApiError
from services.character_service import CharacterService
from components.travel_dialog import travel_dialog
from services.session_state import (
    set_battle_return_route, get_battle_return_route, set_battle_setup, set_current_character,
)


MAP_ROUTE_PREFIX = "/map"
BATTLE_ROUTE = "/battle"
TRAVEL_SECONDS = 5   # how long the travel pop up stays on before the new map opens (placeholder duration)


def map_route(map_id: str) -> str:
    """Builds a map's route from its id."""
    return f"{MAP_ROUTE_PREFIX}/{map_id}"


def navigate_to_map(map_id: str) -> None:
    ft.context.page.navigate(map_route(map_id))


def change_place(character: dict, map_id: str, instant: bool = False) -> None:
    """Moves the character to another map: a pop up with his walking animation stays on for TRAVEL_SECONDS, then
    the new place is saved on the backend and the map opens. The pop up's Cancel button stops the trip before
    that: nothing is saved and the character stays where he is. Going into a building is `instant`: no pop up."""
    async def move():
        page = ft.context.page
        if instant:
            try:
                updated = await CharacterService.change_place(character["id"], map_id)
            except ApiError as error:
                print(f"Failed to register the new place: {error.detail}")
                return
            set_current_character(updated)
            navigate_to_map(map_id)
            return
        cancelled = asyncio.Event()
        dialog, animate = travel_dialog(character["job"], lambda e: cancelled.set())
        page.show_dialog(dialog)
        animation = asyncio.create_task(animate())
        try:
            await asyncio.wait_for(cancelled.wait(), TRAVEL_SECONDS)   # returns early only if Cancel is pressed
            trip_cancelled = True
        except asyncio.TimeoutError:
            trip_cancelled = False   # the trip lasted its whole duration
        animation.cancel()
        if trip_cancelled:
            page.pop_dialog()
            return
        try:
            updated = await CharacterService.change_place(character["id"], map_id)
        except ApiError as error:
            print(f"Failed to register the new place: {error.detail}")
            return
        finally:
            page.pop_dialog()
        set_current_character(updated)
        navigate_to_map(map_id)

    ft.context.page.run_task(move)


def navigate_to_battle(return_route: str, setup: dict) -> None:
    """setup = the BattleService.start_battle response"""
    set_battle_return_route(return_route)
    set_battle_setup(setup)
    ft.context.page.navigate(BATTLE_ROUTE)


def navigate_back_from_battle() -> None:
    ft.context.page.navigate(get_battle_return_route() or "/profile_page")
