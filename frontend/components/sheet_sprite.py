import asyncio
import flet as ft
from services.battle_animation import get_sheet
from components.unit_sprite import sheet_frame

# Clip used as a monster's picture outside the battle board (map cards, battle unit cards)
MONSTER_PICTURE_CLIP = "idle_sw"


@ft.component
def sheet_sprite(sheet_name: str, clip_name: str, height: float, width: float | None = None):
    """Loops one clip of a sprite sheet, cropped to the clip's box.
    Scaled to `height`; with `width` too, scaled to fit inside width x height and centered."""
    frame, set_frame = ft.use_state(0)
    loop_state, _ = ft.use_state(lambda: {"closed": False})

    def on_mount():
        async def anim_loop():
            while not loop_state["closed"]:
                clip = get_sheet(sheet_name).clips[clip_name]
                await asyncio.sleep(1 / clip.fps)
                if not loop_state["closed"]:
                    set_frame(lambda index: index + 1)

        ft.context.page.run_task(anim_loop)

    def on_unmount():
        loop_state["closed"] = True

    ft.use_effect(on_mount, [], cleanup=on_unmount)

    sheet = get_sheet(sheet_name)
    clip = sheet.clips[clip_name]
    box = clip.box or (0, 0, sheet.frame_w, sheet.frame_h)
    scale = height / box[3] if width is None else min(width / box[2], height / box[3])
    sprite = sheet_frame(sheet, clip.row, frame % clip.frames, box, scale=scale)
    if width is None:
        return sprite
    return ft.Container(width=width, height=height, alignment=ft.Alignment.CENTER, content=sprite)


def monster_sprite(sheet_name: str, width: float, height: float):
    """A monster's idle animation fitted inside width x height."""
    return sheet_sprite(sheet_name, MONSTER_PICTURE_CLIP, height=height, width=width)
