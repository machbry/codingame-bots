from typing import List

from bots.fall_challenge_2023.challengelibs.asset import Scores, Asset
from bots.fall_challenge_2023.singletons import SCORE_BY_TYPE, SCORE_FOR_FULL_COLOR, SCORE_FOR_FULL_TYPE, \
    SCORE_MULTIPLIER_FIRST


def order_assets(drones: List[Asset], on_attr: str, ascending: bool = True):
    return sorted(drones, key=lambda drone: getattr(drone, on_attr), reverse=not ascending)


def evaluate_extra_score_for_owner_creature(creature_kind: int, creature_escaped: bool, creature_saved_by_owner: bool,
                                            creature_saved_by_other_owner: bool):
    if creature_kind == -1:
        return 0

    if creature_escaped:
        return 0

    if creature_saved_by_owner:
        return 0

    if creature_saved_by_other_owner:
        return SCORE_BY_TYPE[creature_kind]
    else:
        return SCORE_MULTIPLIER_FIRST * SCORE_BY_TYPE[creature_kind]
