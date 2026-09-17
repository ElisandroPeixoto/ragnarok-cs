JOBS_SPRITES = {
    "Novice": "sprites/0.Novice_Idle.gif",
    "Swordman": "sprites/1.Swordman_Idle.gif"
}

JOBS_BADGES = {
    "Novice": "characters_badges/0_novice_badge.png",
}


def sprite_selector(job: str):
    return JOBS_SPRITES.get(job, None)

def badge_selector(job: str):
    return JOBS_BADGES.get(job, None)
