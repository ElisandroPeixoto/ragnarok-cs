"""Inventory rules (docs/inventario.md): the bag's size, the equipment slots and which item types each slot takes"""

BAG_ROWS = 8
BAG_COLUMNS = 5
BAG_SIZE = BAG_ROWS * BAG_COLUMNS

# item types (ItemModel.type). Only Misc exists in the game for now; the others are here so the equipment slots
# already know what they will take
MISC = "Misc"
WEAPON_TYPES = {"Sword", "Rod", "Axe", "Dagger", "Mace", "Spear", "Bow"}

# equipment slot of the character -> item types it accepts
EQUIP_SLOTS = {
    "head": {"Helmet"},
    "armor": {"Armor"},
    "right_hand": WEAPON_TYPES,
    "left_hand": WEAPON_TYPES | {"Shield"},
    "garment": {"Cape"},
    "shoes": {"Boots"},
    "accessory_1": {"Accessory"},
    "accessory_2": {"Accessory"},
}

# types whose units pile up in a single slot (equipment takes one slot per piece)
STACKABLE_TYPES = {MISC}


def bag_slot(index: int) -> str:
    return f"bag_{index}"


def is_valid_slot(slot: str) -> bool:
    if slot in EQUIP_SLOTS:
        return True
    if slot.startswith("bag_") and slot[4:].isdigit():
        return 0 <= int(slot[4:]) < BAG_SIZE
    return False


def can_hold(slot: str, item_type: str) -> bool:
    """Whether an item of this type may sit in the slot; bag slots take anything"""
    if slot in EQUIP_SLOTS:
        return item_type in EQUIP_SLOTS[slot]
    return is_valid_slot(slot)


def free_bag_slot(occupied: set[str]) -> str | None:
    """First empty bag slot, left to right and top to bottom; None when the bag is full"""
    for index in range(BAG_SIZE):
        if bag_slot(index) not in occupied:
            return bag_slot(index)
    return None
