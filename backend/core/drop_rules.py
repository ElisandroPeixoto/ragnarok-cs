"""Item drops (docs/inventario.md#drops): every monster killed in a won hunt rolls each item it drops once, with the
item's drop rate as the chance"""
import random

# every monster card drops at this rate (percent)
CARD_DROP_RATE = 0.2


def roll_drops(drop_tables: list[list[tuple[str, float]]], rng: random.Random | None = None) -> dict[str, int]:
    """drop_tables has one entry per monster killed: [(item_id, drop rate in percent), ...].
    Returns {item_id: amount dropped}, without the items that did not drop"""
    rng = rng or random
    dropped: dict[str, int] = {}
    for table in drop_tables:
        for item_id, rate in table:
            if rng.random() * 100 < rate:
                dropped[item_id] = dropped.get(item_id, 0) + 1
    return dropped
