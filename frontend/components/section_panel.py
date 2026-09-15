import flet as ft
import themes as t


def section_panel(title: str, items: list, empty_message: str, item_builder):
    """Bordered card with a title and a row of item_cards, or an empty state.
    Reused for NPCs, Navigation and Monsters panels on map screens."""
    if items:
        body = ft.Row(controls=[item_builder(item) for item in items], spacing=12, wrap=True)
    else:
        body = ft.Container(
            alignment=ft.Alignment.CENTER,
            padding=20,
            content=ft.Text(empty_message, size=14, color=t.MUTED_TEXT, font_family="Cinzel"),
        )

    return ft.Container(
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=6,
        padding=16,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=t.TITLE_TEXT, font_family="Cinzel"),
                body,
            ],
        ),
    )