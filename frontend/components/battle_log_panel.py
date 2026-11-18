import flet as ft
import themes as t
from components.panel_header import panel_header


def log_row(entry):
    spans = [ft.TextSpan(f"R{entry.round:02d}  ", style=ft.TextStyle(color=t.MUTED_TEXT, size=11)),
             ft.TextSpan(entry.message + " ")]
    if entry.damage_text:
        spans.append(ft.TextSpan(entry.damage_text, style=ft.TextStyle(color=t.DAMAGE_TEXT)))
    if entry.level_text:
        spans.append(ft.TextSpan(entry.level_text, style=ft.TextStyle(color=t.LEVEL_UP_TEXT)))
    return ft.Text(spans=spans, size=15, color=t.NORMAL_TEXT, font_family="Cinzel")


def battle_log_panel(entries, width: int, height: int):
    live_feed = ft.Text("Live Feed", size=11, color=t.MUTED_TEXT, font_family="Cinzel")
    return ft.Container(
        width=width, height=height,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        padding=10,
        content=ft.Column(spacing=8, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                          controls=[
                              panel_header(ft.Icons.RECEIPT_LONG, "Battle Log", live_feed),
                              ft.Container(
                                  expand=True,
                                  bgcolor=t.PANEL_INNER_BG,
                                  border=ft.Border.all(1, t.CARD_BORDER),
                                  border_radius=6,
                                  padding=8,
                                  content=ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, auto_scroll=True,
                                                    controls=[log_row(e) for e in entries]),
                              ),
                          ]),
    )
