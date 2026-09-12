import flet as ft
import themes as t
from components.sidebar import sidebar
from components.zeny_badge import zeny_badge
from components.status_bars import status_bar

# Mocked data — backend integration deferred
MOCK_CHARACTER = {
    "name": "CharName",
    "job": "Novice",
    "level": 1,
    "job_level": 1,
    "hp": 20,
    "max_hp": 50,
    "exp": 0,
    "max_exp": 100,
    "current_map": "Novice Academy",
    "zeny": 200,
    "sprite": "sprites/0.Novice_Idle.gif",
    "map_thumbnail": "maps/0_novice_academy.jpg",
}


def character_card(character: dict):
    return ft.Container(width=260,
                        bgcolor=t.CARD_BG,
                        border=ft.Border.all(1, t.CARD_BORDER),
                        border_radius=6,
                        padding=20,
                        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                          spacing=10,
                                          controls=[ft.Image(src=character["sprite"], width=90, height=190, fit=ft.BoxFit.CONTAIN),
                                                    ft.Text(character["name"], size=22, font_family="Cinzel", color=t.NORMAL_TEXT, weight=ft.FontWeight.BOLD),
                                                    ft.Text(character["job"], size=15, font_family="Cinzel", color=t.TITLE_TEXT),
                                                    ft.Container(height=8),
                                                    ft.Text(f"Level: {character['level']}", size=13, color=t.NORMAL_TEXT, font_family="Cinzel"),
                                                    ft.Text(f"Job: {character['job_level']}", size=13, color=t.NORMAL_TEXT, font_family="Cinzel"),
                                                    ft.Container(height=4),
                                                    status_bar("HP", character["hp"], character["max_hp"],t.HP_BAR_COLOR),
                                                    status_bar("EXP", character["exp"], character["max_exp"],t.EXP_BAR_COLOR)]))

def current_place_card(character: dict):
    return ft.Container(bgcolor=t.CARD_BG,
                        border=ft.Border.all(1, t.CARD_BORDER),
                        border_radius=6,
                        padding=16,
                        content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                       spacing=16,
                                       controls=[ft.Container(width=90,
                                                              height=60,
                                                              border_radius=4,
                                                              bgcolor="#1A1712",
                                                              image=ft.DecorationImage(src=character["map_thumbnail"], fit=ft.BoxFit.COVER),
                                                              ),
                                                 ft.Column(spacing=2,
                                                           controls=[ft.Text("Current Place:", size=13, color=t.MUTED_TEXT, font_family="Cinzel"),
                                                                     ft.Text(character["current_map"], size=18, font_family="Cinzel", color=t.NORMAL_TEXT, weight=ft.FontWeight.BOLD)]),
                                                 ft.Container(expand=True),
                                                 ft.Button(content=ft.Text("Enter", font_family="Cinzel", weight=ft.FontWeight.BOLD, size=14),
                                                           bgcolor=t.BUTTON_PRIMARY,
                                                           color=t.NORMAL_TEXT,
                                                           width=110)]
                                       ))

def info_panel(title: str):
    return ft.Container(
        expand=True,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=6,
        padding=20,
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Text(line, size=14, color=t.NORMAL_TEXT, font_family="Cinzel") for line in [title]
            ],
        ),
    )


def skills_panel():
    return ft.Container(
        height=260,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=6,
        alignment=ft.Alignment.CENTER,
        content=ft.Text("SKILLS", size=15, color=t.NORMAL_TEXT, font_family="Cinzel"),
    )


@ft.component
def profile_page():
    character = MOCK_CHARACTER  # TODO: INSERT BACKEND
    collapsed, set_collapsed = ft.use_state(False)

    def toggle_sidebar(e):
        set_collapsed(not collapsed)

    top_bar = ft.Row(alignment=ft.MainAxisAlignment.END,
                     controls=[zeny_badge(character["zeny"])])

    stats_row = ft.Row(spacing=16,
                       expand=True,
                       controls=[info_panel("ATTRIBUTES"), info_panel("STATUS")])

    right_column = ft.Column(expand=True,
                             spacing=16,
                             controls=[current_place_card(character), stats_row])

    top_row = ft.Row(vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                     spacing=16,
                     height=490,
                     controls=[character_card(character), right_column])

    main_content = ft.Column(expand=True,
                             spacing=16,
                             scroll=ft.ScrollMode.AUTO,
                             controls=[top_bar, top_row, skills_panel()])

    return ft.Container(expand=True,
                        bgcolor=t.BACKGROUND_OPACITY,
                        content=ft.Row(
                            expand=True,
                            spacing=0,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[sidebar(collapsed, toggle_sidebar),
                                      ft.Container(expand=True, padding=24, content=main_content)]
                        ))
