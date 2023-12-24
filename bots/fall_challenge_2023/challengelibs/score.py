from typing import List

from bots.fall_challenge_2023.challengelibs.asset import Creature, Scores, Drone, Scan
from bots.fall_challenge_2023.singletons import SCORE_BY_TYPE, SCORE_FOR_FULL_COLOR, SCORE_FOR_FULL_TYPE, \
    SCORE_MULTIPLIER_FIRST, MY_OWNER, FOE_OWNER
from bots.fall_challenge_2023.challengelibs.game_assets import GameAssets, AssetType


def order_assets(drones: List[Drone], on_attr: str, ascending: bool = True) -> List[Drone]:
    return sorted(drones, key=lambda drone: getattr(drone, on_attr), reverse=not ascending)


def evaluate_extra_scores_for_creature(creature: Creature, scans: List[Scan]) -> Scores:
    creature_kind = creature.kind
    if creature.kind == -1:
        return Scores(0, 0)

    if creature.escaped:
        return Scores(0, 0)

    creature_scanned_by = creature.saved_by_owners

    scanned_by_me = MY_OWNER in creature_scanned_by
    scanned_by_foe = FOE_OWNER in creature_scanned_by

    if scanned_by_me:
        if scanned_by_foe:
            return Scores(0, 0)
        my_extra_score = 0

        foe_extra_score = SCORE_BY_TYPE[creature_kind]  # TODO : WIP
    elif scanned_by_foe:
        foe_extra_score = 0

        my_extra_score = SCORE_BY_TYPE[creature_kind]   # TODO : WIP
    else:
        # EVALUATION DU SCORE SUPP SI SAUVEGARDE PAR MOI OU FOE DU SCAN DE LA CREATURE
        my_extra_score = foe_extra_score = SCORE_BY_TYPE[creature_kind]  # TODO : WIP

    return Scores(my_extra_score, foe_extra_score)
