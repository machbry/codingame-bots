import sys
from typing import List, Dict

from bots.summer_challenge_2024.challengelibs.actions import Action
from bots.summer_challenge_2024.challengelibs.mini_games import HurdleRace, MiniGame
from bots.summer_challenge_2024.challengelibs.score_info import ScoreInfo


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "player_idx", "nb_mini_games", "mini_games",
                 "players_scores")
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.player_idx = int(self.get_init_input())
        self.nb_mini_games = int(self.get_init_input())
        self.mini_games: List[MiniGame] = []
        self.players_scores: List[ScoreInfo] = []

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

        self.players_scores = [ScoreInfo(inputs=self.get_turn_input().split(), nb_mini_games=self.nb_mini_games)
                               for i in range(3)]

        self.mini_games = [HurdleRace(inputs=self.get_turn_input().split(), player_idx=self.player_idx,
                                      players_scores=self.players_scores) for i in range(self.nb_mini_games)]

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

            scores_evolutions = {}
            for action in Action:
                for mini_game in self.mini_games:
                    score_evolution = mini_game.average_score_evolution_expected(action)
                    if not scores_evolutions.get(action):
                        scores_evolutions[action] = 0
                    scores_evolutions[action] += score_evolution

            best_action = None
            best_score_evolution = None

            for action, score_evolution in scores_evolutions.items():
                if not best_action:
                    best_action = action
                    best_score_evolution = score_evolution
                else:
                    if score_evolution > best_score_evolution:
                        best_action = action
                        best_score_evolution = score_evolution

            print(best_action.value)
