import flet as ft
import themes as t


def format_zeny(zeny) -> str:
    """Whole zeny with a dot as the thousands separator, e.g. 1234567 becomes 1.234.567z"""
    return f"{int(zeny or 0):,}".replace(",", ".") + "z"


def zeny_amount(zeny: int):
    """Zeny icon and value, without a frame (used inside other panels, e.g. the inventory's bag)"""
    return ft.Row(spacing=8, tight=True,
                  vertical_alignment=ft.CrossAxisAlignment.CENTER,
                  controls=[
                      ft.Image(src="icons/zeny.png", width=23, height=26),
                      ft.Text(format_zeny(zeny), size=14, color=t.NORMAL_TEXT, font_family="Cinzel"),
                  ])


def zeny_badge(zeny: int):
    return ft.Container(padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                        bgcolor=t.CARD_BG,
                        border=ft.Border.all(1, t.CARD_BORDER),
                        border_radius=20,
                        content=zeny_amount(zeny))
