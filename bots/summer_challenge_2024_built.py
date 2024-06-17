import sys
import math
import random
import numpy as np
from enum import Enum
from typing import Callable, Any, Dict, List, Tuple

class Action(Enum):
    UP = 'UP'
    RIGHT = 'RIGHT'
    DOWN = 'DOWN'
    LEFT = 'LEFT'

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if isinstance(other, Point):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, nombre):
        return Point(nombre * self.x, nombre * self.y)

    def __rmul__(self, nombre):
        return self * nombre

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __round__(self, n=None):
        return Point(round(self.x, n), round(self.y, n))

    def dist(self, point):
        return math.dist([self.x, self.y], [point.x, point.y])

class Vector(Point):

    def __init__(self, x, y):
        super().__init__(x, y)

    def __mul__(self, nombre):
        return Vector(nombre * self.x, nombre * self.y)

    def __round__(self, n=None):
        return Vector(round(self.x, n), round(self.y, n))

    def dot(self, vector):
        return self.x * vector.x + self.y * vector.y

    @property
    def norm2(self):
        return self.dot(self)

    @property
    def norm(self):
        return math.sqrt(self.norm2)
NB_PLAYERS = 3
NB_MINI_GAMES = 4
NB_MEDALS_COLORS = 3
DEFAULT_MINI_GAMES_RESULTS = np.ones(shape=(NB_MINI_GAMES, NB_MEDALS_COLORS)) / 3

class MiniGame:
    __slots__ = ('gpu', 'reg', 'my_idx')

    def __init__(self, inputs: List[str]=None, my_idx: int=None):
        if inputs:
            self.gpu = inputs[0]
            self.reg = np.array([int(inputs[1]), int(inputs[2]), int(inputs[3]), int(inputs[4]), int(inputs[5]), int(inputs[6]), int(inputs[7])])
        self.my_idx = my_idx

    def copy(self):
        mini_game_copy = MiniGame()
        mini_game_copy.gpu = self.gpu
        mini_game_copy.reg = self.reg.copy()
        mini_game_copy.my_idx = self.my_idx
        return mini_game_copy

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) -> Tuple[str, np.ndarray]:
        return (current_gpu, current_reg.copy())

    def best_next_action_for_player(self, player_idx: int, current_gpu: str, current_reg: np.ndarray) -> Action:
        return random.choice([action for action in Action])

    def predict_players_mini_game_results_with_gpu_reg(self, gpu: str, reg: np.ndarray) -> List[np.ndarray]:
        player_mini_games_results = []
        for player_idx in range(NB_PLAYERS):
            mini_games_results = DEFAULT_MINI_GAMES_RESULTS[0, :]
            player_mini_games_results.append(mini_games_results)
        return player_mini_games_results

class HurdleRace(MiniGame):
    ACTIONS_MOVE = {Action.UP: 2, Action.LEFT: 1, Action.DOWN: 2, Action.RIGHT: 3}

    def copy(self):
        mini_game_copy = HurdleRace()
        mini_game_copy.gpu = self.gpu
        mini_game_copy.reg = self.reg.copy()
        mini_game_copy.my_idx = self.my_idx
        return mini_game_copy

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) -> Tuple[str, np.ndarray]:
        next_gpu = current_gpu
        next_reg = current_reg.copy()
        if current_gpu == 'GAME_OVER':
            return (next_gpu, next_reg)
        player_stunned_for = current_reg[player_idx + NB_PLAYERS]
        if player_stunned_for > 0:
            next_reg[player_idx + NB_PLAYERS] = player_stunned_for - 1
            return (next_gpu, next_reg)
        player_position = current_reg[player_idx]
        remaining_sections = current_gpu[player_position:30]
        move_qty = self.ACTIONS_MOVE[action]
        nb_remaining_sections = len(remaining_sections)
        if nb_remaining_sections <= move_qty:
            next_reg[player_idx] = player_position + nb_remaining_sections - 1
            next_gpu = 'GAME_OVER'
            return (next_gpu, next_reg)
        if action == Action.UP and remaining_sections[move_qty] == '#':
            next_reg[player_idx] = player_position + move_qty
            next_reg[player_idx + NB_PLAYERS] = 3
            return (next_gpu, next_reg)
        sections_crossed = remaining_sections[1:1 + move_qty]
        if action in [Action.LEFT, Action.DOWN, Action.RIGHT] and '#' in sections_crossed:
            next_reg[player_idx] = player_position + len(sections_crossed.split('#')[0]) + 1
            next_reg[player_idx + NB_PLAYERS] = 3
            return (next_gpu, next_reg)
        next_reg[player_idx] = player_position + move_qty
        next_reg[player_idx + NB_PLAYERS] = 0
        return (next_gpu, next_reg)

    def best_next_action_for_player(self, player_idx: int, current_gpu: str, current_reg: np.ndarray) -> Action:
        best_action = None
        max_action_eval = None
        for action in Action:
            next_gpu, next_reg = self.next_gpu_reg_with_player_action(player_idx, action, current_gpu, current_reg)
            action_eval = next_reg[player_idx] - next_reg[player_idx + NB_PLAYERS]
            if not best_action or action_eval > max_action_eval:
                best_action = action
                max_action_eval = action_eval
        return best_action

    def predict_players_mini_game_results_with_gpu_reg(self, gpu: str, reg: np.ndarray) -> List[np.ndarray]:
        players_mini_game_results = []
        players_positions_sorted = sorted(reg[0:3])
        min_position = players_positions_sorted[0]
        middle_position = players_positions_sorted[1]
        max_position = players_positions_sorted[2]
        game_completion = max_position / 29
        p = game_completion * (2 / 3)
        q = p / 2
        for player_idx in range(NB_PLAYERS):
            player_mini_game_results = DEFAULT_MINI_GAMES_RESULTS[0, :].copy()
            player_position = reg[player_idx]
            if player_position == max_position:
                player_mini_game_results = player_mini_game_results + np.array([p, -q, -q])
            elif player_position == middle_position:
                player_mini_game_results = player_mini_game_results + np.array([-q, p, -q])
            elif player_position == min_position:
                player_mini_game_results = player_mini_game_results + np.array([-q, -q, p])
            players_mini_game_results.append(player_mini_game_results)
        return players_mini_game_results

class Archery(MiniGame):
    ACTIONS_VECTOR = {Action.UP: Vector(0, -1), Action.LEFT: Vector(-1, 0), Action.DOWN: Vector(0, 1), Action.RIGHT: Vector(1, 0)}

    def copy(self):
        mini_game_copy = Archery()
        mini_game_copy.gpu = self.gpu
        mini_game_copy.reg = self.reg.copy()
        mini_game_copy.my_idx = self.my_idx
        return mini_game_copy

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) -> Tuple[str, np.ndarray]:
        next_gpu = current_gpu
        next_reg = current_reg.copy()
        if current_gpu == 'GAME_OVER':
            return (next_gpu, next_reg)
        player_position = Point(current_reg[2 * player_idx], current_reg[2 * player_idx + 1])
        player_next_position = player_position + int(current_gpu[0]) * self.ACTIONS_VECTOR[action]
        next_reg[2 * player_idx] = max(min(player_next_position.x, 20), -20)
        next_reg[2 * player_idx + 1] = max(min(player_next_position.y, 20), -20)
        next_gpu = next_gpu[1:len(next_gpu)]
        if not next_gpu:
            next_gpu = 'GAME_OVER'
        return (next_gpu, next_reg)

    def best_next_action_for_player(self, player_idx: int, current_gpu: str, current_reg: np.ndarray) -> Action:
        best_action = None
        min_action_eval = None
        for action in Action:
            next_gpu, next_reg = self.next_gpu_reg_with_player_action(player_idx, action, current_gpu, current_reg)
            action_eval = Vector(next_reg[2 * player_idx], next_reg[2 * player_idx + 1]).norm2
            if not best_action or action_eval < min_action_eval:
                best_action = action
                min_action_eval = action_eval
        return best_action

    def predict_players_mini_game_results_with_gpu_reg(self, gpu: str, reg: np.ndarray) -> List[np.ndarray]:
        players_mini_game_results = []
        players_distance_to_middle = [Vector(reg[2 * p], reg[2 * p + 1]).norm2 for p in range(NB_PLAYERS)]
        players_distance_to_middle_sorted = sorted(players_distance_to_middle)
        min_distance = players_distance_to_middle_sorted[0]
        middle_distance = players_distance_to_middle_sorted[1]
        max_distance = players_distance_to_middle_sorted[2]
        game_completion = max((10 - len(gpu)) / 10, 0)
        p = game_completion * (2 / 3)
        q = p / 2
        for player_idx in range(NB_PLAYERS):
            player_mini_game_results = DEFAULT_MINI_GAMES_RESULTS[0, :].copy()
            player_distance = players_distance_to_middle[player_idx]
            if player_distance == min_distance:
                player_mini_game_results = player_mini_game_results + np.array([p, -q, -q])
            elif player_distance == middle_distance:
                player_mini_game_results = player_mini_game_results + np.array([-q, p, -q])
            elif player_distance == max_distance:
                player_mini_game_results = player_mini_game_results + np.array([-q, -q, p])
            players_mini_game_results.append(player_mini_game_results)
        return players_mini_game_results

class Roller(MiniGame):
    ACTIONS_LETTER = {Action.UP: 'U', Action.LEFT: 'L', Action.DOWN: 'D', Action.RIGHT: 'R'}
    LETTERS_ACTION = {'U': Action.UP, 'L': Action.LEFT, 'D': Action.DOWN, 'R': Action.RIGHT}

    def copy(self):
        mini_game_copy = Roller()
        mini_game_copy.gpu = self.gpu
        mini_game_copy.reg = self.reg.copy()
        mini_game_copy.my_idx = self.my_idx
        return mini_game_copy

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) -> Tuple[str, np.ndarray]:
        next_gpu = current_gpu
        next_reg = current_reg.copy()
        if current_gpu == 'GAME_OVER':
            return (next_gpu, next_reg)
        turns_left = current_reg[6]
        if turns_left == 0:
            next_gpu = 'GAME_OVER'
            return (next_gpu, next_reg)
        player_risk = current_reg[player_idx + NB_PLAYERS]
        if player_risk < 0:
            next_reg[player_idx + NB_PLAYERS] = player_risk + 1
            return (next_gpu, next_reg)
        player_movement = current_reg[player_idx]
        action_letter = self.ACTIONS_LETTER[action]
        if action_letter == current_gpu[0]:
            next_reg[player_idx] = player_movement + 1
            if player_risk > 0:
                next_reg[player_idx + NB_PLAYERS] = player_risk - 1
        if action_letter == current_gpu[1]:
            next_reg[player_idx] = player_movement + 2
        if action_letter == current_gpu[2]:
            next_reg[player_idx] = player_movement + 2
            if player_risk > 0:
                next_reg[player_idx + NB_PLAYERS] = player_risk + 1
        if action_letter == current_gpu[3]:
            next_reg[player_idx] = player_movement + 3
            if player_risk > 0:
                next_reg[player_idx + NB_PLAYERS] = player_risk + 2
        if player_risk >= 5:
            next_reg[player_idx + NB_PLAYERS] = -2
        next_reg[6] = turns_left - 1
        return (next_gpu, next_reg)

    def best_next_action_for_player(self, player_idx: int, current_gpu: str, current_reg: np.ndarray) -> Action:
        if current_gpu == 'GAME_OVER':
            return random.choice([action for action in Action])
        return self.LETTERS_ACTION[current_gpu[1]]

    def predict_players_mini_game_results_with_gpu_reg(self, gpu: str, reg: np.ndarray) -> List[np.ndarray]:
        players_mini_game_results = []
        players_movement_sorted = sorted(reg[0:3])
        min_movement = players_movement_sorted[0]
        middle_movement = players_movement_sorted[1]
        max_movement = players_movement_sorted[2]
        game_completion = 1 - reg[6] / 15
        p = game_completion * (2 / 3)
        q = p / 2
        for player_idx in range(NB_PLAYERS):
            player_mini_game_results = DEFAULT_MINI_GAMES_RESULTS[0, :].copy()
            player_movement = reg[player_idx]
            if player_movement == max_movement:
                player_mini_game_results = player_mini_game_results + np.array([p, -q, -q])
            elif player_movement == middle_movement:
                player_mini_game_results = player_mini_game_results + np.array([-q, p, -q])
            elif player_movement == min_movement:
                player_mini_game_results = player_mini_game_results + np.array([-q, -q, p])
            players_mini_game_results.append(player_mini_game_results)
        return players_mini_game_results

class ArtisticDiving(MiniGame):
    ACTIONS_LETTER = {Action.UP: 'U', Action.LEFT: 'L', Action.DOWN: 'D', Action.RIGHT: 'R'}
    LETTERS_ACTION = {'U': Action.UP, 'L': Action.LEFT, 'D': Action.DOWN, 'R': Action.RIGHT}

    def copy(self):
        mini_game_copy = ArtisticDiving()
        mini_game_copy.gpu = self.gpu
        mini_game_copy.reg = self.reg.copy()
        mini_game_copy.my_idx = self.my_idx
        return mini_game_copy

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) -> Tuple[str, np.ndarray]:
        next_gpu = current_gpu
        next_reg = current_reg.copy()
        if current_gpu == 'GAME_OVER':
            return (next_gpu, next_reg)
        player_points = current_reg[player_idx]
        player_combo = current_reg[player_idx + NB_PLAYERS]
        action_letter = self.ACTIONS_LETTER[action]
        if action_letter == current_gpu[0]:
            next_reg[player_idx + NB_PLAYERS] = player_combo + 1
            next_reg[player_idx] = player_points + player_combo + 1
        else:
            next_reg[player_idx + NB_PLAYERS] = 0
        next_gpu = next_gpu[1:len(next_gpu)]
        if not next_gpu:
            next_gpu = 'GAME_OVER'
        return (next_gpu, next_reg)

    def best_next_action_for_player(self, player_idx: int, current_gpu: str, current_reg: np.ndarray) -> Action:
        if current_gpu == 'GAME_OVER':
            return random.choice([action for action in Action])
        return self.LETTERS_ACTION[current_gpu[0]]

    def predict_players_mini_game_results_with_gpu_reg(self, gpu: str, reg: np.ndarray) -> List[np.ndarray]:
        players_mini_game_results = []
        players_points_sorted = sorted(reg[0:3])
        min_points = players_points_sorted[0]
        middle_points = players_points_sorted[1]
        max_points = players_points_sorted[2]
        game_completion = max((15 - len(gpu)) / 15, 0)
        p = game_completion * (2 / 3)
        q = p / 2
        for player_idx in range(NB_PLAYERS):
            player_mini_game_results = DEFAULT_MINI_GAMES_RESULTS[0, :].copy()
            player_points = reg[player_idx]
            if player_points == max_points:
                player_mini_game_results = player_mini_game_results + np.array([p, -q, -q])
            elif player_points == middle_points:
                player_mini_game_results = player_mini_game_results + np.array([-q, p, -q])
            elif player_points == min_points:
                player_mini_game_results = player_mini_game_results + np.array([-q, -q, p])
            players_mini_game_results.append(player_mini_game_results)
        return players_mini_game_results

class PlayerScoreInfo:
    SCORE_ARRAY = np.array([[3], [2], [1]])

    def __init__(self, inputs: List[str]):
        self.global_score = int(inputs[0])
        self.medals_counter = np.zeros(shape=(NB_MINI_GAMES, NB_MEDALS_COLORS))
        for g in range(NB_MINI_GAMES):
            for c in range(NB_MEDALS_COLORS):
                self.medals_counter[g, c] = inputs[g + c + 1]

    def evaluate_additional_global_score(self, player_mini_games_results: np.ndarray):
        next_medals_counter = self.medals_counter + player_mini_games_results
        new_mini_games_scores = next_medals_counter.dot(self.SCORE_ARRAY)
        new_global_score = 1
        for i in range(NB_MINI_GAMES):
            new_global_score = new_global_score * new_mini_games_scores[i, 0]
        return new_global_score - self.global_score

    def current_mini_game_score(self, mini_game_idx):
        return self.medals_counter.dot(self.SCORE_ARRAY)[mini_game_idx, 0]

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'my_idx', 'foes_idx', 'nb_mini_games', 'mini_games', 'players_scores')
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.my_idx = int(self.get_init_input())
        self.foes_idx = [i for i in range(NB_PLAYERS) if i != self.my_idx]
        self.nb_mini_games = int(self.get_init_input())
        self.mini_games: List[MiniGame] = []
        self.players_scores: List[PlayerScoreInfo] = []
        if GameLoop.LOG:
            self.print_init_logs()

    def get_init_input(self):
        result = input()
        self.init_inputs.append(result)
        return result

    def get_turn_input(self):
        result = input()
        self.turns_inputs.append(result)
        return result

    def update_assets(self):
        self.nb_turns += 1
        self.players_scores = [PlayerScoreInfo(inputs=self.get_turn_input().split()) for i in range(3)]
        self.mini_games = [HurdleRace(inputs=self.get_turn_input().split(), my_idx=self.my_idx), Archery(inputs=self.get_turn_input().split(), my_idx=self.my_idx), Roller(inputs=self.get_turn_input().split(), my_idx=self.my_idx), ArtisticDiving(inputs=self.get_turn_input().split(), my_idx=self.my_idx)]
        if GameLoop.LOG:
            self.print_turn_logs()

    def print_init_logs(self):
        print(self.init_inputs, file=sys.stderr, flush=True)

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()
            max_mini_game_prio_eval = None
            my_best_first_action = None
            initial_mini_games = [mini_game.copy() for mini_game in self.mini_games]
            for m in range(self.nb_mini_games):
                mini_game_prio_evals = []
                current_mini_game_score = self.players_scores[self.my_idx].current_mini_game_score(m)
                if current_mini_game_score > 0:
                    for f0 in range(self.nb_mini_games):
                        for f1 in range(self.nb_mini_games):
                            current_simulation_mini_games = [mini_game.copy() for mini_game in initial_mini_games]
                            my_mini_game_prio = current_simulation_mini_games[m]
                            foe_0_mini_game_prio = current_simulation_mini_games[f0]
                            foe_1_mini_game_prio = current_simulation_mini_games[f1]
                            for turn in range(3):
                                my_action = my_mini_game_prio.best_next_action_for_player(self.my_idx, my_mini_game_prio.gpu, my_mini_game_prio.reg)
                                if turn == 0:
                                    my_first_action = my_action
                                foe_0_action = foe_0_mini_game_prio.best_next_action_for_player(self.foes_idx[0], foe_0_mini_game_prio.gpu, foe_0_mini_game_prio.reg)
                                foe_1_action = foe_1_mini_game_prio.best_next_action_for_player(self.foes_idx[1], foe_1_mini_game_prio.gpu, foe_1_mini_game_prio.reg)
                                for mini_game in current_simulation_mini_games:
                                    current_gpu = mini_game.gpu
                                    current_reg = mini_game.reg.copy()
                                    next_gpu, next_reg = mini_game.next_gpu_reg_with_player_action(self.my_idx, my_action, current_gpu, current_reg)
                                    next_gpu, next_reg = mini_game.next_gpu_reg_with_player_action(self.foes_idx[0], foe_0_action, current_gpu, next_reg)
                                    next_gpu, next_reg = mini_game.next_gpu_reg_with_player_action(self.foes_idx[1], foe_1_action, current_gpu, next_reg)
                                    mini_game.gpu = next_gpu
                                    mini_game.reg = next_reg
                            my_mini_games_results = np.zeros(shape=(NB_MINI_GAMES, NB_MEDALS_COLORS))
                            for i, mini_game in enumerate(self.mini_games):
                                my_mini_game_results = mini_game.predict_players_mini_game_results_with_gpu_reg(mini_game.gpu, mini_game.reg)[self.my_idx]
                                my_mini_games_results[i, :] = my_mini_game_results
                            mini_game_prio_evals.append(self.players_scores[self.my_idx].evaluate_additional_global_score(my_mini_games_results))
                    mini_game_prio_eval = sum(mini_game_prio_evals) / len(mini_game_prio_evals)
                    if not my_best_first_action or mini_game_prio_eval > max_mini_game_prio_eval:
                        max_mini_game_prio_eval = mini_game_prio_eval
                        my_best_first_action = my_first_action
            if not my_best_first_action:
                best_mini_game = initial_mini_games[3]
                my_best_first_action = best_mini_game.best_next_action_for_player(self.my_idx, best_mini_game.gpu, best_mini_game.reg)
            print(my_best_first_action.value)
GameLoop().start()