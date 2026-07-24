import flet as ft
from pages.char_creation import character_creation
from pages.char_selection import character_selection
from pages.start_game import start_game

routes: list[ft.Route] = [
    ft.Route(index=True, component=start_game),
    ft.Route(path="/character_selection", component=character_selection),
    ft.Route(path="/char_creation", component=character_creation),
]
