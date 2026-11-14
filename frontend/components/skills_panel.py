import flet as ft
import themes as t

# Keyboard shortcuts: the hero's n-th skill is triggered by the n-th key (see battle_page.handle_key)
SKILL_KEYS = ["Q", "W", "E", "R", "T"]


def skill_button(name: str, skill: dict, is_selected: bool, enabled: bool, on_click, hotkey: str | None = None):
    icon_src = skill.get("icon")
    icon = ft.Container(
        width=46, height=46,
        bgcolor="#1A1712",
        border=ft.Border.all(2 if is_selected else 1, t.CARD_BORDER_SELECTED if is_selected else t.CARD_BORDER),
        alignment=ft.Alignment.CENTER,
        image=ft.DecorationImage(src=icon_src, fit=ft.BoxFit.COVER),
        content=ft.Container(  # shortcut key in the icon's corner
            alignment=ft.Alignment.BOTTOM_RIGHT, padding=ft.Padding(right=3, bottom=1),
            content=ft.Text(hotkey or "", size=11, weight=ft.FontWeight.BOLD, color=t.NORMAL_TEXT,
                            font_family="Cinzel",
                            style=ft.TextStyle(shadow=[ft.BoxShadow(blur_radius=2, color=t.DAMAGE_POPUP_OUTLINE)])),
        ),
    )
    return ft.Container(
        opacity=1 if enabled else 0.4,
        on_click=on_click,
        content=ft.Column(
            spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[icon, ft.Text(name, size=11, color=t.NORMAL_TEXT, font_family="Cinzel")],
        ),
    )


def skills_panel(state, selected_skill: str | None, on_select, width: int, height: int):
    player_turn = (state.winner is None and not state.input_locked
                   and state.current_unit()["team"] == "player")
    unit = state.current_unit() if player_turn else None

    buttons = []
    for index, name in enumerate(state.units["hero"]["skills"]):       # the player character's skills
        skill = state.skills[name]
        enabled = bool(unit) and unit["ap"] >= skill["ap_cost"]
        buttons.append(skill_button(name, skill, selected_skill == name, enabled,
                                    lambda e, n=name: on_select(n),
                                    SKILL_KEYS[index] if index < len(SKILL_KEYS) else None))

    return ft.Container(
        width=width, height=height,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        padding=10,
        content=ft.Column(spacing=10, controls=[
            ft.Text("Skills", size=18, color=t.NORMAL_TEXT, font_family="Cinzel"),
            ft.Row(spacing=12, controls=buttons),
        ]),
    )