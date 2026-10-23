"""Save the selected character during the app session"""

_current_character: dict | None = None
_battle_return_route: str | None = None


def set_current_character(character: dict) -> None:
    global _current_character
    _current_character = character


def get_current_character() -> dict | None:
    return _current_character


def set_battle_return_route(route: str) -> None:
    global _battle_return_route
    _battle_return_route = route


def get_battle_return_route() -> str | None:
    return _battle_return_route