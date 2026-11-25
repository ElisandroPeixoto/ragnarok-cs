"""Inventory rules (docs/inventario.md): the bag's size, the equipment slots and which items each slot takes"""

BAG_ROWS = 8
BAG_COLUMNS = 5
BAG_SIZE = BAG_ROWS * BAG_COLUMNS

# equipment slot of the character -> item equip types it accepts (ItemModel.equip_type)
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

# items every new character starts with: (item id, amount)
STARTER_ITEMS = [("knife", 1), ("cotton_shirt", 1), ("red_potion", 5)]


def bag_slot(index: int) -> str:
    return f"bag_{index}"


def is_valid_slot(slot: str) -> bool:
    if slot in EQUIP_SLOTS:
        return True
    if slot.startswith("bag_") and slot[4:].isdigit():
        return 0 <= int(slot[4:]) < BAG_SIZE
    return False


def can_hold(slot: str, equip_type: str | None) -> bool:
    """Whether an item with this equip type (None = not equippable) may sit in the slot; bag slots take anything"""
    if slot in EQUIP_SLOTS:
        return equip_type in EQUIP_SLOTS[slot]
    return is_valid_slot(slot)
