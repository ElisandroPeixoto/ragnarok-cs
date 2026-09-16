# USE ONLY TO VALIDADE FRONTEND BEFORE INTEGRATE WITH API BACKEND

# Mocked data — backend integration deferred
MOCK_CHARACTER = {
    "name": "CharName",
    "job": "Novice",
    "level": 1,
    "job_level": 1,
    "hp": 50,
    "max_hp": 50,
    "exp": 0,
    "max_exp": 100,
    "current_map": "Novice Academy",
    "current_map_id": "novice_academy",
    "zeny": 200,
    "sprite": "sprites/0.Novice_Idle.gif",
    "map_thumbnail": "maps/novice_academy.jpg",
    "badge": "characters_badges/0_novice_badge.png"

}


MOCK_MAPS = {
    "novice_academy": {
        "name": "Novice Academy",
        "level_range": "1 - 10",
        "image": "maps/novice_academy.jpg",
        "about": "Lorem ipsum dolor sit amet...",
        "npcs": [
            {"name": "Hostess", "image": "npcs/hostess.gif"},
            {"name": "Sailor", "image": "npcs/sailor.gif"},
        ],
        "monsters": [],  # pode ficar vazio mesmo — section_panel já trata isso
        "navigation": [
            {"name": "Academy", "image": "places/academy.jpg", "map_id": "academy"},
            {"name": "Training Field 1", "image": "maps/training_field_1.jpg", "map_id": "training_field_1"},
        ],
    },
    "training_field_1": {
        "name": "Training Field 1",
        "level_range": "5 - 15",
        "image": "maps/training_field_1.jpg",
        "about": "...",
        "npcs": [{"name": "Hostess", "image": "npcs/trainer.gif"}],
        "monsters": [
            {"name": "Poring", "image": "monsters/poring.gif", "spawn_rate": 40}, {"name": "Lunatic", "image": "monsters/lunatic.gif", "spawn_rate": 40}, {"name": "Wilow", "image": "monsters/wilow.gif", "spawn_rate": 20}
        ],
        "navigation": [
            {"name": "Novice Academy", "image": "maps/novice_academy.jpg", "map_id": "novice_academy"},
        ],
    },
}
