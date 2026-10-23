# MOCKUPS
INITIAL_UNITS = {
    "hero": {
        "name": "Character", "job": "Novice", "team": "player",
        "sheet": "novice", "facing": "se",
        "avatar": "characters_badges/0_novice_badge.png",

        "col": 0, "row": 4, "is_draggable": True,
        "offset_x": 0, "offset_y": 0,

        "hp": 50, "max_hp": 50,
        "ap": 5, "max_ap": 5,
        "skills": ["Basic Attack"]
    },


    "monster": {
        "name": "Poring", "team": "enemy",
        "sprite": "monsters/poring.gif", "width": 50, "height": 50,
        "avatar": "monsters/poring.gif",
        "ai": "approach_and_attack",

        "col": 9, "row": 4, "is_draggable": False,
        "placeholder_color": "#B3261E",
        "offset_x": 0, "offset_y": 6,

        "hp": 50, "max_hp": 50,
        "ap": 2, "max_ap": 2,
        "skills": ["Basic Attack"]
    },
}