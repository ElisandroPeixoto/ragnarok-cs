import flet as ft
import themes as t


def character_badge(character: dict):
    """Small avatar + name badge shown at the top of map screens."""
    avatar = ft.Container(
        width=32,
        height=32,
        border_radius=16,
        bgcolor="#1A1712",
        image=ft.DecorationImage(src=character["sprite"], fit=ft.BoxFit.COVER)
        if character.get("sprite") else None,
    )

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=20,
        content=ft.Row(
            spacing=10,
            controls=[avatar, ft.Text(character["name"], size=14, color=t.NORMAL_TEXT, font_family="Cinzel")],
        ),
    )
