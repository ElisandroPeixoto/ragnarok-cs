"""Save the selected character during the app session"""

_current_character: dict | None = None


def set_current_character(character: dict) -> None:
    global _current_character
    _current_character = character


def get_current_character() -> dict | None:
    return _current_character
