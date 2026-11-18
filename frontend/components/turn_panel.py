import flet as ft
import themes as t
from components.panel_header import panel_header


def stat_box(label: str, value: str, value_color: str = t.NORMAL_TEXT):
    return ft.Container(
        expand=True, padding=ft.Padding.symmetric(vertical=6), border_radius=6, bgcolor=t.PANEL_INNER_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        content=ft.Column(spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Text(label, size=10, color=t.MUTED_TEXT, font_family="Cinzel"),
            ft.Text(value, size=17, weight=ft.FontWeight.BOLD, color=value_color, font_family="Cinzel"),
        ]),
    )


def turn_panel(state, on_end_turn, on_leave, width: int, height: int):
    can_end_turn = (state.winner is None and not state.input_locked
                    and state.current_unit()["team"] == "player")

    if state.winner == "victory":
        time_value, time_color = "Victory!", t.VICTORY_TEXT
    elif state.winner == "defeat":
        time_value, time_color = "Defeat", t.DEFEAT_TEXT
    elif state.input_locked:
        time_value, time_color = "Enemy", t.DEFEAT_TEXT
    else:
        time_value, time_color = f"{state.time_left}s", t.NORMAL_TEXT

    turn_end = ft.Button(
        content=ft.Row(spacing=6, tight=True, alignment=ft.MainAxisAlignment.CENTER, controls=[
            ft.Icon(ft.Icons.PLAY_ARROW, size=20, color=t.BUTTON_TURN_END_TEXT),
            ft.Text("Turn End", size=15, weight=ft.FontWeight.BOLD, color=t.BUTTON_TURN_END_TEXT,
                    font_family="Cinzel", no_wrap=True),
        ]),
        bgcolor=t.BUTTON_TURN_END, disabled=not can_end_turn, opacity=1 if can_end_turn else 0.45,
        expand=True, height=44, on_click=on_end_turn,
    )
    leave = ft.Container(   # only an icon: leaving costs nothing and pays nothing
        width=44, height=44, border_radius=8, bgcolor=t.BUTTON_ALERT, alignment=ft.Alignment.CENTER,
        tooltip="Leave", on_click=on_leave,
        content=ft.Icon(ft.Icons.LOGOUT, size=22, color=t.NORMAL_TEXT),
    )

    return ft.Container(
        width=width, height=height,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        padding=10,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(spacing=8, controls=[
                    panel_header(ft.Icons.TIMER_OUTLINED, "Turn"),
                    ft.Row(spacing=8, controls=[stat_box("Round", f"{state.round:02d}"), stat_box("Time", time_value, time_color)]),
                ]),
                ft.Row(spacing=8, controls=[turn_end, leave]),
            ],
        ),
    )
