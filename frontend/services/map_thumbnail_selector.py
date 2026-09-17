from mockup import MOCK_MAPS  # TODO: REMOVE AFTER MAP BACKEND MIGRATION


def map_thumbnail_selector(map_id: str):
    return MOCK_MAPS.get(map_id, {}).get("image")
