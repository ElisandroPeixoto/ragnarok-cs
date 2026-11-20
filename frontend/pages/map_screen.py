import flet as ft
import themes as t
from components.sidebar import sidebar
from components.item_card import item_card
from components.sheet_sprite import monster_sprite
from services.session_state import get_current_character, pop_battle_result
from components.battle_result_dialog import battle_result_dialog
from services.map_service import MapService
from services.api_client import ApiError
from services.sprite_selector import badge_selector
from typing import cast
from services.map_router_manager import map_route, navigate_to_battle, change_place
from services.battle_service import BattleService
from services import map_zoom
from pages.battle_page import CONTENT_WIDTH as BATTLE_CONTENT_WIDTH


# Left column, fixed size in every map: the title card on top, the town map below it and, in maps with monsters, the
# "Monsters nearby" card under the map. The town map is 4:3 so the whole image fits without cropping and the
# markers' x/y (fractions) land right.
LEFT_WIDTH = 800
TITLE_HEIGHT = 64
MONSTERS_HEIGHT = 176
TOWN_HEIGHT = LEFT_WIDTH * 3 // 4
TOWN_BORDER = 1
VIEW_WIDTH = LEFT_WIDTH - 2 * TOWN_BORDER      # the town map's viewport (inside its border)
VIEW_HEIGHT = TOWN_HEIGHT - 2 * TOWN_BORDER
TOP_HEIGHT = TITLE_HEIGHT + 16 + TOWN_HEIGHT   # title + town map; the right column is as tall as the left one
FRAME_RADIUS = 8
MARKER_SLOT_WIDTH = 160   # markers are centered on their x/y inside a slot this wide
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

# MapModel.zone -> (label, icon, color). Only safe zones are labeled: any other zone shows nothing
ZONES = {
    "safe": ("Safe Zone", ft.Icons.GPP_GOOD, t.MAP_ZONE_SAFE),
}


def cinzel(value: str, size: float, color: str = t.NORMAL_TEXT, **kwargs) -> ft.Text:
    return ft.Text(value, size=size, color=color, font_family="Cinzel", **kwargs)


def place_icon(place: dict):
    return PLACE_ICONS.get(place.get("icon"), DEFAULT_PLACE_ICON)


def zone_tag(zone: str, size: float = 11) -> ft.Control | None:
    """Shield + "Safe Zone" in green; None for zones that have no label (everything but safe)."""
    if zone not in ZONES:
        return None
    label, icon, color = ZONES[zone]
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
    zone_label = zone_tag(zone, 12)
    zone_pill = ft.Container(
        padding=ft.Padding.symmetric(horizontal=12, vertical=6), border_radius=6, bgcolor=t.MAP_MARKER_BG,
        content=zone_label,
    ) if zone_label else None
    return ft.Column(spacing=8, controls=[
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.END,
               controls=[ft.Column(spacing=4, controls=[identity, ft.Column(spacing=0, controls=stats)]),
                         *([zone_pill] if zone_pill else [])]),
        ft.Divider(height=1, thickness=1, color=t.MAP_DIVIDER),
    ])


# ---------- map image with place markers ----------

def place_marker(place: dict, selected: bool, on_click, view: map_zoom.View):
    """Pill with icon + name, centered on the place's x/y over the (zoomed) town map. The pill never scales."""
    color = t.MAP_SELECTED if selected else t.NORMAL_TEXT
    pill = ft.Container(
        padding=ft.Padding.symmetric(horizontal=8), height=MARKER_HEIGHT, border_radius=MARKER_HEIGHT / 2,
        bgcolor=t.MAP_MARKER_BG, border=ft.Border.all(1, t.MAP_SELECTED if selected else t.MAP_MARKER_BORDER),
        on_click=lambda e: on_click(place), tooltip=place["name"],
        content=ft.Row(spacing=4, tight=True, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Icon(place_icon(place), size=13, color=color), cinzel(place["name"], 11, color),
        ]),
    )
    center_x, center_y = map_zoom.to_viewport(view, place["x"], place["y"], VIEW_WIDTH, VIEW_HEIGHT)
    if not (-20 <= center_x <= VIEW_WIDTH + 20 and -20 <= center_y <= VIEW_HEIGHT + 20):
        return None   # zoomed out of sight
    return ft.Container(
        left=center_x - MARKER_SLOT_WIDTH / 2, top=center_y - MARKER_HEIGHT / 2,
        width=MARKER_SLOT_WIDTH, height=MARKER_HEIGHT, alignment=ft.Alignment.CENTER,
        content=pill,
    )


def title_card(map_data: dict):
    """The map's name and recommended level, in a card on top of the town map."""
    return ft.Container(
        width=LEFT_WIDTH, height=TITLE_HEIGHT, bgcolor=t.MAP_SECTION_BG, border=ft.Border.all(1, t.MAP_PANEL_BORDER),
        border_radius=FRAME_RADIUS, padding=ft.Padding.symmetric(horizontal=18), alignment=ft.Alignment.CENTER_LEFT,
        content=ft.Column(spacing=1, tight=True, controls=[
            cinzel(map_data["name"], 24, t.MAP_TITLE_TEXT, weight=ft.FontWeight.BOLD),
            cinzel(f"Recommended Level: {map_data.get('level_range', '-')}", 12, t.MAP_LIGHT_TEXT),
        ]),
    )


def zoom_button(icon, tooltip: str, on_click):
    return ft.Container(
        width=30, height=30, border_radius=15, bgcolor=t.MAP_MARKER_BG, border=ft.Border.all(1, t.MAP_MARKER_BORDER),
        alignment=ft.Alignment.CENTER, tooltip=tooltip, on_click=on_click,
        content=ft.Icon(icon, size=18, color=t.NORMAL_TEXT),
    )


def town_frame(map_data: dict, show_places: bool, is_selected, on_place_click, on_toggle_places,
               view: map_zoom.View, on_zoom, on_pan, on_reset_view):
    """The town map with the clickable place markers, which can be zoomed (wheel or +/-) and dragged. A map with no
    town image gets an empty square. on_zoom(factor, x, y) zooms around a viewport pixel; on_pan(dx, dy) drags."""
    frame = dict(width=LEFT_WIDTH, height=TOWN_HEIGHT, border=ft.Border.all(TOWN_BORDER, t.MAP_SECTION_BORDER),
                 border_radius=FRAME_RADIUS)
    town_image = map_data.get("town_image")
    if not town_image:
        return ft.Container(bgcolor=t.MAP_SECTION_BG, **frame)

    left, top, width, height = map_zoom.image_rect(view, VIEW_WIDTH, VIEW_HEIGHT)
    markers = [place_marker(place, is_selected(place), on_place_click, view)
               for place in map_data.get("places", [])] if show_places else []
    surface = ft.GestureDetector(
        on_scroll=lambda e: on_zoom(map_zoom.WHEEL_STEP if scroll_amount(e) < 0 else 1 / map_zoom.WHEEL_STEP,
                                    e.local_position.x, e.local_position.y),
        on_pan_update=lambda e: on_pan(e.local_delta.x, e.local_delta.y),
        content=ft.Stack(width=VIEW_WIDTH, height=VIEW_HEIGHT, controls=[
            ft.Image(src=town_image, fit=ft.BoxFit.FILL, left=left, top=top, width=width, height=height,
                     filter_quality=ft.FilterQuality.MEDIUM),
            *[marker for marker in markers if marker is not None],
        ]),
    )
    center = (VIEW_WIDTH / 2, VIEW_HEIGHT / 2)
    controls_box = ft.Container(right=10, top=10, content=ft.Column(
        spacing=6, horizontal_alignment=ft.CrossAxisAlignment.END, controls=[
            view_places_button(show_places, on_toggle_places),
            ft.Row(spacing=6, tight=True, controls=[
                zoom_button(ft.Icons.REMOVE, "Zoom out", lambda e: on_zoom(1 / map_zoom.BUTTON_STEP, *center)),
                zoom_button(ft.Icons.ADD, "Zoom in", lambda e: on_zoom(map_zoom.BUTTON_STEP, *center)),
                zoom_button(ft.Icons.FIT_SCREEN, "Reset zoom", lambda e: on_reset_view()),
            ]),
        ]))
    return ft.Container(
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS, **frame,
        content=ft.Stack(expand=True, controls=[surface, controls_box]),
    )


def scroll_amount(event) -> float:
    """Vertical amount of a mouse wheel event (negative = wheel up = zoom in)."""
    delta = event.scroll_delta
    return getattr(delta, "y", delta)


def view_places_button(show_places: bool, on_toggle):
    """Small pill over the town map: shows or hides the place markers."""
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=5), border_radius=14, on_click=on_toggle,
        bgcolor=t.MAP_MARKER_BG, border=ft.Border.all(1, t.MAP_MARKER_BORDER),
        content=ft.Row(spacing=6, tight=True, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Icon(ft.Icons.VISIBILITY_OFF_OUTLINED if show_places else ft.Icons.VISIBILITY_OUTLINED,
                    size=16, color=t.NORMAL_TEXT),
            cinzel("Hide Places" if show_places else "View Places", 11),
        ]),
    )


# ---------- sections ----------

def section(title: str, icon, content: ft.Control, expand: int | None = None, scroll: bool = False,
            height: int | None = None):
    """Dark card with an icon + title, a divider and the content below. With `expand` it fills its share of the
    parent's height, and `scroll` lets a long content scroll inside the card."""
    body = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[content]) if scroll else content
    return ft.Container(
        expand=expand, height=height, bgcolor=t.MAP_SECTION_BG, border=ft.Border.all(1, t.MAP_SECTION_BORDER), border_radius=FRAME_RADIUS,
        padding=ft.Padding(left=20, top=14, right=20, bottom=18),
        content=ft.Column(spacing=10, controls=[
            ft.Row(spacing=8, controls=[ft.Icon(icon, size=22, color=t.NORMAL_TEXT), cinzel(title, 18)]),
            ft.Divider(height=1, thickness=1, color=t.MAP_DIVIDER),
            body,
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
        padding=ft.Padding.symmetric(horizontal=12, vertical=3.6), border_radius=4.8,
        border=ft.Border.all(1.2, t.MAP_MARKER_BORDER), tooltip="Coming soon", on_click=lambda e: None,
        content=cinzel("Talk", 13),
    )


def npc_card(npc: dict):
    return ft.Container(
        width=252, height=127, padding=9.6, border_radius=7.2, border=ft.Border.all(1.2, t.MAP_SECTION_BORDER),
        content=ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Image(src=npc["image"], width=55, height=106, fit=ft.BoxFit.CONTAIN),
            ft.Column(expand=True, spacing=4.8, alignment=ft.MainAxisAlignment.CENTER, controls=[
                cinzel(npc["name"], 18),
                cinzel(npc.get("greeting", ""), 10.8, t.MAP_MUTED_TEXT, max_lines=3,
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
    zone_label = zone_tag(route["zone"]) if route.get("zone") else None
    if zone_label:
        tags.append(zone_label)
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
        elif place["kind"] == "exit":   # the map behind it does not exist yet: listed, without the travel arrow
            routes.append({"key": place["id"], "name": place["name"], "detail": place.get("direction"), "map_id": None})
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
    """The map's monsters and the Hunt button, in a card of fixed height under the town map."""
    return section("Monsters nearby", ft.Icons.PETS, ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(expand=True, wrap=True, spacing=10, run_spacing=10, controls=[monster_card(m) for m in monsters]),
            hunt_button(map_id, character),
        ],
    ), height=MONSTERS_HEIGHT, scroll=True)


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
    view, set_view = ft.use_state(map_zoom.DEFAULT_VIEW)   # town map zoom: (zoom, center x, center y)

    def show_battle_result():
        """Back from a battle: pop up with Victory!/Defeat and the damage report (shown once)."""
        result = pop_battle_result()
        if result:
            ft.context.page.show_dialog(battle_result_dialog(result, lambda e: ft.context.page.pop_dialog()))

    ft.use_effect(show_battle_result, [])

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

    def zoom_map(factor: float, x: float, y: float):
        set_view(lambda current: map_zoom.zoom_at(current, factor, x, y, VIEW_WIDTH, VIEW_HEIGHT))

    def pan_map(dx: float, dy: float):
        set_view(lambda current: map_zoom.pan(current, dx, dy, VIEW_WIDTH, VIEW_HEIGHT))

    def travel(route: dict):
        change_place(character, route["map_id"])

    routes_content = (ft.Column(spacing=10, controls=[
        route_card(route, route["key"] == selected_route_key,
                   lambda route: set_selected_route_key(route["key"]), travel)
        for route in routes]) if routes else cinzel("No routes available", 12, t.MAP_MUTED_TEXT))

    # left: the title card, the town map and (maps with monsters) "Monsters nearby" under it;
    # right: "In the area" and "Routes", as tall as the left column
    monsters = map_data.get("monsters", [])
    left_controls = [
        title_card(map_data),
        town_frame(map_data, show_places, is_selected, select_place, lambda e: set_show_places(not show_places),
                   view, zoom_map, pan_map, lambda: set_view(map_zoom.DEFAULT_VIEW)),
    ]
    main_height = TOP_HEIGHT
    if monsters:
        left_controls.append(monsters_nearby(map_data["id"], monsters, character))
        main_height += GAP + MONSTERS_HEIGHT
    left_column = ft.Column(width=LEFT_WIDTH, spacing=GAP, controls=left_controls)
    right_column = ft.Container(expand=True, height=main_height, content=ft.Column(spacing=GAP, expand=True, controls=[
        section("In the area", ft.Icons.EXPLORE_OUTLINED,
                in_the_area_content(areas, npcs, selected_area_id, select_place), expand=1, scroll=True),
        section("Routes", ft.Icons.ROUTE, routes_content, expand=1, scroll=True),
    ]))
    main_row = ft.Row(spacing=GAP, vertical_alignment=ft.CrossAxisAlignment.START, controls=[left_column, right_column])

    body = [header(character, map_data.get("zone", "safe")), main_row]

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

        # the map's own background picture (maps.background_image), faded behind the screen
        background = map_data.get("background_image") if map_data else None
        background_layer = ft.Container(
            expand=True,
            opacity=0.15,
            image=ft.DecorationImage(src=background, fit=ft.BoxFit.COVER) if background else None,
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
