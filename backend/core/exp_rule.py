"""Experience rule: how much EXP a hero earns for defeating a monster (see docs/regra-de-experiencia.md).
The backend owns it: battles.py sends each monster's reward, characters.py settles the hunt.

The percentage depends on the level difference (hero level - monster level):
  hero higher: 0-5 -> 100%, 6-10 -> 90%, 11-30 -> 50%, over 30 -> 10%
  hero lower:  1-5 -> 100%, 6-10 -> 110%, 11-30 -> 120%, over 30 -> 40%
"""

DEATH_EXP_PENALTY = 20   # percent of the current EXP lost when the hero dies

# (largest difference covered, percentage), checked in order; the last row is the open-ended tier
HERO_HIGHER_TIERS = [(5, 100), (10, 90), (30, 50), (None, 10)]
HERO_LOWER_TIERS = [(5, 100), (10, 110), (30, 120), (None, 40)]


def exp_percentage(hero_level: int, monster_level: int) -> int:
    """Percentage of the monster's base EXP earned at this level difference."""
    difference = hero_level - monster_level
    tiers = HERO_HIGHER_TIERS if difference >= 0 else HERO_LOWER_TIERS
    for limit, percentage in tiers:
        if limit is None or abs(difference) <= limit:
            return percentage
    return 100  # unreachable: the last tier has no limit


def exp_after_death(level_progress: int) -> int:
    """The EXP accumulated in the current level after dying: loses DEATH_EXP_PENALTY% of it, rounded down.
    Only the progress inside the level is penalized, so dying never lowers the level."""
    return level_progress - level_progress * DEATH_EXP_PENALTY // 100


def exp_gain(hero_level: int, monster_level: int, base_exp: int) -> int:
    """EXP earned for the kill, rounded down."""
    return base_exp * exp_percentage(hero_level, monster_level) // 100
