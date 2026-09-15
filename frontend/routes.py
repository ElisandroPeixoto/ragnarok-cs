import flet as ft
from pages.char_creation import character_creation
from pages.char_selection import character_selection
from pages.start_game import start_game
from pages.profile_page import profile_page
from pages.map_screen import build_map_page
from services.map_router_manager import map_route
from mockup import MOCK_MAPS  # TODO: REMOVE AFTER INTEGRATION WITH BACKEND


def view_wrapper(component, route, appbar_visible=True):
    @ft.component
    def wrapped():
        return ft.View(
            route=route,
            appbar=ft.AppBar(visible=appbar_visible),
            padding=0,
            controls=[component()]
        )
    return wrapped


routes: list[ft.Route] = [
    ft.Route(index=True, component=view_wrapper(start_game, "/", appbar_visible=False)),
    ft.Route(path="/char_selection", component=view_wrapper(character_selection, "/char_selection", appbar_visible=False)),
    ft.Route(path="/char_creation", component=view_wrapper(character_creation, "/char_creation")),
    ft.Route(path="/profile_page", component=view_wrapper(profile_page, "/profile_page", appbar_visible=False)),
]

routes += [
    ft.Route(path=map_route(map_id),
             component=view_wrapper(build_map_page(map_id), map_route(map_id), appbar_visible=False))
    for map_id in MOCK_MAPS
]
