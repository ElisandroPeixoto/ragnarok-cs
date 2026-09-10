import flet as ft
import themes as t


# Mocked data — backend integration deferred
MOCK_CHARACTER = {
    "name": "CharName",
    "job": "Novice",
    "level": 1,
    "job_level": 1,
    "hp": 50,
    "max_hp": 50,
    "exp": 0,
    "max_exp": 100,
    "current_map": "Novice Academy",
    "zeny": 200,
    "sprite": "sprites/0.Novice_Idle.gif",
    "map_thumbnail": "maps/0_novice_academy.jpg",
}


SIDEBAR_WIDTH = 240
SIDEBAR_WIDTH_COLLAPSED = 72
SIDEBAR_BG = "#0A0C14"
STAT_BAR_BG = "#1A1712"
HP_BAR_COLOR = "#B3261E"
EXP_BAR_COLOR = t.BUTTON_PRIMARY


def status_bar(label: str, value: int, max_value: int, bar_color: str):  # TODO: MOVE TO COMPONENTS FOLDER
    """Labeled status bar. e.g.: HP, EXP, etc."""

    ratio = (value / max_value) if max_value else 0

    return ft.Column(spacing=4, controls=[
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            ft.Text(label, size=13, color=t.NORMAL_TEXT, font_family="Cinzel"),
            ft.Text(f"{value}/{max_value}", size=13, color=t.NORMAL_TEXT, font_family="Cinzel"),
        ]),
        ft.ProgressBar(value=ratio, bgcolor=STAT_BAR_BG, color=bar_color, bar_height=8, border_radius=4)
    ])


def sidebar_item(icon: str, label: str, on_click=None, collapsed: bool = False):  # TODO: MOVE TO COMPONENTS FOLDER
    return ft.Container(padding=ft.Padding(left=20, top=10, right=20, bottom=10) if not collapsed else ft.Padding.all(10),
                        alignment=ft.Alignment.CENTER if collapsed else None,
                        bgcolor=t.CARD_BG,
                        border_radius=6,
                        on_click=on_click,
                        content=ft.Row(spacing=12, controls=[
                            ft.Image(src=icon, width=23, height=26),
                            *([] if collapsed else [
                                ft.Text(label, size=15, font_family="Cinzel", color=t.TITLE_TEXT),
                            ])
                        ]))

def sidebar(collapsed: bool, on_toggle):
    toggle_button = ft.Container(alignment=ft.Alignment.CENTER if collapsed else None,
                                 padding=ft.Padding(left=10 if not collapsed else 0, top=16, right=10, bottom=0),
                                 on_click=on_toggle,
                                 content=ft.Icon(ft.Icons.MENU_OPEN if not collapsed else ft.Icons.MENU,
                                                 size=22,
                                                 color=t.MUTED_TEXT))
    logo = ft.Container(alignment=ft.Alignment.CENTER,
                        padding=ft.Padding.symmetric(vertical=16),
                        content=ft.Container(
                            width=50 if collapsed else 90,
                            height=50 if collapsed else 90,
                            border_radius=35,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Image(src="Icon.png")
                        ))
    nav_items = ft.Column(spacing=4,
                          controls=[
                              sidebar_item("icons/profile.png", "Profile", collapsed=collapsed),
                              sidebar_item("icons/quests.png", "Quests", collapsed=collapsed),
                              sidebar_item("icons/inventory.png", "Inventory", collapsed=collapsed),
                              sidebar_item("icons/map.png", "World Map", collapsed=collapsed),
                              sidebar_item("icons/instances.png", "Instances", collapsed=collapsed),
                              sidebar_item("icons/wiki.png", "Wiki", collapsed=collapsed),
                              sidebar_item("icons/change_char.png", "Change Character", collapsed=collapsed,
                                           on_click=lambda e: ft.context.page.navigate("/char_selection"))])

    return ft.Container(width=SIDEBAR_WIDTH_COLLAPSED if collapsed else SIDEBAR_WIDTH,
                        bgcolor=SIDEBAR_BG,
                        padding=ft.Padding(left=10, right=10, top=0, bottom=20),
                        animate=ft.Animation(duration=250, curve=ft.AnimationCurve.EASE_IN_OUT),
                        content=ft.Column(controls=[toggle_button, logo, nav_items], spacing=0))

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
                                                    status_bar("HP", character["hp"], character["max_hp"],HP_BAR_COLOR),
                                                    status_bar("EXP", character["exp"], character["max_exp"],EXP_BAR_COLOR)]))

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
