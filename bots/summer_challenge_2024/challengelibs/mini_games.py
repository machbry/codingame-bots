from typing import List, Tuple

import numpy as np

from botlibs.trigonometry import Vector, Point
from bots.summer_challenge_2024.challengelibs.actions import Action
from bots.summer_challenge_2024.singletons import NB_PLAYERS, DEFAULT_MINI_GAMES_RESULTS


class MiniGame:

    def __init__(self, inputs: List[str], my_idx: int):
        self.gpu = inputs[0]
        self.reg = np.array([int(inputs[1]),
                             int(inputs[2]),
                             int(inputs[3]),
                             int(inputs[4]),
                             int(inputs[5]),
                             int(inputs[6]),
                             int(inputs[7])])
        self.my_idx = my_idx

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) \
            -> Tuple[str, np.ndarray]:
        return current_gpu, current_reg.copy()

    def predict_players_mini_game_results_with_gpu_reg(self, gpu: str, reg: np.ndarray) -> List[np.ndarray]:
        player_mini_games_results = []
        for player_idx in range(NB_PLAYERS):
            mini_games_results = DEFAULT_MINI_GAMES_RESULTS[0, :]
            player_mini_games_results.append(mini_games_results)

        return player_mini_games_results

    def mini_game_results_after_player_action(self, player_idx: int, action: Action) -> List[np.ndarray]:
        current_gpu = self.gpu
        current_reg = self.reg.copy()

        for t in range(3):
            for p in range(NB_PLAYERS):
                if p == player_idx and t == 0:
                    next_gpu, next_reg = self.next_gpu_reg_with_player_action(p, action, current_gpu, current_reg)
                else:
                    next_gpus_regs = [self.next_gpu_reg_with_player_action(p, a, current_gpu, current_reg) for a in Action]
                    next_reg = sum([r for g, r in next_gpus_regs]) / len(Action)
                    next_reg = next_reg.round(0).astype(int)
                current_reg = next_reg.copy()
            current_gpu = next_gpus_regs[0][0]
            # TODO : prendre en compte collisions possibles pour le Roller

        return self.predict_players_mini_game_results_with_gpu_reg(next_gpu, next_reg)


class HurdleRace(MiniGame):
    ACTIONS_MOVE = {Action.UP: 2,
                    Action.LEFT: 1,
                    Action.DOWN: 2,
                    Action.RIGHT: 3}

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) \
            -> Tuple[str, np.ndarray]:
        next_gpu = current_gpu
        next_reg = current_reg.copy()

        if current_gpu == "GAME_OVER":
            return next_gpu, next_reg

        # player is stunned
        player_stunned_for = current_reg[player_idx + NB_PLAYERS]
        if player_stunned_for > 0:
            next_reg[player_idx + NB_PLAYERS] = player_stunned_for - 1
            return next_gpu, next_reg

        player_position = current_reg[player_idx]
        remaining_sections = current_gpu[player_position:30]

        move_qty = self.ACTIONS_MOVE[action]
        nb_remaining_sections = len(remaining_sections)

        # player will reach the end
        if nb_remaining_sections <= move_qty:
            next_reg[player_idx] = player_position + nb_remaining_sections - 1
            next_gpu = "GAME_OVER"
            return next_gpu, next_reg

        # player hurts a hurdle after a jump
        if action == Action.UP and remaining_sections[move_qty] == '#':
            next_reg[player_idx] = player_position + move_qty
            next_reg[player_idx + NB_PLAYERS] = 3
            return next_gpu, next_reg

        # player hurst a hurdle in his way
        sections_crossed = remaining_sections[1:1 + move_qty]
        if action in [Action.LEFT, Action.DOWN, Action.RIGHT] and '#' in sections_crossed:
            next_reg[player_idx] = player_position + len(sections_crossed.split("#")[0]) + 1
            next_reg[player_idx + NB_PLAYERS] = 3
            return next_gpu, next_reg

        next_reg[player_idx] = player_position + move_qty
        next_reg[player_idx + NB_PLAYERS] = 0
        return next_gpu, next_reg

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
                player_mini_game_results = player_mini_game_results + np.array([p, - q, - q])
            elif player_position == middle_position:
                player_mini_game_results = player_mini_game_results + np.array([- q, p, - q])
            elif player_position == min_position:
                player_mini_game_results = player_mini_game_results + np.array([- q, - q, p])

            players_mini_game_results.append(player_mini_game_results)

        return players_mini_game_results


class Archery(MiniGame):
    ACTIONS_VECTOR = {Action.UP: Vector(0, -1),
                      Action.LEFT: Vector(-1, 0),
                      Action.DOWN: Vector(0, 1),
                      Action.RIGHT: Vector(1, 0)}

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) \
            -> Tuple[str, np.ndarray]:
        next_gpu = current_gpu
        next_reg = current_reg.copy()

        if current_gpu == "GAME_OVER":
            return next_gpu, next_reg

        player_position = Point(current_reg[2 * player_idx], current_reg[2 * player_idx + 1])
        player_next_position = player_position + int(current_gpu[0]) * self.ACTIONS_VECTOR[action]

        next_reg[2 * player_idx] = max(min(player_next_position.x, 20), -20)
        next_reg[2 * player_idx + 1] = max(min(player_next_position.y, 20), -20)

        next_gpu = next_gpu[1:len(next_gpu)]
        if not next_gpu:
            next_gpu = "GAME_OVER"

        return next_gpu, next_reg

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
                player_mini_game_results = player_mini_game_results + np.array([p, - q, - q])
            elif player_distance == middle_distance:
                player_mini_game_results = player_mini_game_results + np.array([- q, p, - q])
            elif player_distance == max_distance:
                player_mini_game_results = player_mini_game_results + np.array([- q, - q, p])

            players_mini_game_results.append(player_mini_game_results)

        return players_mini_game_results


class Roller(MiniGame):
    ACTIONS_LETTER = {Action.UP: "U",
                      Action.LEFT: "L",
                      Action.DOWN: "D",
                      Action.RIGHT: "R"}

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) \
            -> Tuple[str, np.ndarray]:
        next_gpu = current_gpu
        next_reg = current_reg.copy()

        if current_gpu == "GAME_OVER":
            return next_gpu, next_reg

        turns_left = current_reg[6]
        if turns_left == 0:
            next_gpu = "GAME_OVER"
            return next_gpu, next_reg

        player_risk = current_reg[player_idx + NB_PLAYERS]
        if player_risk < 0:
            next_reg[player_idx + NB_PLAYERS] = player_risk + 1
            return next_gpu, next_reg

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

        return next_gpu, next_reg

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
                player_mini_game_results = player_mini_game_results + np.array([p, - q, - q])
            elif player_movement == middle_movement:
                player_mini_game_results = player_mini_game_results + np.array([- q, p, - q])
            elif player_movement == min_movement:
                player_mini_game_results = player_mini_game_results + np.array([- q, - q, p])

            players_mini_game_results.append(player_mini_game_results)

        return players_mini_game_results


class ArtisticDiving(MiniGame):
    ACTIONS_LETTER = {Action.UP: "U",
                      Action.LEFT: "L",
                      Action.DOWN: "D",
                      Action.RIGHT: "R"}

    def next_gpu_reg_with_player_action(self, player_idx: int, action: Action, current_gpu: str, current_reg: np.ndarray) \
            -> Tuple[str, np.ndarray]:
        next_gpu = current_gpu
        next_reg = current_reg.copy()

        if current_gpu == "GAME_OVER":
            return next_gpu, next_reg

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
            next_gpu = "GAME_OVER"

        return next_gpu, next_reg

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
                player_mini_game_results = player_mini_game_results + np.array([p, - q, - q])
            elif player_points == middle_points:
                player_mini_game_results = player_mini_game_results + np.array([- q, p, - q])
            elif player_points == min_points:
                player_mini_game_results = player_mini_game_results + np.array([- q, - q, p])

            players_mini_game_results.append(player_mini_game_results)

        return players_mini_game_results
