import flet as ft
import themes as t
from components.panel_header import panel_header

# Keyboard shortcuts: the hero's n-th skill is triggered by the n-th key (see battle_page.handle_key)
SKILL_KEYS = ["Q", "W", "E", "R", "T"]
CARD_WIDTH = 147   # two cards plus the gap fit in the 330 px panel


def ap_badge(cost: int):
    """The skill's Action Point cost, in the game's gold."""
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=6, vertical=1), border_radius=8, bgcolor=t.AP_BG,
        content=ft.Text(f"{cost} AP", size=11, weight=ft.FontWeight.BOLD, color=t.AP_TEXT, font_family="Cinzel"),
    )


def skill_card(name: str, skill: dict, is_selected: bool, enabled: bool, on_click, hotkey: str | None = None):
    """Card with the skill's icon, name, AP cost and damage. The selected skill gets a golden border."""
    icon = ft.Container(
        width=36, height=36, bgcolor="#1A1712", border_radius=4,
        border=ft.Border.all(1, t.CARD_BORDER),
        alignment=ft.Alignment.BOTTOM_RIGHT, padding=ft.Padding(right=2, bottom=0),
        image=ft.DecorationImage(src=skill.get("icon"), fit=ft.BoxFit.COVER),
        content=ft.Text(hotkey or "", size=10, weight=ft.FontWeight.BOLD, color=t.NORMAL_TEXT, font_family="Cinzel",
                        style=ft.TextStyle(shadow=[ft.BoxShadow(blur_radius=2, color=t.DAMAGE_POPUP_OUTLINE)])),
    )
    info = ft.Column(spacing=2, expand=True, controls=[
        ft.Text(name, size=12, color=t.NORMAL_TEXT, font_family="Cinzel", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Text(f"Dmg {skill['damage']}", size=10, color=t.MUTED_TEXT, font_family="Cinzel"),
            ap_badge(skill["ap_cost"]),
        ]),
    ])
    return ft.Container(
        width=CARD_WIDTH, padding=6, border_radius=6, bgcolor=t.PANEL_INNER_BG,
        border=ft.Border.all(2 if is_selected else 1, t.CARD_BORDER_SELECTED if is_selected else t.CARD_BORDER),
        opacity=1 if enabled else 0.4, on_click=on_click,
        content=ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[icon, info]),
    )


def skills_panel(state, selected_skill: str | None, on_select, width: int, height: int):
    player_turn = (state.winner is None and not state.input_locked
                   and state.current_unit()["team"] == "player")
    unit = state.current_unit() if player_turn else None

    cards = []
    for index, name in enumerate(state.units["hero"]["skills"]):       # the player character's skills
        skill = state.skills[name]
        enabled = bool(unit) and unit["ap"] >= skill["ap_cost"]
        cards.append(skill_card(name, skill, selected_skill == name, enabled, lambda e, n=name: on_select(n),
                                SKILL_KEYS[index] if index < len(SKILL_KEYS) else None))

    hero = state.units["hero"]
    ap_note = ft.Text(f"AP: {hero['ap']}", size=14, weight=ft.FontWeight.BOLD, color=t.AP_TEXT, font_family="Cinzel")

    return ft.Container(
        width=width, height=height,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        padding=10,
        content=ft.Column(spacing=8, controls=[
            panel_header(ft.Icons.FLASH_ON, "Skills", ap_note),
            ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[ft.Row(wrap=True, spacing=8, run_spacing=8, width=width - 20, controls=cards)]),
        ]),
    )
