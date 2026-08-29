JOBS_SPRITES = {
    "Novice": "sprites/0.Novice_Idle.gif",
    "Swordman": "sprites/1.Swordman_Idle.gif"
}

def sprite_selector(job: str):
    return JOBS_SPRITES.get(job, None)
