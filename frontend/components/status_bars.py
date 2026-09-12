import flet as ft
import themes as t


def status_bar(label: str, value: int, max_value: int, bar_color: str):
    """Labeled status bar. e.g.: HP, EXP, etc."""

    ratio = (value / max_value) if max_value else 0

    return ft.Column(spacing=4, controls=[
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            ft.Text(label, size=13, color=t.NORMAL_TEXT, font_family="Cinzel"),
            ft.Text(f"{value}/{max_value}", size=13, color=t.NORMAL_TEXT, font_family="Cinzel"),
        ]),
        ft.ProgressBar(value=ratio, bgcolor=t.STAT_BAR_BG, color=bar_color, bar_height=8, border_radius=4)
    ])
