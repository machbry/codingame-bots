from typing import Dict

from bots.fall_challenge_2023.singletons import D_MAX, HASH_MAP_NORMS
from bots.fall_challenge_2023.challengelibs.asset import Unit


def get_closest_unit_from(unit: Unit, other_units: Dict[int, Unit]):
    d_min = D_MAX
    closest_unit = None
    for other_unit_idt, other_unit in other_units.items():
        if unit.idt != other_unit.idt:
            try:
                unit_to_other_unit_vector = other_unit.position - unit.position
            except (AttributeError, TypeError):
                continue
            unit_to_other_unit_distance = HASH_MAP_NORMS[unit_to_other_unit_vector]
            if unit_to_other_unit_distance < d_min:
                d_min = unit_to_other_unit_distance
                closest_unit = other_unit
    return closest_unit
