from services.api_client import api


API_PREFIX = "/api/v1/characters"

BAG_ROWS = 8
BAG_COLUMNS = 5
BAG_SIZE = BAG_ROWS * BAG_COLUMNS

# equipment slot -> item equip types it accepts (mirror of backend/core/inventory_rules.py EQUIP_SLOTS)
EQUIP_SLOTS = {
    "head": {"head"},
    "armor": {"armor"},
    "right_hand": {"weapon"},
    "left_hand": {"weapon", "shield"},
    "garment": {"garment"},
    "shoes": {"shoes"},
    "accessory_1": {"accessory"},
    "accessory_2": {"accessory"},
}


def bag_slot(index: int) -> str:
    return f"bag_{index}"


def can_hold(slot: str, item: dict | None) -> bool:
    """Whether the item may sit in the slot (None = nothing, always fine); bag slots take anything"""
    if item is None or slot not in EQUIP_SLOTS:
        return True
    return item.get("equip_type") in EQUIP_SLOTS[slot]


def move_entries(entries: list[dict], from_slot: str, to_slot: str) -> list[dict] | None:
    """Local copy of the move the backend makes: the item in from_slot goes to to_slot and an item already there
    swaps places with it. Returns the new list, or None when the move is not allowed"""
    by_slot = {entry["slot"]: entry for entry in entries}
    moving, other = by_slot.get(from_slot), by_slot.get(to_slot)
    if moving is None or from_slot == to_slot:
        return None
    if not can_hold(to_slot, moving["item"]) or not can_hold(from_slot, other["item"] if other else None):
        return None
    result = []
    for entry in entries:
        if entry is moving:
            entry = {**entry, "slot": to_slot}
        elif entry is other:
            entry = {**entry, "slot": from_slot}
        result.append(entry)
    return result


class InventoryService:
    """Handles inventory-related API calls"""

    @staticmethod
    async def get_inventory(character_id: int) -> list[dict]:
        """Every item the character carries: [{"id", "slot", "amount", "item": {...}}]"""
        return await api.get(f"{API_PREFIX}/{character_id}/inventory")

    @staticmethod
    async def move_item(character_id: int, from_slot: str, to_slot: str) -> list[dict]:
        """Moves (or swaps) an item between slots; returns the whole inventory as saved"""
        return await api.post(f"{API_PREFIX}/{character_id}/inventory/move",
                              json={"from_slot": from_slot, "to_slot": to_slot})
