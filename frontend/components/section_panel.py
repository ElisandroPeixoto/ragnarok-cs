import flet as ft
import themes as t

PANEL_HEIGHT = 295
HEADER_HEIGHT = 40


def section_panel(title: str, content: ft.Control, expand: int = 1):
    """Painel dos mapas: cabeçalho dourado com o título e o conteúdo logo abaixo.
    Usado em People in the area / Monsters / Go To."""
    header = ft.Container(
        height=HEADER_HEIGHT,
        bgcolor=t.MAP_PANEL_HEADER,
        border=ft.Border.all(1, t.MAP_PANEL_BORDER),
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=8),
        alignment=ft.Alignment.CENTER_LEFT,
        content=ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, font_family="Cinzel"),
    )

    return ft.Container(
        expand=expand,
        height=PANEL_HEIGHT,
        bgcolor=t.MAP_PANEL_BG,
        border=ft.Border.all(1, t.MAP_PANEL_BORDER),
        border_radius=10,
        content=ft.Column(
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                header,
                ft.Container(expand=True, padding=ft.Padding(left=8, top=8, right=6, bottom=8), content=content),
            ],
        ),
    )
