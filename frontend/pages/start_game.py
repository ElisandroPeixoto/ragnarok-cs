import flet as ft


@ft.component
def start_game():
    return ft.Column(
        controls=[ft.Text("Ragnarok C.S"), ft.Button("Start Game", on_click=lambda: ft.context.page.navigate("/character_selection"))],
    )
