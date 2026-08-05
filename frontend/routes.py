import flet as ft
from pages.char_creation import character_creation
from pages.char_selection import character_selection
from pages.start_game import start_game


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
]
