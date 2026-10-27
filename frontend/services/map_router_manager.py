import flet as ft
from services.session_state import set_battle_return_route, get_battle_return_route, set_battle_setup


MAP_ROUTE_PREFIX = "/map"
BATTLE_ROUTE = "/battle"


def map_route(map_id: str) -> str:
    """Monta a rota de um mapa a partir do seu id."""
    return f"{MAP_ROUTE_PREFIX}/{map_id}"


def navigate_to_map(map_id: str) -> None:
    ft.context.page.navigate(map_route(map_id))


def navigate_to_battle(return_route: str, setup: dict) -> None:
    """setup = resposta do BattleService.start_battle"""
    set_battle_return_route(return_route)
    set_battle_setup(setup)
    ft.context.page.navigate(BATTLE_ROUTE)


def navigate_back_from_battle() -> None:
    ft.context.page.navigate(get_battle_return_route() or "/profile_page")
