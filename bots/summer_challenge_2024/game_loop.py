import sys
from typing import List

import numpy as np

from bots.summer_challenge_2024.challengelibs.actions import Action
from bots.summer_challenge_2024.challengelibs.mini_games import HurdleRace, MiniGame, Archery, Roller, ArtisticDiving
from bots.summer_challenge_2024.challengelibs.score_info import PlayerScoreInfo
from bots.summer_challenge_2024.singletons import NB_MINI_GAMES, NB_MEDALS_COLORS, NB_PLAYERS


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "my_idx", "foes_idx", "nb_mini_games", "mini_games",
                 "players_scores")
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

                                my_action = my_mini_game_prio.best_next_action_for_player(self.my_idx,
                                                                                          my_mini_game_prio.gpu,
                                                                                          my_mini_game_prio.reg)
                                if turn == 0:
                                    my_first_action = my_action

                                foe_0_action = foe_0_mini_game_prio.best_next_action_for_player(self.foes_idx[0],
                                                                                                foe_0_mini_game_prio.gpu,
                                                                                                foe_0_mini_game_prio.reg)

                                foe_1_action = foe_1_mini_game_prio.best_next_action_for_player(self.foes_idx[1],
                                                                                                foe_1_mini_game_prio.gpu,
                                                                                                foe_1_mini_game_prio.reg)

                                for mini_game in current_simulation_mini_games:

                                    current_gpu = mini_game.gpu
                                    current_reg = mini_game.reg.copy()

                                    next_gpu, next_reg = mini_game.next_gpu_reg_with_player_action(self.my_idx,
                                                                                                   my_action,
                                                                                                   current_gpu,
                                                                                                   current_reg)

                                    next_gpu, next_reg = mini_game.next_gpu_reg_with_player_action(self.foes_idx[0],
                                                                                                   foe_0_action,
                                                                                                   current_gpu,
                                                                                                   next_reg)

                                    next_gpu, next_reg = mini_game.next_gpu_reg_with_player_action(self.foes_idx[1],
                                                                                                   foe_1_action,
                                                                                                   current_gpu,
                                                                                                   next_reg)

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

