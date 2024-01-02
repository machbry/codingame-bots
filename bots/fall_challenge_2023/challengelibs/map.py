from typing import Dict, List
import math
import sys

import numpy as np

from bots.fall_challenge_2023.challengelibs.act import Action
from bots.fall_challenge_2023.singletons import D_MAX, HASH_MAP_NORMS, MAX_NUMBER_OF_RADAR_BLIPS_USED, DRONE_MAX_SPEED, \
    EMERGENCY_RADIUS, SAFE_RADIUS_FROM_MONSTERS
from bots.fall_challenge_2023.challengelibs.asset import Unit, Creature, RadarBlip, MyDrone, Drone


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
                    creature.x = creature.next_x = round((x_min + x_max) / 2)
                    creature.y = creature.next_y = round((y_min + y_max) / 2)
            else:
                creature.x = creature.next_x = round((x_min + x_max) / 2)
                creature.y = creature.next_y = round((y_min + y_max) / 2)

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


def is_collision(drone: Drone, monster: Creature, collision_range=EMERGENCY_RADIUS):
    xm, ym, xd, yd = monster.x, monster.y, drone.x, drone.y
    x, y = xm - xd, ym - yd
    vx, vy = monster.vx - drone.vx, monster.vy - drone.vy

    a = vx**2 + vy**2

    if a <= 0:
        return False

    b = 2*(x * vx + y * vy)
    c = x**2 + y**2 - collision_range
    delta = b**2 - 4 * a * c

    if delta < 0:
        return False

    t = (-b - math.sqrt(delta)) / (2 * a)

    if t <= 0:
        return False

    if t > 1:
        return False

    return True


def is_action_safe(drone: MyDrone, aimed_action: Action, monsters: List[Creature], nb_turns: int,
                   hash_map_norms=HASH_MAP_NORMS, drone_max_speed=DRONE_MAX_SPEED,
                   safe_radius_from_monsters=SAFE_RADIUS_FROM_MONSTERS):

    # INIT
    target_position = aimed_action.target_position
    drone_to_target = target_position - drone.position
    drone.has_to_avoid = []

    # CHECK MONSTERS POSITIONS (CURRENT & NEXT)
    for monster in monsters:
        if monster.last_turn_visible:
            if nb_turns - monster.last_turn_visible <= 3:
                if hash_map_norms[monster.position - drone.position] <= safe_radius_from_monsters:
                    drone.has_to_avoid.append(monster)

    # TRY GO DIRECTLY TOWARDS THE TARGET
    distance_to_target = hash_map_norms[drone_to_target]
    if distance_to_target <= drone_max_speed:
        wanted_next_position = round(target_position)
    else:
        wanted_next_position = drone.position + round(((drone_max_speed / distance_to_target) ** (1/2)) * drone_to_target)

    drone.vx = wanted_next_position.x - drone.x
    drone.vy = wanted_next_position.y - drone.y

    # DANGER OF EMERGENCY ?
    safe_action = True
    for monster in drone.has_to_avoid:
        if is_collision(drone, monster):
            safe_action = False

    return safe_action
