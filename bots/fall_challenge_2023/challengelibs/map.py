from typing import Dict

import numpy as np

from bots.fall_challenge_2023.singletons import D_MAX, HASH_MAP_NORMS, MAX_NUMBER_OF_RADAR_BLIPS_USED
from bots.fall_challenge_2023.challengelibs.asset import Unit, Creature, RadarBlip, MyDrone


def evaluate_positions_of_creatures(creatures: Dict[int, Creature], radar_blips: Dict[int, RadarBlip],
                                    my_drones: Dict[int, MyDrone], nb_turns: int,
                                    max_number_of_radar_blips_used=MAX_NUMBER_OF_RADAR_BLIPS_USED):

    # TODO : use zones lightened by drones to eliminates possible zones

    for creature_idt, creature in creatures.items():
        if not creature.visible:
            possible_zones = [creature.habitat]
            for drone_idt, drone in my_drones.items():
                radar_idt = hash((drone_idt, creature_idt))
                radar_blip = radar_blips[radar_idt]
                if radar_blip is not None:
                    radar_blip_zones = radar_blip.zones
                    n = min(len(radar_blip_zones), max_number_of_radar_blips_used)
                    for i in range(0, n):
                        possible_zones.append(radar_blip_zones[-i - 1])

            intersection = np.array(possible_zones)
            x_min = np.max(intersection[:, 0])
            y_min = np.max(intersection[:, 1])
            x_max = np.min(intersection[:, 2])
            y_max = np.min(intersection[:, 3])

            if creature.last_turn_visible:
                last_seen_turns = nb_turns - creature.last_turn_visible
                current_x_projection = creature.x + last_seen_turns * creature.vx
                current_y_projection = creature.y + last_seen_turns * creature.vy
                if (x_min <= current_x_projection <= x_max) and (y_min <= current_y_projection <= y_max):
                    creature.x = current_x_projection
                    creature.y = current_y_projection
                else:
                    creature.x = (x_min + x_max) / 2
                    creature.y = (y_min + y_max) / 2
            else:
                creature.x = (x_min + x_max) / 2
                creature.y = (y_min + y_max) / 2


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
