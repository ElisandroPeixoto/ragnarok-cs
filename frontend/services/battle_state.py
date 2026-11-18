import copy
import random
from services.battle_geometry import BoardConfig
from services.battle_log import BattleLog, LogEntry

TURN_DURATION = 30

# Columns where each team can spawn; the row is random
SPAWN_COLUMNS = {"player": (0,), "enemy": (7, 8, 9)}
SPAWN_FACING = {"player": "se", "enemy": "nw"}


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
    def __init__(self, units: dict, skills: dict, board: BoardConfig, monsters: list[dict] | None = None,
                 turn_duration: int = TURN_DURATION):
        """units (the hero), skills and monsters (3 to 6, already rolled) come from the backend
        (BattleService.start_battle); positions are rolled here. The battle ends when the hero kills
        every monster (victory) or dies (defeat)."""
        self.units = copy.deepcopy(units)
        self.skills = skills
        self.board = board
        for unit in self.units.values():
            place_unit(unit, set(board.blocked_tiles), board)
        # the hero acts first; monsters are appended in the order they arrive
        self.turn_order: list[str] = list(self.units)
        self.turn_index : int = 0
        self.round : int = 1
        self.spawn_monsters(monsters or [])
        self.turn_duration: int = turn_duration
        self.time_left = turn_duration
        self.winner: str | None = None
        self.log = BattleLog()
        self.damage_popups: list[dict] = []   # floating damage numbers (see battle_animation.damage_popup)
        # What the hero did, for the log and the result screen. EXP is only paid by the backend on victory
        self.kills: list[str] = []            # names of the monsters the hero killed
        self.exp_pending = 0                  # EXP of those kills (shown in the log; paid only if the hero wins)
        self.damage_taken = 0                 # damage the hero received
        self.monster_names = {unit_id: unit["name"] for unit_id, unit in self.units.items() if unit["team"] == "enemy"}
        self.monster_damage = {unit_id: 0 for unit_id in self.monster_names}   # damage the hero dealt to each one
        self.finishing = False                # the end of the battle is being processed (battle_page.finish_battle)

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
        """Runs when a new round starts (the hero is next): clears the dead monsters from the board."""
        for unit_id in [uid for uid, unit in self.units.items() if unit["team"] == "enemy" and unit["hp"] <= 0]:
            del self.units[unit_id]
            self.turn_order.remove(unit_id)

    def spawn_monsters(self, monsters: list[dict]) -> None:
        """Puts the hunt's monsters on free enemy tiles (ids monster_1, monster_2... in the given order)."""
        taken = set(self.board.blocked_tiles) | {(u["col"], u["row"]) for u in self.units.values() if u["hp"] > 0}
        for number, monster in enumerate(monsters, start=1):
            unit = copy.deepcopy(monster)
            if not place_unit(unit, taken, self.board):
                break   # enemy columns are full
            unit_id = f"monster_{number}"
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
        """Defeat when the player's team is dead; victory when every monster is dead. (Leaving by the button
        ends the battle without a result.)"""
        if self.winner is None:
            player_alive = any(u["team"] == "player" and u["hp"] > 0 for u in self.units.values())
            enemy_alive = any(u["team"] == "enemy" and u["hp"] > 0 for u in self.units.values())
            if not player_alive:
                self.winner = "defeat"
            elif not enemy_alive:
                self.winner = "victory"
            if self.winner:
                self.log.add(LogEntry(round=self.round, kind="end", result=self.winner))
        return self.winner

    def damage_report(self) -> list[dict]:
        """[{"name", "damage"}] for every monster of the hunt, in spawn order; repeated names get " 1", " 2"..."""
        report = [{"name": self.monster_names[unit_id], "damage": damage}
                  for unit_id, damage in self.monster_damage.items()]
        counts = {}
        for entry in report:
            counts[entry["name"]] = counts.get(entry["name"], 0) + 1
        seen = {}
        for entry in report:
            if counts[entry["name"]] > 1:
                seen[entry["name"]] = seen.get(entry["name"], 0) + 1
                entry["name"] = f"{entry['name']} {seen[entry['name']]}"
        return report