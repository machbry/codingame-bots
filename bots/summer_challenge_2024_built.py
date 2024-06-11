import sys
import numpy as np
from enum import Enum
from typing import List, Dict

class Action(Enum):
    UP = 'UP'
    RIGHT = 'RIGHT'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    PASS = 'PASS'

class MiniGame:

    def __init__(self, inputs: List[str], player_idx: int):
        self.gpu = inputs[0]
        self.reg_0 = int(inputs[1])
        self.reg_1 = int(inputs[2])
        self.reg_2 = int(inputs[3])
        self.reg_3 = int(inputs[4])
        self.reg_4 = int(inputs[5])
        self.reg_5 = int(inputs[6])
        self.reg_6 = int(inputs[7])
        self.player_idx = player_idx

class HurdleRace(MiniGame):

    def __init__(self, inputs: List[str], player_idx: int):
        super().__init__(inputs, player_idx)
        self.player_position = [self.reg_0, self.reg_1, self.reg_2][self.player_idx]
        self.player_stunned_for = [self.reg_3, self.reg_4, self.reg_5][self.player_idx]
        self.safe_sections = [len(safe_section) for safe_section in self.gpu[self.player_position:30].split('#')]

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
            current_sections = []
            for i in range(self.nb_mini_games):
                mini_game: HurdleRace = self.mini_games[i]
                if mini_game.player_stunned_for == 0 and mini_game.gpu != 'GAME_OVER':
                    current_section = mini_game.safe_sections[0]
                    if current_section == 0:
                        try:
                            next_section = mini_game.safe_sections[1]
                            current_sections.append(next_section)
                        except IndexError:
                            pass
                    else:
                        current_sections.append(current_section)
            if current_sections:
                min_len = min(current_sections)
                if min_len > 3:
                    print(Action.RIGHT.value)
                elif min_len == 3:
                    print(Action.DOWN.value)
                elif min_len == 2:
                    print(Action.LEFT.value)
                elif min_len == 1:
                    if current_sections.count(1) >= current_sections.count(2):
                        print(Action.UP.value)
                    else:
                        print(Action.LEFT.value)
                else:
                    print(Action.LEFT.value)
            else:
                print(Action.LEFT.value)
GameLoop().start()