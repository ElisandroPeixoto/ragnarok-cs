import flet as ft

MAP_ROUTE_PREFIX = "/map"


def map_route(map_id: str) -> str:
    """Monta a rota de um mapa a partir do seu id."""
    return f"{MAP_ROUTE_PREFIX}/{map_id}"


def navigate_to_map(map_id: str) -> None:
    ft.context.page.navigate(map_route(map_id))
