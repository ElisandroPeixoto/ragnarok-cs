import flet as ft
import themes as t


def item_card(image: str, label: str, on_click=None):
    """Small square card used for NPCs and Navigation entries."""
    return ft.Container(
        width=100,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=6,
        padding=10,
        on_click=on_click,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Container(
                    width=70,
                    height=70,
                    border_radius=6,
                    bgcolor="#1A1712",
                    image=ft.DecorationImage(src=image, fit=ft.BoxFit.COVER),
                ),
                ft.Text(label, size=13, color=t.NORMAL_TEXT, font_family="Cinzel",
                        text_align=ft.TextAlign.CENTER),
            ],
        ),
    )