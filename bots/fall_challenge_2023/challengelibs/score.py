from typing import List

from bots.fall_challenge_2023.challengelibs.asset import Creature, Scores, Drone
from bots.fall_challenge_2023.singletons import SCORE_BY_TYPE, SCORE_FOR_FULL_COLOR, SCORE_FOR_FULL_TYPE, \
    SCORE_MULTIPLIER_FIRST, MY_OWNER, FOE_OWNER
from bots.fall_challenge_2023.challengelibs.game_assets import GameAssets, AssetType


def order_drones_from_top_to_bottom(drones: List[Drone]) -> List[Drone]:
    return sorted(drones, key=lambda drone: drone.y)


def evaluate_extra_scores_for_creature(creature: Creature, current_scores: Scores, game_assets=GameAssets()) -> Scores:
    creature_kind = creature.kind
    if creature.kind == -1:
        return Scores(0, 0)

    if creature.escaped:
        return Scores(0, 0)

    creature_scanned_by = creature.scanned_by

    scanned_by_me = MY_OWNER in creature_scanned_by
    scanned_by_foe = FOE_OWNER in creature_scanned_by

    if scanned_by_me:
        if scanned_by_foe:
            return Scores(0, 0)
        my_extra_score = 0
        # EVALUATION POUR LES DRONES FOE UNIQUEMENT
        ordered_drones = order_drones_from_top_to_bottom(game_assets.get_all(asset_type=AssetType.FOEDRONE).values())
        foe_extra_score = SCORE_BY_TYPE[creature_kind]
    elif scanned_by_foe:
        foe_extra_score = 0
        # EVALUATION POUR MES DRONES UNIQUEMENT
        ordered_drones = order_drones_from_top_to_bottom(game_assets.get_all(asset_type=AssetType.MYDRONE).values())
        my_extra_score = SCORE_BY_TYPE[creature_kind]
    else:
        # EVALUATION POUR TOUS LES DRONES
        all_drones = [*game_assets.get_all(asset_type=AssetType.FOEDRONE).values(), *game_assets.get_all(asset_type=AssetType.MYDRONE).values()]
        ordered_drones = order_drones_from_top_to_bottom(all_drones) # TODO : SET AS ARGUMENT OF FUNCTION AND COMPUTE BEFORE

        # TODO : POUR CHAQUE DRONE SAUVEGARDE DES SCANS ET CALCUL DU SCORE SUPPLEMENTAIRE

        # EVALUATION DU SCORE SUPP SI SAUVEGARDE PAR MOI DU SCAN DE LA CREATURE
        my_extra_score = foe_extra_score = SCORE_BY_TYPE[creature_kind]

    return Scores(my_extra_score, foe_extra_score)
