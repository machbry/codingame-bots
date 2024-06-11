import sys
from typing import List, Dict

from bots.summer_challenge_2024.mini_games import HurdleRace, MiniGame


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "player_idx", "nb_mini_games", "mini_games")
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
            global_score, nb_gold_medals, nb_silver_medals, nb_bronze_medals = (int(i) for i in
                                                                                self.get_turn_input().split())

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

            for i in range(self.nb_mini_games):
                self.mini_games[i].play()
