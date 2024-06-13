import numpy as np
import sys
from enum import Enum
from typing import Dict, List

class Action(Enum):
    UP = 'UP'
    RIGHT = 'RIGHT'
    DOWN = 'DOWN'
    LEFT = 'LEFT'

class MiniGame:

    def __init__(self, inputs: List[str], player_idx: int):
        self.gpu = inputs[0]
        self.reg = np.array([int(inputs[1]), int(inputs[2]), int(inputs[3]), int(inputs[4]), int(inputs[5]), int(inputs[6]), int(inputs[7])])
        self.player_idx = player_idx

    def evaluate_action(self, action: Action) -> int:
        return 0

class HurdleRace(MiniGame):
    ACTIONS_MOVE = {Action.UP: 2, Action.LEFT: 1, Action.DOWN: 2, Action.RIGHT: 3}

    def __init__(self, inputs: List[str], player_idx: int):
        super().__init__(inputs, player_idx)
        self.player_position = self.reg[self.player_idx]
        self.player_stunned_for = self.reg[self.player_idx + 3]
        self.remaining_sections = self.gpu[self.player_position:30]

    def evaluate_action(self, action: Action) -> int:
        move = self.ACTIONS_MOVE[action]
        nb_remaining_sections = len(self.remaining_sections)
        if nb_remaining_sections <= move:
            return nb_remaining_sections
        if self.remaining_sections[move] == '#':
            return move - 6
        if action in [Action.DOWN, Action.RIGHT]:
            sections_crossed = self.remaining_sections[1:1 + move]
            if '#' in sections_crossed:
                return len(sections_crossed.split('#')[0]) - 5
        return move

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'player_idx', 'nb_mini_games', 'mini_games')
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.player_idx = int(self.get_init_input())
        self.nb_mini_games = int(self.get_init_input())
        self.mini_games: Dict[int, MiniGame] = {}
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
        for i in range(3):
            score_info = self.get_turn_input().split()
        for i in range(self.nb_mini_games):
            self.mini_games[i] = HurdleRace(inputs=self.get_turn_input().split(), player_idx=self.player_idx)
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
            actions_evaluations = {}
            for action in Action:
                for mini_game in self.mini_games.values():
                    action_evaluation = mini_game.evaluate_action(action)
                    if not actions_evaluations.get(action):
                        actions_evaluations[action] = 0
                    actions_evaluations[action] += action_evaluation
            best_action = None
            best_evaluation = None
            for action, action_evaluation in actions_evaluations.items():
                if not best_action:
                    best_action = action
                    best_evaluation = action_evaluation
                elif action_evaluation > best_evaluation:
                    best_action = action
                    best_evaluation = action_evaluation
            print(best_action.value)
GameLoop().start()