from typing import List

import numpy as np


class ScoreInfo:
    SCORE_ARRAY = np.array([[3], [2], [1]])

    def __init__(self, inputs: List[str], nb_mini_games: int):
        self.nb_mini_games = nb_mini_games
        self.global_score = int(inputs[0])

        self.medals_counter = np.zeros(shape=(nb_mini_games, 3))
        for i in range(self.nb_mini_games):
            for j in range(3):
                self.medals_counter[i, j] = inputs[i+j+1]

    def evaluate_additional_global_score(self, mini_games_results: np.ndarray):
        next_medals_counter = self.medals_counter + mini_games_results

        new_mini_games_scores = next_medals_counter.dot(self.SCORE_ARRAY)

        new_global_score = 1
        for i in range(self.nb_mini_games):
            new_global_score = new_global_score * new_mini_games_scores[i, 0]

        return new_global_score - self.global_score
