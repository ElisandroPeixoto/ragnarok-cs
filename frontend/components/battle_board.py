import flet as ft
import flet.canvas as cv
from services.battle_state import BattleState
from services.battle_geometry import (
    is_inside_board, sort_units_by_depth, get_sprite_bounds, tile_to_pixel, pixel_to_tile,
)
from services.battle_actions import can_move, find_path, perform_move, perform_attack, get_attack_tiles
from services.battle_animation import board_position, walk_remaining
from services.assets import asset_file_exists
from components.battle_grid import STATIC_GRID_SHAPES, create_tile_diamond, create_fill_paint
import themes as t
from components.unit_sprite import unit_sprite


_hover_state = {
    "tile": None,           # tile under the pointer (for the path preview), or None
    "render_counter": 0,    # ever-increasing value used only to trigger re-renders
}


def get_pointer_position(event) -> tuple[float, float]:
    """Pointer position relative to the stage (works across Flet versions)."""
    position = getattr(event, "local_position", None)
    if position is not None:
        return position.x, position.y
    return event.local_x, event.local_y


# ============================================================
# COMPONENT
# state e selected_skill vêm da página; on_change(clear_skill=False) avisa a página
# que o estado mudou (para atualizar cards, log e timer).
# `version` só existe para a página poder forçar o re-render deste componente.
# ============================================================
@ft.component
def battle_board(state: BattleState, version: int, selected_skill: str | None, on_change):
    board = state.board
    units = state.units
    _, set_render_tick = ft.use_state(0)

    def force_rerender():
        _hover_state["render_counter"] += 1
        set_render_tick(_hover_state["render_counter"])

    def player_can_act() -> bool:
        return (state.winner is None and not state.input_locked
                and state.current_unit()["team"] == "player"
                and walk_remaining(state.current_unit()) == 0)   # espera terminar de andar

    # ---------- gesture handlers ----------
    def handle_hover(event):
        tile = pixel_to_tile(*get_pointer_position(event), board)
        if not is_inside_board(*tile, board):
            tile = None
        if tile != _hover_state["tile"]:
            _hover_state["tile"] = tile
            force_rerender()

    def handle_exit(event):
        if _hover_state["tile"] is not None:
            _hover_state["tile"] = None
            force_rerender()

    def handle_move_click(pointer_x: float, pointer_y: float):
        """Clicar num tile anda até ele pelo caminho mais curto (se houver PA)."""
        target_col, target_row = pixel_to_tile(pointer_x, pointer_y, board)
        result = perform_move(state, state.current_unit_id, target_col, target_row)
        if result["ok"]:
            on_change()
        elif result["reason"] != "already on this tile":
            print(f"[move] {result['reason']}")

    def handle_tap(event):
        """Com uma skill selecionada, clicar no inimigo ataca; sem skill, clicar no tile anda."""
        if not player_can_act():
            return
        pointer_x, pointer_y = get_pointer_position(event)
        if not selected_skill:
            handle_move_click(pointer_x, pointer_y)
            return

        attacker_id = state.current_unit_id
        attacker_team = units[attacker_id]["team"]
        for unit_id, unit in sort_units_by_depth(units, farthest_first=False):
            if unit["hp"] <= 0 or unit["team"] == attacker_team:
                continue
            center_x, center_y = tile_to_pixel(unit["col"], unit["row"], board)
            left, top, right, bottom = get_sprite_bounds(unit, center_x, center_y)
            if left <= pointer_x <= right and top <= pointer_y <= bottom:
                result = perform_attack(state, attacker_id, unit_id, selected_skill)
                if result["ok"]:
                    on_change(clear_skill=True)
                else:
                    print(f"[attack] {result['reason']}")
                return

    # ---------- layer 1: background ----------
    if asset_file_exists(board.background_image):
        background = ft.Image(src=board.background_image, width=board.width,
                              height=board.height, fit=ft.BoxFit.FILL)
    else:
        background = ft.Container(width=board.width, height=board.height,
                                  bgcolor=t.PLACEHOLDER_BACKGROUND_COLOR)

    # ---------- layer 2: grid + destaques ----------
    grid_shapes = list(STATIC_GRID_SHAPES)
    hover_tile = _hover_state["tile"]

    if selected_skill and player_can_act():
        # modo ataque: destaca os tiles que a skill alcança
        for col, row in get_attack_tiles(state, state.current_unit_id, selected_skill):
            grid_shapes.append(create_tile_diamond(col, row, create_fill_paint(t.ATTACK_TILE_COLOR), board))
    elif hover_tile is not None and player_can_act():
        # modo movimento: caminho até o tile em verde, ou o tile em vermelho se não dá para ir
        unit_id = state.current_unit_id
        current = state.current_unit()
        if hover_tile != (current["col"], current["row"]):
            is_valid, _, _ = can_move(state, unit_id, *hover_tile)
            if is_valid:
                for col, row in find_path(state, unit_id, *hover_tile):
                    grid_shapes.append(create_tile_diamond(col, row, create_fill_paint(t.VALID_TILE_COLOR), board))
            else:
                grid_shapes.append(create_tile_diamond(*hover_tile, create_fill_paint(t.INVALID_TILE_COLOR), board))

    grid_layer = cv.Canvas(shapes=grid_shapes, width=board.width, height=board.height)

    # ---------- layer 3: sprites (só unidades vivas) ----------
    sprite_controls = []
    for unit_id, unit in sort_units_by_depth(units):
        has_sheet = bool(unit.get("sheet"))
        if unit["hp"] <= 0 and not has_sheet:
            continue  # sem sheet não há animação de morte: some na hora
        center_x, center_y = tile_to_pixel(*board_position(unit), board)   # interpolado enquanto anda

        left, top, _, _ = get_sprite_bounds(unit, center_x, center_y)

        if has_sheet:
            sprite = unit_sprite(unit, left, top)
        elif asset_file_exists(unit["sprite"]):
            sprite = ft.Image(src=unit["sprite"], width=unit["width"],
                              height=unit["height"], fit=ft.BoxFit.CONTAIN)
        else:
            sprite = ft.Container(width=unit["width"], height=unit["height"],
                                  bgcolor=unit["placeholder_color"], border_radius=6)
        sprite.left, sprite.top = left, top
        sprite_controls.append(sprite)

    stage = ft.Stack(
        controls=[background, grid_layer, *sprite_controls],
        width=board.width,
        height=board.height,
    )

    gesture_detector = ft.GestureDetector(
        content=stage,
        on_tap_down=handle_tap,
        on_hover=handle_hover,
        on_exit=handle_exit,
    )

    return ft.Container(
        border=ft.Border.all(1, t.BOARD_BORDER_COLOR),
        border_radius=6,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=gesture_detector,
    )
