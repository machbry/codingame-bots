from typing import List, Dict, Tuple

import numpy as np

from bots.fall_challenge_2023.challengelibs.asset import Score, Creature
from bots.fall_challenge_2023.singletons import SCORE_BY_KIND, ACTIVATE_COLORS, \
    SCORE_FOR_FULL_COLOR, SCORE_FOR_FULL_KIND, ACTIVATE_KINDS, EMPTY_ARRAY_CREATURES


def update_saved_scans(saved_creatures: np.ndarray, creature_color: int, creature_kind: int):
    creature_saved = saved_creatures[creature_color, creature_kind]
    if creature_saved == 1:
        return False
    saved_creatures[creature_color, creature_kind] = 1
    return True


def update_trophies(owner: int, saved_creatures: np.ndarray, newly_saved_creatures: np.ndarray,
                    creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray,
                    activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS,
                    score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):

    newly_completed_creatures = newly_saved_creatures == owner
    creatures_trophies_available = creatures_win_by == 0
    creatures_win_by[newly_completed_creatures & creatures_trophies_available] = owner

    completed_colors = saved_creatures.dot(activate_colors) == score_for_full_color
    colors_trophies_available = colors_win_by == 0
    colors_win_by[completed_colors & colors_trophies_available] = owner

    completed_kinds = activate_kinds.dot(saved_creatures) == score_for_full_kind
    kinds_trophies_available = kinds_win_by == 0
    kinds_win_by[completed_kinds & kinds_trophies_available] = owner


def compute_score(owner: int, saved_creatures: np.ndarray, creatures_win_by: np.ndarray,
                  colors_win_by: np.ndarray, kinds_win_by: np.ndarray, score_by_kind=SCORE_BY_KIND,
                  activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS,
                  score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):

    score = Score()

    creatures_activated = saved_creatures.dot(score_by_kind)

    bonus_saved_creatures = np.zeros_like(saved_creatures)
    bonus_saved_creatures[creatures_win_by == owner] = 1
    bonus_creatures_activated = bonus_saved_creatures.dot(score_by_kind)

    colors_activated = saved_creatures.dot(activate_colors)
    completed_colors = colors_activated == score_for_full_color
    owned_colors_trophies = colors_win_by == owner

    kinds_activated = activate_kinds.dot(saved_creatures)
    completed_kinds = kinds_activated == score_for_full_kind
    owned_kinds_trophies = kinds_win_by == owner

    score.base_creatures = creatures_activated.sum()
    score.bonus_creatures = bonus_creatures_activated.sum()

    score.base_colors = colors_activated[completed_colors].sum()
    score.bonus_colors = score_for_full_color * colors_win_by[owned_colors_trophies].size

    score.base_kinds = kinds_activated[completed_kinds].sum()
    score.bonus_kinds = score_for_full_kind * kinds_win_by[owned_kinds_trophies].size

    return score


class ScoreSimulation:
    __slots__ = ("simulation_scenario", "owners_saved_creatures", "creatures_win_by", "colors_win_by", "kinds_win_by",
                 "empty_array_creatures", "newly_saved_creatures", "owners_in_scenario", "simulation_done")

    def __init__(self, simulation_scenario: List[Tuple[int, List[Creature]]],
                 owners_saved_creatures: Dict[int, np.ndarray],
                 creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray):
        self.simulation_scenario = simulation_scenario
        self.owners_saved_creatures = {owner: saved_creatures.copy() for owner, saved_creatures
                                       in owners_saved_creatures.items()}
        self.creatures_win_by = creatures_win_by.copy()
        self.colors_win_by = colors_win_by.copy()
        self.kinds_win_by = kinds_win_by.copy()

        self.empty_array_creatures = EMPTY_ARRAY_CREATURES
        self.newly_saved_creatures = None
        self.owners_in_scenario = set()
        self.simulation_done = False

    def do_simulation(self):
        for owner, creatures_to_save in self.simulation_scenario:
            self.owners_in_scenario.add(owner)
            self.newly_saved_creatures = np.zeros_like(EMPTY_ARRAY_CREATURES)

            for creature in creatures_to_save:
                if update_saved_scans(self.owners_saved_creatures[owner], creature.color, creature.kind):
                    self.newly_saved_creatures[creature.color, creature.kind] = owner

            update_trophies(owner=owner, saved_creatures=self.owners_saved_creatures[owner],
                            newly_saved_creatures=self.newly_saved_creatures,
                            creatures_win_by=self.creatures_win_by, colors_win_by=self.colors_win_by,
                            kinds_win_by=self.kinds_win_by)

        self.simulation_done = True

    def compute_new_score(self):
        if not self.simulation_done:
            self.do_simulation()

        new_score_per_owner = {owner: compute_score(owner=owner,
                                                    saved_creatures=self.owners_saved_creatures[owner],
                                                    creatures_win_by=self.creatures_win_by,
                                                    colors_win_by=self.colors_win_by,
                                                    kinds_win_by=self.kinds_win_by)
                               for owner in self.owners_in_scenario}

        return new_score_per_owner

    def scans_and_trophies_after_simulation(self):
        if not self.simulation_done:
            self.do_simulation()

        return {'owners_saved_creatures': self.owners_saved_creatures,
                'creatures_win_by': self.creatures_win_by,
                'colors_win_by': self.colors_win_by,
                'kinds_win_by': self.kinds_win_by}

