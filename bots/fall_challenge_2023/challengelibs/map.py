from typing import Dict, List

import numpy as np

from bots.fall_challenge_2023.challengelibs.act import Action
from bots.fall_challenge_2023.singletons import D_MAX, HASH_MAP_NORMS, MAX_NUMBER_OF_RADAR_BLIPS_USED, DRONE_MAX_SPEED, \
    EMERGENCY_RADIUS
from bots.fall_challenge_2023.challengelibs.asset import Unit, Creature, RadarBlip, MyDrone


def evaluate_positions_of_creatures(creatures: Dict[int, Creature], radar_blips: Dict[int, RadarBlip],
                                    my_drones: Dict[int, MyDrone], nb_turns: int,
                                    max_number_of_radar_blips_used=MAX_NUMBER_OF_RADAR_BLIPS_USED):

    # TODO : use zones lightened by drones to eliminates possible zones

    for creature_idt, creature in creatures.items():
        if not creature.visible:
            possible_zones = [creature.habitat]
            for drone_idt, drone in my_drones.items():
                radar_blip = radar_blips.get(hash((drone_idt, creature_idt)))
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

            creature.x = creature.next_x = (x_min + x_max) / 2
            creature.y = creature.next_y = (y_min + y_max) / 2

            if creature.last_turn_visible:
                last_seen_turns = nb_turns - creature.last_turn_visible
                current_x_projection = creature.x + last_seen_turns * creature.vx
                current_y_projection = creature.y + last_seen_turns * creature.vy
                if (x_min <= current_x_projection <= x_max) and (y_min <= current_y_projection <= y_max):
                    creature.x = current_x_projection
                    creature.y = current_y_projection
                    creature.next_x = current_x_projection + creature.vx
                    creature.next_y = current_y_projection + creature.vy

        else:
            creature.next_x = creature.x + creature.vx
            creature.next_y = creature.y + creature.vy


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


def avoid_monsters_while_aiming_for_an_action(drone: MyDrone, aimed_action: Action, monsters: List[Creature],
                                              nb_turns: int,
                                              hash_map_norms=HASH_MAP_NORMS, drone_max_speed=DRONE_MAX_SPEED,
                                              emergency_radius=EMERGENCY_RADIUS):

    # INIT
    monsters_positions = []
    target_position = aimed_action.target_position
    drone_to_target = target_position - drone.position

    # CHECK MONSTERS POSITIONS (CURRENT & NEXT)
    for monster in monsters:
        if monster.last_turn_visible:
            if nb_turns - monster.last_turn_visible <= 3:
                monsters_positions.extend([monster.position, monster.next_position])

    # TRY GO DIRECTLY TOWARDS THE TARGET
    distance_to_target = hash_map_norms[drone_to_target]
    if distance_to_target <= drone_max_speed:
        wanted_next_position = target_position
    else:
        wanted_next_position = drone.position + (drone_max_speed / distance_to_target) * drone_to_target

    # DANGER OF EMERGENCY ?
    future_emergency = False
    monsters_in_my_way = []
    for monster_position in monsters_positions:
        monster_in_my_way = hash_map_norms[monster_position - wanted_next_position] <= emergency_radius
        if monster_in_my_way:
            future_emergency = True
            monsters_in_my_way.append(monster_position)

    if not future_emergency:
        return aimed_action
    else:
        pass  # TRY ANOTHER NEXT_POSITION
