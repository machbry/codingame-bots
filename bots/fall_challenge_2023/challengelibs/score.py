from typing import List, Dict

import numpy as np

from bots.fall_challenge_2023.challengelibs.asset import KindsTrophy, ColorsTrophy
from bots.fall_challenge_2023.singletons import SCORE_BY_KIND, SCORE_MULTIPLIER_FIRST, COLORS, ACTIVATE_COLORS, \
    SCORE_FOR_FULL_COLOR, SCORE_FOR_FULL_KIND, ACTIVATE_KINDS, KINDS


def update_trophies(owner: int, saved_creatures: np.ndarray, colors_trophies: Dict[int, ColorsTrophy],
                    kinds_trophies: Dict[int, KindsTrophy]):
    for color in COLORS[saved_creatures.dot(ACTIVATE_COLORS) == SCORE_FOR_FULL_COLOR]:
        colors_trophy = colors_trophies[color]
        color_win_by_owners = colors_trophy.win_by_owners
        if owner not in color_win_by_owners:
            color_win_by_owners.append(owner)

    for kind in KINDS[ACTIVATE_KINDS.dot(saved_creatures) == SCORE_FOR_FULL_KIND]:
        kinds_trophy = kinds_trophies[kind]
        kind_win_by_owners = kinds_trophy.win_by_owners
        if owner not in kind_win_by_owners:
            kind_win_by_owners.append(owner)


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
