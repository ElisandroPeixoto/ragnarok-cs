import flet as ft
import themes as t


def panel_header(icon, title: str, right: ft.Control | None = None):
    """Title row of the combat panels: icon + title on the left, an optional note on the right."""
    return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                  controls=[
                      ft.Row(spacing=6, tight=True, controls=[
                          ft.Icon(icon, size=18, color=t.TITLE_TEXT),
                          ft.Text(title, size=16, color=t.NORMAL_TEXT, font_family="Cinzel"),
                      ]),
                      right if right is not None else ft.Container(),
                  ])
