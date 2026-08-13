import flet as ft
import themes as t


########## Mock data - REPLACE AFTER INTEGRATE BACKEND
MOCK_CHARACTERS = [
    {"name": "DarknessChar", "job": "Novice", "level": 1, "hp": 50, "max_hp": 50, "sp": 10, "max_sp": 10, "sprite": "sprites/0.Novice_Idle.gif"},
]


SLOT_COUNT = 6
SLOT_WIDTH = 160
SLOT_HEIGHT = 248
####################


def character_slot(character: dict | None, on_click, is_selected: bool = False):
    """Single character slot card - filled or empty."""
    if character:
        content = ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[
                ft.Image(src=character["sprite"], width=62, height=133, fit=ft.BoxFit.CONTAIN)
                if character.get("sprite") else ft.Container(height=90),
                ft.Text(character["name"], size=14, color=t.TITLE_TEXT, font_family="Cinzel", weight=ft.FontWeight.BOLD),
                ft.Text(character["job"], size=12, color=t.NORMAL_TEXT, font_family="Cinzel"),
                ft.Text(f"Level: {character['level']}", size=12, color=t.NORMAL_TEXT, font_family="Cinzel"),
            ],
        )
    else:
        content = ft.Text("Empty", italic=True, color=t.MUTED_TEXT, font_family="Cinzel", size=14)

    border_color = t.CARD_BORDER_SELECTED if is_selected else t.CARD_BORDER
    border_width = 2 if is_selected else 1

    return ft.Container(
        width=SLOT_WIDTH,
        height=SLOT_HEIGHT,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(border_width, border_color),
        border_radius=6,
        alignment=ft.Alignment.CENTER,
        content=content,
        on_click=on_click,
    )


def info_panel(character: dict | None):
    """Right side panel showing HP/SP of the selected character."""
    hp = character["hp"] if character else 0
    max_hp = character["max_hp"] if character else 0
    sp = character["sp"] if character else 0
    max_sp = character["max_sp"] if character else 0

    def stat_row(label, value):
        return ft.Row(
            controls=[
                ft.Text(label, color=t.TITLE_TEXT, font_family="Cinzel", size=15),
                ft.Text(value, color=t.NORMAL_TEXT, font_family="Cinzel", size=15),
            ],
            spacing=8,
        )

    return ft.Container(
        width=300,
        height=SLOT_HEIGHT * 2 + 10,
        bgcolor=t.PANEL_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=6,
        padding=20,
        content=ft.Column(
            controls=[
                stat_row("HP:", f"{hp}/{max_hp}"),
                stat_row("SP:", f"{sp}/{max_sp}"),
            ],
            spacing=14,
        ),
    )

@ft.component
def character_selection():
    selected, set_selected = ft.use_state(0)

    slots = MOCK_CHARACTERS + [None] * (SLOT_COUNT - len(MOCK_CHARACTERS))

    def make_click(index):
        return lambda e: set_selected(index)

    grid = ft.Column(
        controls=[ft.Row(controls=[character_slot(slots[row * 3 + col], make_click(row * 3 + col), is_selected=(selected == row * 3 + col)) for col in range(3)],
                         spacing=15)
                  for row in range(2)],
        spacing=15,
    )

    action_buttons = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Button(
                        content=ft.Text("CREATE CHARACTER", font_family="Cinzel", size=13, color=t.NORMAL_TEXT, text_align=ft.TextAlign.CENTER),
                        bgcolor=t.BUTTON_SECONDARY,
                        width=145,
                        on_click=lambda e: ft.context.page.navigate("/char_creation")
                    ),
                    ft.Button(
                        content=ft.Text("DELETE CHARACTER", font_family="Cinzel", size=13, color=t.NORMAL_TEXT, text_align=ft.TextAlign.CENTER),
                        bgcolor=t.BUTTON_ALERT,
                        width=145,
                    ),
                ],
                spacing=10,
            ),
            ft.Button(
                content=ft.Text("START GAME", font_family="Cinzel", size=15, color=t.NORMAL_TEXT, text_align=ft.TextAlign.CENTER),
                bgcolor=t.BUTTON_PRIMARY,
                width=300,
            ),
        ],
        spacing=10,
        width=300,
    )

    right_side = ft.Column(
        controls=[info_panel(slots[selected]), action_buttons],
        spacing=15,
    )

    body = ft.Row(
        controls=[grid, right_side],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=30,
    )

    title = ft.Text(
        "Character Selection",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=t.TITLE_TEXT,
        font_family="Cinzel",
    )

    page_content = ft.Column(
        controls=[title, ft.Container(height=20), body],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.START,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    background_layer = ft.Container(
        expand=True,
        opacity=0.1,
        image=ft.DecorationImage(src="background.png", fit=ft.BoxFit.COVER),
    )

    foreground_layer = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=40,
        content=page_content,
    )

    return ft.Container(
        expand=True,
        bgcolor=t.BACKGROUND_OPACITY,
        content=ft.Stack(controls=[background_layer, foreground_layer], expand=True),
    )
