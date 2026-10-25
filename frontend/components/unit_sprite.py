import flet as ft
from services.battle_animation import SpriteSheet, get_sheet, current_frame


def sheet_frame(sheet: SpriteSheet, row: int, col: int,
                box: tuple[int, int, int, int] | None = None, scale: float = 1.0) -> ft.Container:
    """Um frame da sheet. box = (x, y, w, h) recorta só essa área do frame; scale amplia."""
    box_x, box_y, box_w, box_h = box or (0, 0, sheet.frame_w, sheet.frame_h)
    return ft.Container(
        width=box_w * scale, height=box_h * scale,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            width=box_w * scale, height=box_h * scale,
            controls=[
                ft.Image(
                    src=sheet.src,
                    left=-(col * sheet.frame_w + box_x) * scale,
                    top=-(row * sheet.frame_h + box_y) * scale,
                    width=sheet.frame_w * sheet.cols * scale,
                    height=sheet.frame_h * sheet.rows * scale,
                    fit=ft.BoxFit.FILL,
                    filter_quality=ft.FilterQuality.NONE,   # pixel art: amplia sem borrar
                )
            ],
        ),
    )


def unit_sprite(unit: dict, left: float, top: float) -> ft.Container:
    sheet = get_sheet(unit["sheet"])
    row, col = current_frame(unit)
    sprite = sheet_frame(sheet, row, col)
    sprite.left, sprite.top = left, top
    return sprite
