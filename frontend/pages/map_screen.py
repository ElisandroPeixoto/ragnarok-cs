import flet as ft
import themes as t
from components.sidebar import sidebar
from components.zeny_badge import zeny_badge
from components.character_badge import character_badge
from components.section_panel import section_panel
from components.item_card import item_card, card_image
from services.session_state import get_current_character
from services.map_service import MapService
from services.api_client import ApiError
from typing import cast
from services.map_router_manager import map_route, navigate_to_battle
from services.battle_service import BattleService
from pages.battle_page import CONTENT_WIDTH as BATTLE_CONTENT_WIDTH


BANNER_HEIGHT = 494
GAP = 15

# Lugares visitáveis dentro de cada mapa (This Area). TODO: INSERT ON BACKEND; o destino dos botões é futuro
MAP_PLACES = {
    "novice_academy": [{"name": "Academy", "image": "places/academy.png"}],
}


def hunt_button(map_id: str, character: dict):
    def handle_hunt(e):
        async def start():
            try:
                setup = await BattleService.start_battle(character["id"], map_id)
            except ApiError as error:
                print(f"Failed to start battle: {error.detail}")
                return
            navigate_to_battle(map_route(map_id), setup)

        ft.context.page.run_task(start)

    return ft.Button(
        content=ft.Text("Hunt", font_family="Cinzel", size=14),
        bgcolor=t.BUTTON_PRIMARY,
        color=t.NORMAL_TEXT,
        on_click=handle_hunt,
    )


def npc_item(item: dict):
    return item_card(card_image(item["image"]), item["name"])


def monster_item(item: dict):
    spawn_rate = item.get("spawn_rate")
    subtitle = f"{spawn_rate}%" if spawn_rate is not None else None
    return item_card(card_image(item["image"]), item["name"], subtitle=subtitle)


def place_item(item: dict):
    return item_card(card_image(item["image"], width=56, height=73), item["name"],
                     width=170, height=84, tooltip="Coming soon", on_click=lambda e: None)


def navigation_item(item: dict):
    level_range = item.get("level_range")
    return item_card(ft.Icon(ft.Icons.ARROW_UPWARD, size=28, color=t.MAP_LIGHT_TEXT), item["name"],
                     subtitle=f"(Lv {level_range.replace(' ', '')})" if level_range else None,
                     width=184, height=84,
                     on_click=lambda e: ft.context.page.navigate(map_route(item["map_id"])))


def card_grid(cards: list):
    return ft.Row(wrap=True, spacing=10, run_spacing=10, controls=cards)


def empty_text(message: str):
    return ft.Text(message, size=14, color=t.MUTED_TEXT, font_family="Cinzel")


def label(text: str):
    return ft.Text(text, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, font_family="Cinzel")


def map_banner(map_data: dict):
    """Imagem do mapa com o título e o nível sobrepostos no canto superior esquerdo."""
    title_box = ft.Container(
        left=0, top=5,
        bgcolor=t.MAP_TITLE_OVERLAY,
        border_radius=10,
        padding=ft.Padding(left=15, top=8, right=15, bottom=12),
        content=ft.Column(spacing=4, controls=[
            ft.Text(map_data["name"], size=32, weight=ft.FontWeight.BOLD, color=t.MAP_TITLE_TEXT, font_family="Cinzel"),
            ft.Text(f"Level: {map_data.get('level_range', '-')}", size=18, weight=ft.FontWeight.BOLD,
                    color=t.MAP_LIGHT_TEXT, font_family="Cinzel"),
        ]),
    )
    top_shadow = ft.Container(  # sombra interna no topo da imagem (inset 0 120px 80px rgba(0,0,0,.3))
        left=0, top=0, right=0, height=200,
        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                                   colors=[ft.Colors.with_opacity(0.3, ft.Colors.BLACK), ft.Colors.TRANSPARENT]),
    )
    return ft.Container(
        height=BANNER_HEIGHT,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(expand=True, controls=[
            ft.Container(left=0, top=0, right=0, bottom=0,
                         image=ft.DecorationImage(src=map_data.get("image", ""), fit=ft.BoxFit.COVER)),
            top_shadow,
            title_box,
        ]),
    )


def monsters_content(map_id: str, monsters: list, character: dict):
    if monsters:
        return ft.Column(spacing=8, controls=[
            ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[card_grid([monster_item(m) for m in monsters])]),
            ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[hunt_button(map_id, character)]),
        ])
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8, controls=[
            ft.Text("Safe Zone", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, font_family="Cinzel"),
            ft.Icon(ft.Icons.SHIELD, size=90, color=t.MAP_PANEL_HEADER),
        ]),
    )


def go_to_content(map_data: dict):
    places = MAP_PLACES.get(map_data["id"], [])
    navigation = map_data.get("navigation", [])
    return ft.Column(scroll=ft.ScrollMode.AUTO, spacing=4, controls=[
        label("This Area"),
        card_grid([place_item(p) for p in places]) if places else empty_text("Nothing to visit here"),
        label("Nearby"),
        card_grid([navigation_item(n) for n in navigation]) if navigation else empty_text("No routes available"),
    ])


def map_screen(map_data: dict, character: dict):
    top_controls = [character_badge(character), zeny_badge(character["zeny"])]
    top_bar = ft.Row(spacing=8, controls=top_controls)

    npcs = map_data.get("npcs", [])
    people = (ft.Column(scroll=ft.ScrollMode.AUTO, controls=[card_grid([npc_item(n) for n in npcs])])
              if npcs else empty_text("No one around"))

    panels = ft.Row(
        spacing=GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[  # proporção das larguras do Figma: 348 / 348 / 483
            section_panel("People in the area", people, expand=348),
            section_panel("Monsters", monsters_content(map_data["id"], map_data.get("monsters", []), character), expand=348),
            section_panel("Go To", go_to_content(map_data), expand=483),
        ],
    )

    return ft.Container(
        expand=True,
        padding=ft.Padding(left=27, top=49, right=43, bottom=24),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(  # width é o teto: em janelas mais estreitas o conteúdo encolhe junto
                    width=BATTLE_CONTENT_WIDTH,
                    content=ft.Column(spacing=6, controls=[top_bar, map_banner(map_data), ft.Container(height=7), panels]),
                ),
            ],
        ),
    )


def build_map_page(map_id: str):
    @ft.component
    def _map_page():
        collapsed, set_collapsed = ft.use_state(True)
        map_data, set_map_data = ft.use_state(cast("dict | None", None))
        loading, set_loading = ft.use_state(True)

        def on_mount():
            async def fetch():
                try:
                    set_map_data(await MapService.get_map(map_id))
                except ApiError as e:
                    print(f"Failed to load map: {e.detail}")
                finally:
                    set_loading(False)

            ft.context.page.run_task(fetch)
            return None

        ft.use_effect(on_mount, [])

        def toggle_sidebar(e):
            set_collapsed(not collapsed)

        character = get_current_character()

        if character is None:
            content = ft.Container(
                expand=True, alignment=ft.Alignment.CENTER,
                content=ft.Text("No character selected", color=t.NORMAL_TEXT, font_family="Cinzel"),
            )
        elif loading:
            content = ft.Container(expand=True, alignment=ft.Alignment.CENTER,
                                   content=ft.ProgressRing())
        elif map_data is None:
            content = ft.Container(
                expand=True, alignment=ft.Alignment.CENTER,
                content=ft.Text(f"Map '{map_id}' not found", color=t.NORMAL_TEXT, font_family="Cinzel"),
            )
        else:
            content = map_screen(map_data, character)

        return ft.Container(
            expand=True,
            bgcolor=t.BACKGROUND_OPACITY,
            content=ft.Row(
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[sidebar(collapsed, toggle_sidebar), content],
            ),
        )

    return _map_page
