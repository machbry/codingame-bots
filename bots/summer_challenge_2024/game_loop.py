import sys
from typing import List


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "player_idx", "nb_games")
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.player_idx = int(self.get_init_input())
        self.nb_games = int(self.get_init_input())

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
            score_info = self.get_turn_input()
        for i in range(self.nb_games):
            inputs = self.get_turn_input().split()
            gpu = inputs[0]
            reg_0 = int(inputs[1])
            reg_1 = int(inputs[2])
            reg_2 = int(inputs[3])
            reg_3 = int(inputs[4])
            reg_4 = int(inputs[5])
            reg_5 = int(inputs[6])
            reg_6 = int(inputs[7])

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

            print("LEFT")
