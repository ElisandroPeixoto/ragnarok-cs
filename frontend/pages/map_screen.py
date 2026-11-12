import flet as ft
import themes as t
from components.sidebar import sidebar
from components.item_card import item_card
from components.sheet_sprite import monster_sprite
from services.session_state import get_current_character
from services.map_service import MapService
from services.api_client import ApiError
from services.sprite_selector import badge_selector
from typing import cast
from services.map_router_manager import map_route, navigate_to_battle, change_place
from services.battle_service import BattleService
from pages.battle_page import CONTENT_WIDTH as BATTLE_CONTENT_WIDTH


# Every map image is drawn at this fixed size (map art is 1358x784)
MAP_IMAGE_WIDTH = 800
MAP_IMAGE_HEIGHT = round(MAP_IMAGE_WIDTH * 784 / 1358)
MARKER_SLOT_WIDTH = 180   # markers are centered on their x/y inside a slot this wide
MARKER_HEIGHT = 24
GAP = 16

# Place icon keys (MapPlaceModel.icon) -> Flet icons. TODO: swap for the project's own PNG/SVG icons
PLACE_ICONS = {
    "square": ft.Icons.PARK_OUTLINED,
    "port": ft.Icons.ANCHOR,
    "house": ft.Icons.HOME_OUTLINED,
    "building": ft.Icons.LOCATION_ON_OUTLINED,
    "exit": ft.Icons.LOCATION_ON_OUTLINED,
    "training": ft.Icons.SPORTS_MARTIAL_ARTS,
}
DEFAULT_PLACE_ICON = ft.Icons.PLACE_OUTLINED

# MapModel.zone -> (label, icon, color)
ZONES = {
    "safe": ("Safe Zone", ft.Icons.GPP_GOOD, t.MAP_ZONE_SAFE),
    "hostile_passive": ("Hostile Area (Passive)", ft.Icons.PRIORITY_HIGH, t.MAP_ZONE_HOSTILE),
    "hostile_aggressive": ("Hostile Area (Aggressive)", ft.Icons.PRIORITY_HIGH, t.MAP_ZONE_HOSTILE),
}


def cinzel(value: str, size: float, color: str = t.NORMAL_TEXT, **kwargs) -> ft.Text:
    return ft.Text(value, size=size, color=color, font_family="Cinzel", **kwargs)


def place_icon(place: dict):
    return PLACE_ICONS.get(place.get("icon"), DEFAULT_PLACE_ICON)


def zone_tag(zone: str, size: float = 11):
    """Shield + "Safe Zone" in green, or "!" + "Hostile Area (...)" in red."""
    label, icon, color = ZONES.get(zone, ZONES["safe"])
    return ft.Row(spacing=2, tight=True, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
        ft.Icon(icon, size=size + 3, color=color), cinzel(label, size, color),
    ])


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


# ---------- header ----------

def header(character: dict, zone: str):
    """Character avatar, name and zeny, job/level and HP on the left; the map's zone on the right.
    The API sends zeny as a decimal string (e.g. "0.00"), shown here as a whole number."""
    badge = badge_selector(character["job"])
    avatar = ft.Container(
        width=40, height=40, border_radius=4, bgcolor=t.PLACEHOLDER_BACKGROUND_COLOR,
        border=ft.Border.all(1, t.MAP_SECTION_BORDER),
        image=ft.DecorationImage(src=badge, fit=ft.BoxFit.COVER) if badge else None,
    )
    identity = ft.Row(spacing=8, controls=[
        avatar,
        ft.Column(spacing=0, controls=[
            cinzel(character["name"], 15),
            ft.Row(spacing=4, controls=[ft.Image(src="icons/zeny.png", width=11, height=12),
                                        cinzel(f"{int(float(character.get('zeny') or 0))} z", 11, t.MAP_LEVEL_TEXT)]),
        ]),
    ])
    stats = [cinzel(f"{character['job']} - Lv: {character.get('level', 1)}", 11),
             cinzel(f"HP: {character.get('hp', 0)}/{character.get('max_hp', 0)}", 11)]
    zone_pill = ft.Container(
        padding=ft.Padding.symmetric(horizontal=12, vertical=6), border_radius=6, bgcolor=t.MAP_MARKER_BG,
        content=zone_tag(zone, 12),
    )
    return ft.Column(spacing=8, controls=[
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.END,
               controls=[ft.Column(spacing=4, controls=[identity, ft.Column(spacing=0, controls=stats)]), zone_pill]),
        ft.Divider(height=1, thickness=1, color=t.MAP_DIVIDER),
    ])


# ---------- map image with place markers ----------

def place_marker(place: dict, selected: bool, on_click):
    """Pill with icon + name, centered on the place's x/y over the map image."""
    color = t.MAP_SELECTED if selected else t.NORMAL_TEXT
    pill = ft.Container(
        padding=ft.Padding.symmetric(horizontal=8), height=MARKER_HEIGHT, border_radius=MARKER_HEIGHT / 2,
        bgcolor=t.MAP_MARKER_BG, border=ft.Border.all(1, t.MAP_SELECTED if selected else t.MAP_MARKER_BORDER),
        on_click=lambda e: on_click(place), tooltip=place["name"],
        content=ft.Row(spacing=4, tight=True, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Icon(place_icon(place), size=13, color=color), cinzel(place["name"], 11, color),
        ]),
    )
    return ft.Container(
        left=place["x"] * MAP_IMAGE_WIDTH - MARKER_SLOT_WIDTH / 2,
        top=place["y"] * MAP_IMAGE_HEIGHT - MARKER_HEIGHT / 2,
        width=MARKER_SLOT_WIDTH, height=MARKER_HEIGHT, alignment=ft.Alignment.CENTER,
        content=pill,
    )


def map_frame(map_data: dict, show_places: bool, is_selected, on_place_click):
    title_box = ft.Container(
        left=0, top=0, bgcolor=t.MAP_TITLE_OVERLAY,
        border_radius=ft.BorderRadius.only(bottom_right=10),
        padding=ft.Padding(left=14, top=8, right=18, bottom=10),
        content=ft.Column(spacing=2, controls=[
            cinzel(map_data["name"], 26, t.MAP_TITLE_TEXT, weight=ft.FontWeight.BOLD),
            cinzel(f"Recommended Level: {map_data.get('level_range', '-')}", 13, t.MAP_LIGHT_TEXT),
        ]),
    )
    markers = [place_marker(place, is_selected(place), on_place_click)
               for place in map_data.get("places", [])] if show_places else []
    return ft.Container(
        border=ft.Border.all(2, t.MAP_PANEL_BORDER),
        content=ft.Stack(width=MAP_IMAGE_WIDTH, height=MAP_IMAGE_HEIGHT, controls=[
            ft.Image(src=map_data.get("image", ""), width=MAP_IMAGE_WIDTH, height=MAP_IMAGE_HEIGHT,
                     fit=ft.BoxFit.COVER),
            title_box,
            *markers,
        ]),
    )


def view_places_button(show_places: bool, on_toggle):
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=6, vertical=4), border_radius=4, on_click=on_toggle,
        content=ft.Row(spacing=6, tight=True, controls=[
            ft.Icon(ft.Icons.VISIBILITY_OFF_OUTLINED if show_places else ft.Icons.VISIBILITY_OUTLINED,
                    size=20, color=t.NORMAL_TEXT),
            cinzel("Hide Places" if show_places else "View Places", 12),
        ]),
    )


# ---------- sections ----------

def section(title: str, icon, content: ft.Control, expand: int | None = None):
    """Dark card with an icon + title, a divider and the content below."""
    return ft.Container(
        expand=expand, bgcolor=t.MAP_SECTION_BG, border=ft.Border.all(1, t.MAP_SECTION_BORDER), border_radius=6,
        padding=ft.Padding(left=20, top=14, right=20, bottom=18),
        content=ft.Column(spacing=10, controls=[
            ft.Row(spacing=8, controls=[ft.Icon(icon, size=22, color=t.NORMAL_TEXT), cinzel(title, 18)]),
            ft.Divider(height=1, thickness=1, color=t.MAP_DIVIDER),
            content,
        ]),
    )


def area_chip(place: dict, selected: bool, on_click):
    color = t.MAP_SELECTED if selected else t.NORMAL_TEXT
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=8, vertical=4), border_radius=4,
        border=ft.Border.all(1, t.MAP_SELECTED if selected else t.MAP_MARKER_BORDER),
        on_click=lambda e: on_click(place),
        content=ft.Row(spacing=4, tight=True, controls=[
            ft.Icon(place_icon(place), size=13, color=color), cinzel(place["name"], 11, color),
        ]),
    )


def talk_button():
    return ft.Container(  # TODO: open the NPC's dialogue
        padding=ft.Padding.symmetric(horizontal=10, vertical=3), border_radius=4,
        border=ft.Border.all(1, t.MAP_MARKER_BORDER), tooltip="Coming soon", on_click=lambda e: None,
        content=cinzel("Talk", 11),
    )


def npc_card(npc: dict):
    return ft.Container(
        width=210, height=106, padding=8, border_radius=6, border=ft.Border.all(1, t.MAP_SECTION_BORDER),
        content=ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Image(src=npc["image"], width=46, height=88, fit=ft.BoxFit.CONTAIN),
            ft.Column(expand=True, spacing=4, alignment=ft.MainAxisAlignment.CENTER, controls=[
                cinzel(npc["name"], 15),
                cinzel(npc.get("greeting", ""), 9, t.MAP_MUTED_TEXT, max_lines=3,
                       overflow=ft.TextOverflow.ELLIPSIS),
                ft.Row(controls=[talk_button()]),
            ]),
        ]),
    )


def in_the_area_content(areas: list, npcs: list, selected_area_id, on_area_click):
    if not areas:
        return cinzel("Nothing to see here", 12, t.MAP_MUTED_TEXT)
    here = [npc for npc in npcs if npc.get("place_id") == selected_area_id]
    people = (ft.Row(wrap=True, spacing=10, run_spacing=10, controls=[npc_card(npc) for npc in here])
              if here else cinzel("No one around", 12, t.MAP_MUTED_TEXT))
    return ft.Column(spacing=14, controls=[
        ft.Row(wrap=True, spacing=6, run_spacing=6,
               controls=[area_chip(area, area["id"] == selected_area_id, on_area_click) for area in areas]),
        people,
    ])


def route_card(route: dict, selected: bool, on_select, on_travel):
    """route = {"key", "name", "level_range", "zone", "detail", "map_id"}; map_id None = no link yet."""
    tags = []
    if route.get("level_range"):
        tags.append(cinzel(f"Lv {route['level_range'].replace(' ', '')}", 11, t.MAP_LEVEL_TEXT))
    if route.get("zone"):
        tags.append(zone_tag(route["zone"]))
    info = ft.Column(expand=True, spacing=4, controls=[
        cinzel(route["name"], 16),
        ft.Row(spacing=14, controls=tags),
        ft.Container(height=4),
        cinzel(route.get("detail") or "", 11, t.MAP_MUTED_TEXT),
    ])
    controls = [info]
    if route.get("map_id"):
        controls.append(ft.Container(
            width=36, height=36, border_radius=4, border=ft.Border.all(1, t.MAP_MARKER_BORDER),
            alignment=ft.Alignment.CENTER, tooltip=f"Go to {route['name']}", on_click=lambda e: on_travel(route),
            content=ft.Icon(ft.Icons.NORTH_EAST, size=20, color=t.NORMAL_TEXT),
        ))
    return ft.Container(
        padding=ft.Padding(left=16, top=10, right=18, bottom=10), border_radius=6,
        border=ft.Border.all(1, t.MAP_SELECTED if selected else t.MAP_SECTION_BORDER),
        on_click=lambda e: on_select(route),
        content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=controls),
    )


def build_routes(map_data: dict) -> list[dict]:
    """Exits (to other maps) first, then buildings; connections without an exit marker go last."""
    places = map_data.get("places", [])
    routes = []
    for place in places:
        target = place.get("target")
        if place["kind"] == "exit" and target:
            routes.append({"key": place["id"], "name": target["name"], "level_range": target["level_range"],
                           "zone": target["zone"], "detail": place.get("direction"), "map_id": target["map_id"]})
    linked = {route["map_id"] for route in routes}
    for place in places:
        if place["kind"] == "building":   # buildings are safe; entering them comes later
            routes.append({"key": place["id"], "name": place["name"], "zone": "safe", "detail": "Building"})
    for connection in map_data.get("navigation", []):
        if connection["map_id"] not in linked:
            routes.append({"key": f"map:{connection['map_id']}", "name": connection["name"],
                           "level_range": connection.get("level_range"), "map_id": connection["map_id"]})
    return routes


def monster_card(monster: dict):
    spawn_rate = monster.get("spawn_rate")
    return item_card(monster_sprite(monster["sheet"], width=51, height=64), monster["name"],
                     subtitle=f"{spawn_rate}%" if spawn_rate is not None else None, width=180, height=84)


def monsters_nearby(map_id: str, monsters: list, character: dict):
    return section("Monsters nearby", ft.Icons.PETS, ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(expand=True, wrap=True, spacing=10, run_spacing=10, controls=[monster_card(m) for m in monsters]),
            hunt_button(map_id, character),
        ],
    ))


# ---------- page ----------

def default_area_id(areas: list, npcs: list):
    """The first area with someone in it, else the first area."""
    occupied = {npc.get("place_id") for npc in npcs}
    for area in areas:
        if area["id"] in occupied:
            return area["id"]
    return areas[0]["id"] if areas else None


@ft.component
def map_screen(map_data: dict, character: dict):
    places = map_data.get("places", [])
    npcs = map_data.get("npcs", [])
    areas = [place for place in places if place["kind"] == "area"]
    routes = build_routes(map_data)

    show_places, set_show_places = ft.use_state(True)
    selected_area_id, set_selected_area_id = ft.use_state(lambda: default_area_id(areas, npcs))
    selected_route_key, set_selected_route_key = ft.use_state(cast("int | str | None", None))

    def select_place(place: dict):
        """Markers and chips: an area shows its NPCs below; an exit or building highlights its route."""
        if place["kind"] == "area":
            set_selected_area_id(place["id"])
        else:
            set_selected_route_key(place["id"])

    def is_selected(place: dict) -> bool:
        if place["kind"] == "area":
            return place["id"] == selected_area_id
        return place["id"] == selected_route_key

    def travel(route: dict):
        change_place(character, route["map_id"])

    map_row = ft.Row(spacing=GAP, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
        map_frame(map_data, show_places, is_selected, select_place),
        view_places_button(show_places, lambda e: set_show_places(not show_places)),
    ])

    routes_content = (ft.Column(spacing=10, controls=[
        route_card(route, route["key"] == selected_route_key,
                   lambda route: set_selected_route_key(route["key"]), travel)
        for route in routes]) if routes else cinzel("No routes available", 12, t.MAP_MUTED_TEXT))

    sections = ft.Row(spacing=GAP, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
        section("In the area", ft.Icons.EXPLORE_OUTLINED,
                in_the_area_content(areas, npcs, selected_area_id, select_place), expand=7),
        section("Routes", ft.Icons.ROUTE, routes_content, expand=5),
    ])

    body = [header(character, map_data.get("zone", "safe")), map_row, sections]
    monsters = map_data.get("monsters", [])
    if monsters:
        body.append(monsters_nearby(map_data["id"], monsters, character))

    return ft.Container(
        expand=True,
        padding=ft.Padding(left=24, top=24, right=24, bottom=24),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(  # width is a cap: in narrower windows the content shrinks with it
                    width=BATTLE_CONTENT_WIDTH,
                    content=ft.Column(spacing=GAP, controls=body),
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

        # TODO: placeholder - replace this battle board picture with a proper map screen background image
        background_layer = ft.Container(
            expand=True,
            opacity=0.15,
            image=ft.DecorationImage(src="battle_boards/forest_battlefield.jpg", fit=ft.BoxFit.COVER),
        )

        return ft.Container(
            expand=True,
            bgcolor=t.BACKGROUND_OPACITY,
            content=ft.Stack(
                expand=True,
                controls=[
                    background_layer,
                    ft.Row(
                        expand=True,
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[sidebar(collapsed, toggle_sidebar), content],
                    ),
                ],
            ),
        )

    return _map_page
