import numpy as np

from bots.fall_challenge_2023.challengelibs.asset import Creature, Drone
from bots.fall_challenge_2023.singletons import SCORE_BY_KIND, ACTIVATE_COLORS, \
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

    base_score_creatures = creatures_activated.sum()
    bonus_score_creatures = bonus_creatures_activated.sum()

    base_score_colors = colors_activated[completed_colors].sum()
    bonus_score_colors = score_for_full_color * colors_win_by[owned_colors_trophies].size

    base_score_kinds = kinds_activated[completed_kinds].sum()
    bonus_score_kinds = score_for_full_kind * kinds_win_by[owned_kinds_trophies].size

    return base_score_creatures + bonus_score_creatures + base_score_colors + bonus_score_colors + base_score_kinds + bonus_score_kinds
