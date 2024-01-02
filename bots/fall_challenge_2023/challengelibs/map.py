from typing import Dict, List
import math

import numpy as np

from botlibs.trigonometry import Vector, Point
from bots.fall_challenge_2023.singletons import HASH_MAP_NORM2, MAX_NUMBER_OF_RADAR_BLIPS_USED, DRONE_MAX_SPEED, \
    EMERGENCY_RADIUS2, SAFE_RADIUS_FROM_MONSTERS2, HASH_MAP_NORM, X_MIN, Y_MIN, X_MAX, Y_MAX
from bots.fall_challenge_2023.challengelibs.asset import Creature, RadarBlip, MyDrone, Drone


def evaluate_positions_of_creatures(creatures: Dict[int, Creature], radar_blips: Dict[int, RadarBlip],
                                    my_drones: Dict[int, MyDrone], nb_turns: int,
                                    max_number_of_radar_blips_used=MAX_NUMBER_OF_RADAR_BLIPS_USED):

    # TODO : use zones lightened by drones to eliminates possible zones
    # TODO : add collisions with limits & others to projections

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


def evaluate_monsters_to_avoid(my_drones: Dict[int, MyDrone], monsters: List[Creature], nb_turns: int,
                               hash_map_norm2=HASH_MAP_NORM2, safe_radius_from_monsters=SAFE_RADIUS_FROM_MONSTERS2):
    for drone in my_drones.values():
        drone.has_to_avoid = []
        for monster in monsters:
            if monster.last_turn_visible:
                if nb_turns - monster.last_turn_visible <= 3:
                    if hash_map_norm2[monster.position - drone.position] <= safe_radius_from_monsters:
                        drone.has_to_avoid.append(monster)


def is_collision(drone: Drone, monster: Creature, collision_range=EMERGENCY_RADIUS2, hash_map_norm2=HASH_MAP_NORM2):
    xm, ym, xd, yd = monster.x, monster.y, drone.x, drone.y
    x, y = xm - xd, ym - yd
    vx, vy = monster.vx - drone.vx, monster.vy - drone.vy

    # Resolving: sqrt((x + t * vx) ^ 2 + (y + t * vy) ^ 2) = radius <= > t ^ 2 * (vx ^ 2 + vy ^ 2) + t * 2 * (
    #             x * vx + y * vy) + x ^ 2 + y ^ 2 - radius ^ 2 = 0
    # at ^ 2 + bt + c = 0;
    # a = vx ^ 2 + vy ^ 2
    # b = 2 * (x * vx + y * vy)
    # c = x ^ 2 + y ^ 2 - radius ^ 2

    a = hash_map_norm2[Vector(vx, vy)]

    if a <= 0:
        return False

    b = 2*(x * vx + y * vy)
    c = hash_map_norm2[Vector(x, y)] - collision_range
    delta = b**2 - 4 * a * c

    if delta < 0:
        return False

    t = (-b - math.sqrt(delta)) / (2 * a)

    if t <= 0:
        return False

    if t > 1:
        return False

    return True


def get_drone_next_position_with_target(drone: MyDrone, target_position: Point, drone_max_speed=DRONE_MAX_SPEED,
                                        hash_map_norm=HASH_MAP_NORM):
    drone_to_target = target_position - drone.position
    distance_to_target = hash_map_norm[drone_to_target]
    if distance_to_target <= drone_max_speed:
        return round(target_position)
    else:
        return round((drone_max_speed / distance_to_target) * drone_to_target) + drone.position


def is_next_position_safe(drone: MyDrone, next_position: Point,
                          x_min=X_MIN, y_min=Y_MIN, x_max=X_MAX, y_max=Y_MAX):
    next_x, next_y = next_position.x, next_position.y

    drone.vx = next_x - drone.x
    drone.vy = next_y - drone.y

    if next_x < x_min or next_x > x_max or next_y < y_min or next_y > y_max:
        return False

    is_safe = True
    for monster in drone.has_to_avoid:
        if is_collision(drone, monster):
            is_safe = False

    return is_safe
