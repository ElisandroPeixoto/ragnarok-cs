"""Animação por sprite sheet: carrega o JSON, guarda o clip atual da unidade
e calcula qual frame desenhar a partir do tempo (função pura)."""
import json
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from config import ASSETS_DIR


DEFAULT_ANIM = "idle"
DEFAULT_FACING = "se"
WALK_SECONDS_PER_TILE = 0.35    # velocidade da caminhada no tabuleiro


@dataclass(frozen=True)
class Clip:
    row: int
    frames: int
    fps: float = 8
    loop: bool = True
    hold_last: bool = False
    box: tuple[int, int, int, int] | None = None   # (x, y, w, h) da área desenhada dentro do frame

    @property
    def duration(self) -> float:
        return self.frames / self.fps


@dataclass(frozen=True)
class SpriteSheet:
    src: str
    frame_w: int
    frame_h: int
    cols: int
    rows: int
    anchor_x: int      # pés do personagem dentro do frame
    anchor_y: int
    clips: dict


@lru_cache(maxsize=None)
def get_sheet(name: str) -> SpriteSheet:
    path = Path(ASSETS_DIR) / "sprites" / name / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    clips = {key: Clip(**value) for key, value in data.pop("clips").items()}
    return SpriteSheet(**data, clips=clips)


def _find_clip(sheet: SpriteSheet, anim: str, facing: str) -> Clip:
    """Clip pedido; se não existir, idle na mesma direção; por último, o primeiro clip."""
    for key in (f"{anim}_{facing}", f"{DEFAULT_ANIM}_{facing}"):
        if key in sheet.clips:
            return sheet.clips[key]
    return next(iter(sheet.clips.values()))


def play(unit: dict, anim: str) -> None:
    """Começa um clip ("attack", "hurt", "dead"...). Unidade morta não troca mais de clip."""
    if unit.get("anim") == "dead":
        return
    unit["anim"] = anim
    unit["anim_started"] = time.monotonic()


def facing_for(delta_col: int, delta_row: int) -> str | None:
    """Direção do sprite para um deslocamento. +col=SE, -col=NW, +row=SW, -row=NE."""
    if delta_col == 0 and delta_row == 0:
        return None
    if abs(delta_col) >= abs(delta_row):
        return "se" if delta_col > 0 else "nw"
    return "sw" if delta_row > 0 else "ne"


def face_towards(unit: dict, to_col: int, to_row: int) -> None:
    """Vira a unidade para o tile de destino."""
    facing = facing_for(to_col - unit["col"], to_row - unit["row"])
    if facing:
        unit["facing"] = facing


# CAMINHADA
# A lógica (col/row, ocupação, PA) já vai para o destino na hora; só o desenho
# percorre "walk_path" tile a tile enquanto o clip "walk" estiver tocando.

def start_walk(unit: dict, path: list[tuple[int, int]]) -> None:
    """path = tiles a percorrer, sem o de partida (ver battle_actions.find_path)."""
    unit["walk_path"] = [(unit["col"], unit["row"]), *path]
    (prev_col, prev_row), (col, row) = unit["walk_path"][-2:]
    unit["col"], unit["row"] = col, row
    unit["facing"] = facing_for(col - prev_col, row - prev_row)   # direção ao chegar
    play(unit, "walk")


def _walk_duration(unit: dict) -> float:
    return (len(unit.get("walk_path") or [None]) - 1) * WALK_SECONDS_PER_TILE


def walk_pose(unit: dict, now: float | None = None) -> tuple[float, float, str] | None:
    """(col, row, facing) fracionários no meio da caminhada; None se não está andando."""
    path = unit.get("walk_path")
    if unit.get("anim") != "walk" or not path:
        return None
    now = time.monotonic() if now is None else now
    progress = max(0.0, now - unit["anim_started"]) / WALK_SECONDS_PER_TILE
    step = int(progress)
    if step >= len(path) - 1:
        return None
    (from_col, from_row), (to_col, to_row) = path[step], path[step + 1]
    fraction = progress - step
    return (from_col + (to_col - from_col) * fraction,
            from_row + (to_row - from_row) * fraction,
            facing_for(to_col - from_col, to_row - from_row))


def walk_remaining(unit: dict, now: float | None = None) -> float:
    """Segundos até a unidade chegar ao destino (0 se não está andando)."""
    if unit.get("anim") != "walk":
        return 0.0
    now = time.monotonic() if now is None else now
    return max(0.0, unit["anim_started"] + _walk_duration(unit) - now)


def board_position(unit: dict, now: float | None = None) -> tuple[float, float]:
    """Posição desenhada (col, row): interpolada durante a caminhada, senão o tile da unidade."""
    pose = walk_pose(unit, now)
    return (pose[0], pose[1]) if pose else (unit["col"], unit["row"])


def current_frame(unit: dict, now: float | None = None) -> tuple[int, int]:
    """(linha, coluna) do frame atual na sheet. Não altera a unidade."""
    sheet = get_sheet(unit["sheet"])
    now = time.monotonic() if now is None else now
    anim, started = unit.get("anim", DEFAULT_ANIM), unit.get("anim_started", 0.0)
    pose = walk_pose(unit, now)
    facing = pose[2] if pose else unit.get("facing", DEFAULT_FACING)
    if anim == "walk" and pose is None:     # chegou: fica em idle a partir da chegada
        anim, started = DEFAULT_ANIM, started + _walk_duration(unit)
    clip = _find_clip(sheet, anim, facing)
    elapsed = max(0.0, now - started)
    index = int(elapsed * clip.fps)

    if clip.loop:
        return clip.row, index % clip.frames
    if index < clip.frames:
        return clip.row, index
    if clip.hold_last:
        return clip.row, clip.frames - 1

    # clip de uma vez só terminou: volta para idle
    idle = _find_clip(sheet, DEFAULT_ANIM, facing)
    idle_index = int((elapsed - clip.duration) * idle.fps)
    return idle.row, idle_index % idle.frames