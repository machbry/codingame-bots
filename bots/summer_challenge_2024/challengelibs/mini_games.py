from typing import List

import numpy as np

from bots.summer_challenge_2024.challengelibs.actions import Action


class MiniGame:

    def __init__(self, inputs: List[str], player_idx: int):
        self.gpu = inputs[0]
        self.reg = np.array([int(inputs[1]),
                             int(inputs[2]),
                             int(inputs[3]),
                             int(inputs[4]),
                             int(inputs[5]),
                             int(inputs[6]),
                             int(inputs[7])])
        self.player_idx = player_idx

    def evaluate_action(self, action: Action) -> int:
        return 0


class HurdleRace(MiniGame):
    ACTIONS_MOVE = {Action.UP: 2,
                    Action.LEFT: 1,
                    Action.DOWN: 2,
                    Action.RIGHT: 3}

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

        if self.remaining_sections[move] == "#":
            return move - 6

        if action in [Action.DOWN, Action.RIGHT]:
            sections_crossed = self.remaining_sections[1:1+move]
            if "#" in sections_crossed:
                return len(sections_crossed.split("#")[0]) - 5

        return move
