"""Sprite sheet animation: loads the JSON, stores the unit's current clip
and computes which frame to draw from the time (pure function)."""
import json
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from config import ASSETS_DIR


DEFAULT_ANIM = "idle"
DEFAULT_FACING = "se"
WALK_SECONDS_PER_TILE = 0.35    # walking speed on the board


@dataclass(frozen=True)
class Clip:
    row: int
    frames: int
    fps: float = 8
    loop: bool = True
    hold_last: bool = False
    box: tuple[int, int, int, int] | None = None   # (x, y, w, h) of the drawn area inside the frame

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
    anchor_x: int      # character's feet inside the frame
    anchor_y: int
    clips: dict


@lru_cache(maxsize=None)
def get_sheet(name: str) -> SpriteSheet:
    path = Path(ASSETS_DIR) / "sprites" / name / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    clips = {key: Clip(**value) for key, value in data.pop("clips").items()}
    return SpriteSheet(**data, clips=clips)


def _find_clip(sheet: SpriteSheet, anim: str, facing: str) -> Clip:
    """Requested clip; if missing, idle in the same direction; as a last resort, the first clip."""
    for key in (f"{anim}_{facing}", f"{DEFAULT_ANIM}_{facing}"):
        if key in sheet.clips:
            return sheet.clips[key]
    return next(iter(sheet.clips.values()))


def play(unit: dict, anim: str) -> None:
    """Starts a clip ("attack", "hurt", "dead"...). A dead unit no longer changes clips."""
    if unit.get("anim") == "dead":
        return
    unit["anim"] = anim
    unit["anim_started"] = time.monotonic()


def facing_for(delta_col: int, delta_row: int) -> str | None:
    """Sprite facing for a displacement. +col=SE, -col=NW, +row=SW, -row=NE."""
    if delta_col == 0 and delta_row == 0:
        return None
    if abs(delta_col) >= abs(delta_row):
        return "se" if delta_col > 0 else "nw"
    return "sw" if delta_row > 0 else "ne"


def face_towards(unit: dict, to_col: int, to_row: int) -> None:
    """Turns the unit toward the target tile."""
    facing = facing_for(to_col - unit["col"], to_row - unit["row"])
    if facing:
        unit["facing"] = facing


# WALKING
# The logic (col/row, occupancy, AP) jumps to the destination right away; only the drawing
# goes through "walk_path" tile by tile while the "walk" clip is playing.

def start_walk(unit: dict, path: list[tuple[int, int]]) -> None:
    """path = tiles to walk through, without the starting one (see battle_actions.find_path)."""
    unit["walk_path"] = [(unit["col"], unit["row"]), *path]
    (prev_col, prev_row), (col, row) = unit["walk_path"][-2:]
    unit["col"], unit["row"] = col, row
    unit["facing"] = facing_for(col - prev_col, row - prev_row)   # facing on arrival
    play(unit, "walk")


def _walk_duration(unit: dict) -> float:
    return (len(unit.get("walk_path") or [None]) - 1) * WALK_SECONDS_PER_TILE


def walk_pose(unit: dict, now: float | None = None) -> tuple[float, float, str] | None:
    """Fractional (col, row, facing) mid-walk; None if the unit is not walking."""
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
    """Seconds until the unit reaches its destination (0 if it is not walking)."""
    if unit.get("anim") != "walk":
        return 0.0
    now = time.monotonic() if now is None else now
    return max(0.0, unit["anim_started"] + _walk_duration(unit) - now)


def board_position(unit: dict, now: float | None = None) -> tuple[float, float]:
    """Drawn position (col, row): interpolated while walking, otherwise the unit's tile."""
    pose = walk_pose(unit, now)
    return (pose[0], pose[1]) if pose else (unit["col"], unit["row"])


def current_frame(unit: dict, now: float | None = None) -> tuple[int, int]:
    """(row, column) of the current frame in the sheet. Doesn't modify the unit."""
    sheet = get_sheet(unit["sheet"])
    now = time.monotonic() if now is None else now
    anim, started = unit.get("anim", DEFAULT_ANIM), unit.get("anim_started", 0.0)
    pose = walk_pose(unit, now)
    facing = pose[2] if pose else unit.get("facing", DEFAULT_FACING)
    if anim == "walk" and pose is None:     # arrived: idle from the moment of arrival
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

    # one-shot clip finished: back to idle
    idle = _find_clip(sheet, DEFAULT_ANIM, facing)
    idle_index = int((elapsed - clip.duration) * idle.fps)
    return idle.row, idle_index % idle.frames