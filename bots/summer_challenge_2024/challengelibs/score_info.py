from typing import List

import numpy as np

from bots.summer_challenge_2024.singletons import NB_MINI_GAMES, NB_MEDALS_COLORS


class PlayerScoreInfo:
    SCORE_ARRAY = np.array([[3], [2], [1]])

    def __init__(self, inputs: List[str]):
        self.global_score = int(inputs[0])

        self.medals_counter = np.zeros(shape=(NB_MINI_GAMES, NB_MEDALS_COLORS))
        for g in range(NB_MINI_GAMES):
            for c in range(NB_MEDALS_COLORS):
                self.medals_counter[g, c] = inputs[g+c+1]

    def evaluate_additional_global_score(self, player_mini_games_results: np.ndarray):
        next_medals_counter = self.medals_counter + player_mini_games_results

        new_mini_games_scores = next_medals_counter.dot(self.SCORE_ARRAY)

        new_global_score = 1
        for i in range(NB_MINI_GAMES):
            new_global_score = new_global_score * new_mini_games_scores[i, 0]

        return new_global_score - self.global_score
