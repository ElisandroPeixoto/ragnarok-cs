import copy
import random
from services.battle_geometry import BoardConfig
from services.battle_log import BattleLog, LogEntry

TURN_DURATION = 30

# Columns where each team can spawn; the row is random
SPAWN_COLUMNS = {"player": (0,), "enemy": (7, 8, 9)}
SPAWN_FACING = {"player": "se", "enemy": "nw"}


WAVE_INTERVAL = 3   # a new wave of monsters every 3 rounds (round 1, 4, 7, ...)


def place_unit(unit: dict, taken: set, board: BoardConfig) -> bool:
    """Picks the unit's starting tile at random among the free ones of its team's columns and sets
    its facing. Adds the tile to `taken`; returns False if there is no free tile."""
    team = unit["team"]
    free_tiles = [(col, row) for col in SPAWN_COLUMNS[team] for row in range(board.row_count)
                  if (col, row) not in taken]
    if not free_tiles:
        return False
    unit["col"], unit["row"] = random.choice(free_tiles)
    taken.add((unit["col"], unit["row"]))
    unit["facing"] = SPAWN_FACING[team]
    return True


class BattleState:
    def __init__(self, units: dict, skills: dict, board: BoardConfig, spawn_pool: list[dict] | None = None,
                 spawn_rate: int = 1, turn_duration: int = TURN_DURATION):
        """units (the hero), skills, spawn_pool and spawn_rate come from the backend
        (BattleService.start_battle); positions are rolled here. The battle is endless: monsters
        keep arriving in waves of `spawn_rate`, drawn from `spawn_pool` by weight (repeats allowed)."""
        self.units = copy.deepcopy(units)
        self.skills = skills
        self.board = board
        self.spawn_pool = spawn_pool or []
        self.spawn_rate = spawn_rate
        self.monster_count = 0   # ids are never reused: monster_1, monster_2, ...
        for unit in self.units.values():
            place_unit(unit, set(board.blocked_tiles), board)
        # the hero acts first; monsters are appended in the order they arrive
        self.turn_order: list[str] = list(self.units)
        self.turn_index : int = 0
        self.round : int = 1
        self.spawn_wave()
        self.turn_duration: int = turn_duration
        self.time_left = turn_duration
        self.winner: str | None = None
        self.log = BattleLog()

        # UI Flags
        self.input_locked = False  # True when enemy is playing
        self.closed = False  # TODO: Check if its necessary
        self.version = 0  # Force UI re-render


    # Getters
    @property
    def current_unit_id(self) -> str:
        return self.turn_order[self.turn_index]

    def current_unit(self) -> dict:
        return self.units[self.current_unit_id]

    def is_alive(self, unit_id: str) -> bool:
        return self.units[unit_id]["hp"] > 0

    def unit_at(self, col: int, row: int) -> str | None:
        """Id of the LIVING unit on that tile (or None)."""
        for unit_id, unit in self.units.items():
            if unit["hp"] > 0 and unit["col"] == col and unit["row"] == row:
                return unit_id
        return None


    # Turns
    def refill_ap(self, unit_id: str) -> None:
        unit = self.units[unit_id]
        unit["ap"] = unit["max_ap"]

    def end_turn(self) -> None:
        if self.winner:
            return
        for _ in range(len(self.turn_order)):
            self.turn_index += 1
            if self.turn_index >= len(self.turn_order):
                self.turn_index = 0
                self.round += 1
                self.begin_round()
            if self.is_alive(self.current_unit_id):
                break
        self.time_left = self.turn_duration
        self.refill_ap(self.current_unit_id)

    def begin_round(self) -> None:
        """Runs when a new round starts (the hero is next): clears the dead monsters and, every
        WAVE_INTERVAL rounds, brings a new wave."""
        for unit_id in [uid for uid, unit in self.units.items() if unit["team"] == "enemy" and unit["hp"] <= 0]:
            del self.units[unit_id]
            self.turn_order.remove(unit_id)
        if (self.round - 1) % WAVE_INTERVAL == 0:
            self.spawn_wave()

    def spawn_wave(self) -> None:
        """Rolls `spawn_rate` monsters from the pool (weighted, repeats allowed) onto free enemy tiles."""
        if not self.spawn_pool:
            return
        taken = set(self.board.blocked_tiles) | {(u["col"], u["row"]) for u in self.units.values() if u["hp"] > 0}
        weights = [entry["weight"] for entry in self.spawn_pool]
        for entry in random.choices(self.spawn_pool, weights=weights, k=self.spawn_rate):
            unit = copy.deepcopy(entry["unit"])
            if not place_unit(unit, taken, self.board):
                break   # enemy columns are full
            self.monster_count += 1
            unit_id = f"monster_{self.monster_count}"
            self.units[unit_id] = unit
            self.turn_order.append(unit_id)

    def tick(self) -> bool:
        """Called each second by UI. Return True if the time is over and the turn ends up"""
        if self.winner:
            return False
        self.time_left -= 1
        if self.time_left <= 0:
            self.end_turn()
            return True
        return False


    # Battle End
    def check_battle_end(self) -> str | None:
        """The hunt is endless: it only ends when the player's team is dead (otherwise leave by the button)."""
        player_alive = any(u["team"] == "player" and u["hp"] > 0 for u in self.units.values())
        if self.winner is None and not player_alive:
            self.winner = "defeat"
            self.log.add(LogEntry(round=self.round, kind="end", result=self.winner))
        return self.winner