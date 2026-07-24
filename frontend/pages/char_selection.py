import flet as ft


@ft.component
def character_selection():
    return ft.Column(
        controls=[ft.Text("Character Selection", size=24),
                  ft.Button(content="Button", on_click=lambda: ft.context.page.navigate("/char_creation"))]
    )
