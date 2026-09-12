import flet as ft
import themes as t


def zeny_badge(zeny: int):
    return ft.Container(padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                        bgcolor=t.CARD_BG,
                        border=ft.Border.all(1, t.CARD_BORDER),
                        border_radius=20,
                        content=ft.Row(spacing=8,
                                       controls=[
                                           ft.Image(src="icons/zeny.png", width=23, height=26),
                                           ft.Text(f"{zeny}z", size=14, color=t.NORMAL_TEXT, font_family="Cinzel"),
                                       ]))
