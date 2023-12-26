from typing import List

from bots.fall_challenge_2023.singletons import SCORE_BY_KIND, SCORE_MULTIPLIER_FIRST


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
