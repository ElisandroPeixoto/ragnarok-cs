import flet as ft
import themes as t
from components.sheet_sprite import monster_sprite


def unit_card(unit: dict, is_active: bool):
    alive = unit["hp"] > 0
    avatar_src = unit.get("avatar")

    avatar = ft.Container(
        width=48, height=48,
        bgcolor="#1A1712",
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=2,
        # players have a badge image; monsters show their sheet's idle animation
        image=ft.DecorationImage(src=avatar_src, fit=ft.BoxFit.COVER) if avatar_src else None,
        content=None if avatar_src else monster_sprite(unit["sheet"], width=46, height=46),
    )

    identity = [ft.Text(unit["name"], size=16, color=t.NORMAL_TEXT, font_family="Cinzel")]
    if unit.get("job"):
        identity.append(ft.Text(unit["job"], size=11, color=t.NORMAL_TEXT, font_family="Cinzel"))
    identity.append(ft.Row(spacing=2, tight=True, controls=[   # where the unit stands on the board
        ft.Icon(ft.Icons.PLACE_OUTLINED, size=12, color=t.MAP_MUTED_TEXT),
        ft.Text(f"({unit['col']}, {unit['row']})", size=12, color=t.MAP_MUTED_TEXT, font_family="Cinzel"),
    ]))

    ap_pill = ft.Container(   # Action Points: a subtle gold tag, same size as the HP text
        padding=ft.Padding.symmetric(horizontal=8, vertical=1), border_radius=10, bgcolor=t.AP_BG_SUBTLE,
        content=ft.Text(f"AP:  {unit['ap']}/{unit['max_ap']}", size=12, color=t.AP_TEXT_SUBTLE, font_family="Cinzel"),
    )
    stats = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(f"HP:  {unit['hp']}/{unit['max_hp']}", size=12, color=t.NORMAL_TEXT, font_family="Cinzel"),
            ap_pill,
        ],
    )

    # red HP bar: shrinks as the unit loses health
    hp_bar = ft.ProgressBar(value=max(0, unit["hp"]) / unit["max_hp"] if unit["max_hp"] else 0,
                            bgcolor=t.STAT_BAR_BG, color=t.HP_BAR_COLOR, bar_height=6, border_radius=3)

    return ft.Container(
        bgcolor=t.CARD_BG,
        border=ft.Border.all(2 if is_active else 1, t.CARD_BORDER_SELECTED if is_active else t.CARD_BORDER),
        padding=6,
        opacity=1 if alive else 0.4,
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Row(spacing=8, controls=[avatar, ft.Column(spacing=1, controls=identity)]),
                hp_bar,
                stats,
            ],
        ),
    )


def units_panel(state, width: int, height: int):
    """Units in turn order; the one currently playing gets a golden border."""
    cards = [unit_card(state.units[unit_id], unit_id == state.current_unit_id and state.winner is None)
             for unit_id in state.turn_order]
    return ft.Container(
        width=width, height=height,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        padding=8,
        content=ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, controls=cards),
    )
