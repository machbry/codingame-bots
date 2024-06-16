import sys
from typing import List

import numpy as np

from bots.summer_challenge_2024.challengelibs.actions import Action
from bots.summer_challenge_2024.challengelibs.mini_games import HurdleRace, MiniGame, Archery, Roller, ArtisticDiving
from bots.summer_challenge_2024.challengelibs.score_info import PlayerScoreInfo
from bots.summer_challenge_2024.singletons import NB_MINI_GAMES, NB_MEDALS_COLORS


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "my_idx", "nb_mini_games", "mini_games",
                 "players_scores")
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.my_idx = int(self.get_init_input())
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

        self.mini_games = [HurdleRace(inputs=self.get_turn_input().split(), my_idx=self.my_idx),
                           Archery(inputs=self.get_turn_input().split(), my_idx=self.my_idx),
                           Roller(inputs=self.get_turn_input().split(), my_idx=self.my_idx),
                           ArtisticDiving(inputs=self.get_turn_input().split(), my_idx=self.my_idx)]

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

            # TODO : create Simulator
            best_action = None
            max_additional_score = None

            for action in Action:
                my_mini_games_results = np.zeros(shape=(NB_MINI_GAMES, NB_MEDALS_COLORS))
                for i, mini_game in enumerate(self.mini_games):
                    my_mini_game_results = mini_game.mini_game_results_after_player_action(self.my_idx, action)[self.my_idx]
                    my_mini_games_results[i, :] = my_mini_game_results
                additional_score = self.players_scores[self.my_idx].evaluate_additional_global_score(my_mini_games_results)
                if not best_action:
                    best_action = action
                    max_additional_score = additional_score
                elif additional_score > max_additional_score:
                    best_action = action
                    max_additional_score = additional_score

            print(best_action.value)

