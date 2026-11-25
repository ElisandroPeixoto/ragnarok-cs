import flet as ft
import themes as t
from components.sidebar import sidebar
from components.zeny_badge import zeny_badge
from components.job_sprite import job_sprite
from services.session_state import get_current_character
from services.api_client import ApiError
from services.inventory_service import InventoryService, BAG_ROWS, BAG_COLUMNS, bag_slot, move_entries
from pages.battle_page import CONTENT_WIDTH
from typing import cast


SLOT_SIZE = 64
SLOT_GAP = 6
PANEL_PADDING = 20
PANEL_GAP = 16
BAG_WIDTH = BAG_COLUMNS * SLOT_SIZE + (BAG_COLUMNS - 1) * SLOT_GAP + 2 * PANEL_PADDING
# the equipment panel takes 80% of the width left beside the bag
EQUIPMENT_WIDTH = round((CONTENT_WIDTH - BAG_WIDTH - PANEL_GAP) * 0.8)
SPRITE_HEIGHT = 190   # same size as the character on the profile (profile_page.character_card)
DRAG_GROUP = "inventory"

# equipment slots around the sprite: (slot, label). The character faces the viewer, so the right hand is on the left
EQUIP_LEFT = [("head", "Head"), ("armor", "Armor"), ("right_hand", "Right Hand"), ("accessory_1", "Accessory 1")]
EQUIP_RIGHT = [("garment", "Garment"), ("shoes", "Shoes"), ("left_hand", "Left Hand"), ("accessory_2", "Accessory 2")]

# generic icon for items without art (ItemModel.icon is NULL)
EQUIP_TYPE_ICONS = {
    "head": ft.Icons.FACE, "armor": ft.Icons.CHECKROOM, "weapon": ft.Icons.HARDWARE, "shield": ft.Icons.SHIELD,
    "garment": ft.Icons.DRY_CLEANING, "shoes": ft.Icons.DIRECTIONS_WALK, "accessory": ft.Icons.DIAMOND,
}
KIND_ICONS = {"usable": ft.Icons.LOCAL_DRINK, "etc": ft.Icons.INVENTORY_2}


def item_icon(item: dict, size: int):
    if item.get("icon"):
        return ft.Image(src=item["icon"], width=size, height=size, fit=ft.BoxFit.CONTAIN)
    icon = EQUIP_TYPE_ICONS.get(item.get("equip_type")) or KIND_ICONS.get(item.get("kind"), ft.Icons.INVENTORY_2)
    return ft.Icon(icon, size=size, color=t.TITLE_TEXT)


def item_tile(entry: dict, opacity: float = 1.0):
    """The item drawn inside a slot: its icon and, for stacks, the amount in the corner"""
    controls = [ft.Container(width=SLOT_SIZE, height=SLOT_SIZE, alignment=ft.Alignment.CENTER,
                             content=item_icon(entry["item"], 36))]
    if entry["amount"] > 1:
        controls.append(ft.Container(right=5, bottom=3,
                                     content=ft.Text(str(entry["amount"]), size=12, color=t.NORMAL_TEXT,
                                                     weight=ft.FontWeight.BOLD)))
    return ft.Container(width=SLOT_SIZE, height=SLOT_SIZE, opacity=opacity, content=ft.Stack(controls=controls))


def slot_box(content: ft.Control | None = None):
    return ft.Container(width=SLOT_SIZE, height=SLOT_SIZE,
                        bgcolor=t.PANEL_INNER_BG,
                        border=ft.Border.all(1, t.MAP_SECTION_BORDER),
                        border_radius=6,
                        content=content)


def item_tooltip(entry: dict) -> str:
    item = entry["item"]
    text = item["name"] + (f" x{entry['amount']}" if entry["amount"] > 1 else "")
    if item.get("description"):
        text += "\n" + item["description"]
    return text


def item_slot(slot: str, entry: dict | None, on_drop):
    """A slot that accepts drops; when it holds an item, the item can be dragged to another slot"""
    if entry is None:
        inner = slot_box()
    else:
        inner = ft.Draggable(group=DRAG_GROUP,
                             data=slot,
                             content=slot_box(item_tile(entry)),
                             content_when_dragging=slot_box(item_tile(entry, opacity=0.3)),
                             content_feedback=item_tile(entry, opacity=0.85),
                             tooltip=item_tooltip(entry))

    def accept(e: ft.DragTargetEvent):
        from_slot = e.src.data if e.src is not None else None
        if from_slot:
            on_drop(from_slot, slot)

    return ft.DragTarget(group=DRAG_GROUP, data=slot, on_accept=accept, content=inner)


def equip_slot(slot: str, label: str, by_slot: dict, on_drop):
    # fixed width: labels of different lengths would otherwise shift the slots of a column out of line
    return ft.Column(spacing=4, width=110, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                     controls=[item_slot(slot, by_slot.get(slot), on_drop),
                               ft.Text(label, size=12, color=t.MUTED_TEXT, font_family="Cinzel")])


def panel(content: ft.Control, **kwargs):
    return ft.Container(bgcolor=t.CARD_BG, border=ft.Border.all(1, t.CARD_BORDER), border_radius=6, padding=PANEL_PADDING,
                        content=content, **kwargs)


def bag_panel(by_slot: dict, on_drop):
    """The bag: BAG_ROWS x BAG_COLUMNS slots, numbered left to right, top to bottom (bag_0 is the top left)"""
    rows = []
    for row in range(BAG_ROWS):
        slots = [bag_slot(row * BAG_COLUMNS + column) for column in range(BAG_COLUMNS)]
        rows.append(ft.Row(spacing=SLOT_GAP, tight=True,
                           controls=[item_slot(slot, by_slot.get(slot), on_drop) for slot in slots]))
    return panel(ft.Column(spacing=SLOT_GAP, tight=True, controls=rows))


def equipment_panel(character: dict, by_slot: dict, on_drop):
    def side(slots):
        return ft.Column(spacing=14, controls=[equip_slot(slot, label, by_slot, on_drop) for slot, label in slots])

    return panel(width=EQUIPMENT_WIDTH,
                 content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16, controls=[
                     ft.Text("Equipment", size=16, color=t.TITLE_TEXT, font_family="Cinzel"),
                     ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[side(EQUIP_LEFT),
                                      ft.Container(width=200, alignment=ft.Alignment.CENTER,
                                                   content=job_sprite(character["job"], height=SPRITE_HEIGHT)),
                                      side(EQUIP_RIGHT)]),
                 ]))


@ft.component
def inventory_page():
    character = get_current_character()
    collapsed, set_collapsed = ft.use_state(True)
    entries, set_entries = ft.use_state(cast("list[dict]", []))
    error, set_error = ft.use_state(cast("str | None", None))

    async def load():
        if character is None:
            return
        try:
            set_entries(await InventoryService.get_inventory(character["id"]))
            set_error(None)
        except ApiError as api_error:
            set_error(f"Could not load the inventory ({api_error.status_code})")

    def on_mount():
        ft.context.page.run_task(load)
        return None

    ft.use_effect(on_mount, [])

    if character is None:
        return ft.Container(expand=True, alignment=ft.Alignment.CENTER, bgcolor=t.BACKGROUND_OPACITY,
                            content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                                ft.Text("No character selected", color=t.NORMAL_TEXT, font_family="Cinzel"),
                                ft.Button(content=ft.Text("Back to Character Selection", font_family="Cinzel"),
                                          on_click=lambda e: ft.context.page.navigate("/char_selection"))]))

    def drop(from_slot: str, to_slot: str):
        """Moves locally at once (so the drop feels instant), then saves; the backend's answer is the truth"""
        moved = move_entries(entries, from_slot, to_slot)
        if moved is None:   # not equippable there: the item stays where it was
            return
        set_entries(moved)

        async def save():
            try:
                set_entries(await InventoryService.move_item(character["id"], from_slot, to_slot))
            except ApiError:
                await load()

        ft.context.page.run_task(save)

    by_slot = {entry["slot"]: entry for entry in entries}

    header = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[ft.Text("Inventory", size=28, font_family="Cinzel", color=t.TITLE_TEXT,
                                      weight=ft.FontWeight.BOLD),
                              zeny_badge(character["zeny"])])

    body: list[ft.Control] = [header]
    if error:
        body.append(ft.Text(error, color=t.DAMAGE_TEXT, font_family="Cinzel"))
    body.append(ft.Row(spacing=PANEL_GAP, vertical_alignment=ft.CrossAxisAlignment.START,
                       controls=[bag_panel(by_slot, drop), equipment_panel(character, by_slot, drop)]))

    # same frame as the profile: maximum width, centered; narrower windows shrink it
    main_content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO,
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                             controls=[ft.Container(width=CONTENT_WIDTH,
                                                    content=ft.Column(spacing=16, controls=body))])

    return ft.Container(expand=True, bgcolor=t.BACKGROUND_OPACITY,
                        content=ft.Row(expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START,
                                       controls=[sidebar(collapsed, lambda e: set_collapsed(not collapsed)),
                                                 ft.Container(expand=True, padding=24, content=main_content)]))
