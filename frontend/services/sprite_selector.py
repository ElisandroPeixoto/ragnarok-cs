JOBS_SHEETS = {
    "Novice": "novice",
}

# GIFs das classes que ainda não têm sprite sheet
JOBS_SPRITES = {
}

JOBS_BADGES = {
    "Novice": "characters_badges/0_novice_badge.png",
}


def sheet_selector(job: str):
    return JOBS_SHEETS.get(job, None)

def sprite_selector(job: str):
    return JOBS_SPRITES.get(job, None)

def badge_selector(job: str):
    return JOBS_BADGES.get(job, None)
