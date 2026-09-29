import flet as ft
import themes as t
from components.sidebar import sidebar
from components.zeny_badge import zeny_badge
from components.character_badge import character_badge
from components.section_panel import section_panel
from components.item_card import item_card
from services.map_router_manager import map_route
from services.session_state import get_current_character
from services.map_service import MapService
from services.api_client import ApiError
from typing import cast


def npc_item(item: dict):
    return item_card(item["image"], item["name"])


def navigation_item(item: dict):
    return item_card(item["image"], item["name"],
                     on_click=lambda e: ft.context.page.navigate(map_route(item["map_id"])), image_fit=ft.BoxFit.COVER)

def monster_item(item: dict):
    spawn_rate = item.get("spawn_rate")
    subtitle = f"{spawn_rate}%" if spawn_rate is not None else None
    return item_card(item["image"], item["name"], subtitle=subtitle, image_size=50)


def map_info_card(map_data: dict):
    return ft.Container(
        expand=True,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=6,
        padding=20,
        content=ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(map_data["name"], size=26, weight=ft.FontWeight.BOLD,
                        color=t.NORMAL_TEXT, font_family="Cinzel"),
                ft.Text(f"Level: {map_data.get('level_range', '-')}", size=14,
                        color=t.TITLE_TEXT, font_family="Cinzel"),
                ft.Container(
                    width=480,
                    height=270,  # proporção 16:9 fixa — independe da tela
                    border=ft.Border.all(1, t.BUTTON_PRIMARY),
                    border_radius=4,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    image=ft.DecorationImage(src=map_data.get("image", ""), fit=ft.BoxFit.COVER),
                ),
                ft.Text("About:", size=15, color=t.TITLE_TEXT, font_family="Cinzel", weight=ft.FontWeight.BOLD),
                ft.Text(map_data.get("about", ""), size=14, color=t.NORMAL_TEXT, font_family="Cinzel"),
            ],
        ),
    )


def map_screen(map_data: dict, character: dict):
    top_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[character_badge(character), zeny_badge(character["zeny"])],
    )

    right_column = ft.Column(
        width=320,
        spacing=16,
        controls=[
            section_panel("NPCs", map_data.get("npcs", []), "No NPCs nearby", npc_item),
            section_panel("Navigation", map_data.get("navigation", []), "No routes available", navigation_item),
            section_panel("Monsters", map_data.get("monsters", []), "There are no monsters nearby", monster_item),
        ],
    )

    body = ft.Row(
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[map_info_card(map_data), right_column],
    )

    return ft.Container(
        expand=True,
        padding=24,
        content=ft.Column(
            expand=True,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[top_bar, body],
        ),
    )


def build_map_page(map_id: str):
    @ft.component
    def _map_page():
        collapsed, set_collapsed = ft.use_state(False)
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
