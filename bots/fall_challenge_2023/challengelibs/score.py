from typing import List

import numpy as np

from bots.fall_challenge_2023.challengelibs.asset import Creature, Drone
from bots.fall_challenge_2023.singletons import SCORE_BY_KIND, SCORE_MULTIPLIER_FIRST, ACTIVATE_COLORS, \
    SCORE_FOR_FULL_COLOR, SCORE_FOR_FULL_KIND, ACTIVATE_KINDS


def update_saved_scans(saved_creatures: np.ndarray, creature_color: int, creature_kind: int):
    creature_saved = saved_creatures[creature_color, creature_kind]
    if creature_saved == 1:
        return False
    saved_creatures[creature_color, creature_kind] = 1
    return True


def update_unsaved_scan(drone: Drone, creature: Creature):
    drone.unsaved_creatures_idt.add(creature.idt)
    creature.scanned_by_drones.add(drone.idt)


def update_trophies(owner: int, saved_creatures: np.ndarray, newly_saved_creatures: np.ndarray,
                    creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray):

    newly_completed_creatures = newly_saved_creatures == owner
    creatures_trophies_available = creatures_win_by == 0
    creatures_win_by[newly_completed_creatures & creatures_trophies_available] = owner

    completed_colors = saved_creatures.dot(ACTIVATE_COLORS) == SCORE_FOR_FULL_COLOR
    colors_trophies_available = colors_win_by == 0
    colors_win_by[completed_colors & colors_trophies_available] = owner

    completed_kinds = ACTIVATE_KINDS.dot(saved_creatures) == SCORE_FOR_FULL_KIND
    kinds_trophies_available = kinds_win_by == 0
    kinds_win_by[completed_kinds & kinds_trophies_available] = owner


def evaluate_extra_score_for_owner_creature(creature_kind: int, creature_escaped: bool,
                                            creature_saved_by_owners: List[int], owner: int):
    if creature_kind == -1:
        return 0

    if creature_escaped:
        return 0

    if owner in creature_saved_by_owners:
        return 0

    if len(creature_saved_by_owners) > 0:
        return SCORE_BY_KIND[creature_kind]
    else:
        return SCORE_MULTIPLIER_FIRST * SCORE_BY_KIND[creature_kind]
