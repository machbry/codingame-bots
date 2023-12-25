from typing import List

from bots.fall_challenge_2023.challengelibs.asset import Asset
from bots.fall_challenge_2023.singletons import SCORE_BY_TYPE, SCORE_FOR_FULL_COLOR, SCORE_FOR_FULL_TYPE, \
    SCORE_MULTIPLIER_FIRST


def order_assets(drones: List[Asset], on_attr: str, ascending: bool = True):
    return sorted(drones, key=lambda drone: getattr(drone, on_attr), reverse=not ascending)


def evaluate_extra_score_for_owner_creature(creature_kind: int, creature_escaped: bool,
                                            creature_saved_by_owners: List[int], owner: int):
    if creature_kind == -1:
        return 0

    if creature_escaped:
        return 0

    if owner in creature_saved_by_owners:
        return 0

    if len(creature_saved_by_owners) > 0:
        return SCORE_BY_TYPE[creature_kind]
    else:
        return SCORE_MULTIPLIER_FIRST * SCORE_BY_TYPE[creature_kind]
