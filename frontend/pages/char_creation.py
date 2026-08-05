import flet as ft


@ft.component
def character_creation():
    return ft.Column(
        controls=[ft.Text("Character Creation"), ft.Button("Back", on_click=lambda: ft.context.page.navigate("/char_selection"))],
    )
