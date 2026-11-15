"""Level progression: how much EXP each level costs (see docs/progressao-de-level.md).

`CharacterModel.exp` is the character's TOTAL accumulated EXP; the level is derived from it. Going from
level N to N+1 costs EXP_PER_LEVEL_UP[tier of N], so the total needed to reach a level is the sum of the costs
of every level below it.
"""

MAX_LEVEL = 99

# (last level of the tier, EXP needed to go up from any level in the tier)
TIERS = [
    (5, 100), (10, 150), (20, 200), (30, 300), (40, 400),
    (50, 500), (60, 600), (70, 800), (80, 1000), (90, 1200), (99, 1500),
]


def exp_to_next(level: int) -> int | None:
    """EXP needed to go from `level` to the next one; None at the maximum level."""
    if level >= MAX_LEVEL:
        return None
    for last_level, cost in TIERS:
        if level <= last_level:
            return cost
    return None


def _build_totals() -> list[int]:
    totals = [0, 0]   # index = level; level 1 needs 0 total EXP
    for level in range(1, MAX_LEVEL):
        totals.append(totals[level] + exp_to_next(level))
    return totals


_TOTALS = _build_totals()
MAX_EXP = _TOTALS[MAX_LEVEL]   # total EXP of a level 99 character; more than this is not stored


def total_exp_for_level(level: int) -> int:
    """Total accumulated EXP at which a character reaches `level`."""
    return _TOTALS[max(1, min(level, MAX_LEVEL))]


def level_for_exp(total_exp: int) -> int:
    """The level a character with this total EXP has."""
    level = 1
    while level < MAX_LEVEL and total_exp >= _TOTALS[level + 1]:
        level += 1
    return level


def exp_progress(level: int, total_exp: int) -> int:
    """EXP accumulated inside the current level (what the EXP bar shows)."""
    return max(0, total_exp - total_exp_for_level(level))
