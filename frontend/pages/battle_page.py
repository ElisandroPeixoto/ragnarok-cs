import asyncio
import flet as ft
import themes as t
from services.battle_state import BattleState
from services.battle_ai import iter_ai_turn
from services.battle_animation import walk_remaining
from components.battle_board import battle_board
from components.unit_card import units_panel
from components.skills_panel import skills_panel, SKILL_KEYS
from components.battle_log_panel import battle_log_panel
from components.turn_panel import turn_panel
from services.battle_geometry import BoardConfig
from services.map_router_manager import navigate_back_from_battle
from services.session_state import get_battle_setup, get_current_character, set_current_character
from services.character_service import CharacterService
from services.api_client import ApiError
from components.sidebar import sidebar


board_config = BoardConfig()


BOARD_WIDTH, BOARD_HEIGHT = 1100, 700
LEFT_WIDTH = 330
RIGHT_PANEL_WIDTH = 300
BOTTOM_HEIGHT = 200
GAP = 16
CONTENT_WIDTH = LEFT_WIDTH + GAP + BOARD_WIDTH

ENEMY_ACTION_DELAY = 0.7      # seconds between the monster's actions (so the player can follow them)
TICK_INTERVAL = 0.25          # the loop wakes up 4x per second; the turn clock ticks once per second
ANIM_INTERVAL = 1 / 12      # ~12 re-renders per second; lower to 1/8 if it gets heavy


@ft.component
def battle_page():
    setup = get_battle_setup()
    if setup is None:  # route opened without going through the Hunt button
        return ft.Container(
            expand=True, bgcolor=t.PAGE_BACKGROUND_COLOR, alignment=ft.Alignment.CENTER,
            content=ft.Text("No battle in progress", color=t.NORMAL_TEXT, font_family="Cinzel"),
        )
    return battle_screen(setup)


@ft.component
def battle_screen(setup: dict):
    # lambda: create it (and roll the positions) only on the first render, not on every re-render
    state, _ = ft.use_state(lambda: BattleState(
        setup["units"], setup["skills"], board_config, setup["spawn_pool"], setup["spawn_rate"]))
    _, set_tick = ft.use_state(0)
    selected_skill, set_selected_skill = ft.use_state(None)
    collapsed, set_collapsed = ft.use_state(True)

    def refresh(clear_skill: bool = False):
        """Call after ANY state change: re-renders the page."""
        if clear_skill:
            set_selected_skill(None)
        state.version += 1
        set_tick(state.version)

    async def save_exp():
        """Sends the hero's final EXP to the backend (once per hunt, and only if it changed)."""
        if state.exp_saved:
            return
        state.exp_saved = True
        character, hero_exp = get_current_character(), state.hero.get("exp", 0)
        if character is None or hero_exp == state.exp_start:
            return
        try:
            set_current_character(await CharacterService.update_exp(character["id"], hero_exp))
        except ApiError as error:
            print(f"Failed to save the EXP: {error.detail}")

    # ---------- STEP 11: turn loop (timer + monster turn) ----------
    def on_mount():
        async def turn_loop():
            elapsed = 0.0
            while not state.closed and state.winner is None:
                if state.current_unit()["team"] == "enemy":
                    state.input_locked = True
                    refresh(clear_skill=True)
                    await asyncio.sleep(ENEMY_ACTION_DELAY)
                    unit = state.current_unit()
                    for _ in iter_ai_turn(state, state.current_unit_id):
                        refresh()
                        # if it walked, only act again after reaching the destination
                        await asyncio.sleep(walk_remaining(unit) + ENEMY_ACTION_DELAY)
                    if state.closed:
                        break
                    state.end_turn()
                    state.input_locked = False
                    elapsed = 0.0
                    refresh()
                else:
                    await asyncio.sleep(TICK_INTERVAL)
                    elapsed += TICK_INTERVAL
                    if elapsed >= 1.0 and not state.closed:
                        elapsed = 0.0
                        if state.tick():                  # time ran out: the turn passed on its own
                            refresh(clear_skill=True)
                        else:
                            refresh()

        async def anim_loop():
            while not state.closed:  # keeps going after a winner so the "dead" clip can finish
                await asyncio.sleep(ANIM_INTERVAL)
                if state.winner is not None:
                    await save_exp()   # the death penalty is saved right away, not only on Leave
                refresh()

        ft.context.page.run_task(turn_loop)
        ft.context.page.run_task(anim_loop)


    def on_unmount():
        state.closed = True       # stops the loops when the screen is left
        ft.context.page.on_keyboard_event = None

    ft.use_effect(on_mount, [], cleanup=on_unmount)

    # ---------- handlers ----------
    def player_can_act() -> bool:
        return (state.winner is None and not state.input_locked
                and state.current_unit()["team"] == "player"
                and walk_remaining(state.current_unit()) == 0)

    def handle_select_skill(name: str):
        if not player_can_act():
            return
        if state.current_unit()["ap"] < state.skills[name]["ap_cost"]:
            return
        set_selected_skill(None if selected_skill == name else name)

    def handle_key(event: ft.KeyboardEvent):
        """Q/W/E/R/T select the hero's 1st..5th skill (pressing it again deselects), Space ends the turn."""
        if event.ctrl or event.alt or event.meta or event.shift:
            return
        if event.key in (" ", "Space"):     # space = Turn End button
            handle_end_turn(None)
            return
        key = event.key.upper()
        skills = state.units["hero"]["skills"]
        if key in SKILL_KEYS and SKILL_KEYS.index(key) < len(skills):
            handle_select_skill(skills[SKILL_KEYS.index(key)])

    ft.context.page.on_keyboard_event = handle_key   # re-bound each render so it sees the current selected_skill

    def handle_end_turn(e):
        if not player_can_act():
            return
        state.end_turn()
        refresh(clear_skill=True)

    def handle_leave(e):
        async def leave():
            await save_exp()   # leaving keeps the EXP earned in the hunt
            state.closed = True
            navigate_back_from_battle()
        ft.context.page.run_task(leave)

    # ---------- layout ----------
    log_width = CONTENT_WIDTH - LEFT_WIDTH - RIGHT_PANEL_WIDTH - 2 * GAP

    top_row = ft.Row(
        spacing=GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            units_panel(state, LEFT_WIDTH, BOARD_HEIGHT),
            battle_board(state, state.version, selected_skill, refresh),
        ],
    )

    bottom_row = ft.Row(
        spacing=GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            skills_panel(state, selected_skill, handle_select_skill, LEFT_WIDTH, BOTTOM_HEIGHT),
            battle_log_panel(state.log.entries, log_width, BOTTOM_HEIGHT),
            turn_panel(state, handle_end_turn, handle_leave, RIGHT_PANEL_WIDTH, BOTTOM_HEIGHT),
        ],
    )

    battle_area = ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=CONTENT_WIDTH,
                    padding=ft.Padding.symmetric(vertical=16),
                    content=ft.Column(spacing=GAP, controls=[top_row, bottom_row]),
                ),
            ],
        ),
    )

    return ft.Container(
        expand=True,
        bgcolor=t.PAGE_BACKGROUND_COLOR,
        content=ft.Row(
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                sidebar(collapsed, lambda e: set_collapsed(not collapsed)),
                battle_area,
            ],
        ),
    )