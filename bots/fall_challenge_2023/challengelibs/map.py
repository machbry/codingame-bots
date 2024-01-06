from typing import Dict, List, Union
import math

import numpy as np
from scipy.sparse.csgraph import dijkstra

from botlibs.graph.classes import AdjacencyMatrix, Edge
from botlibs.graph.create import create_adjacency_matrix_from_edges
from botlibs.trigonometry import Vector, Point
from bots.fall_challenge_2023.singletons import HASH_MAP_NORM2, MAX_NUMBER_OF_RADAR_BLIPS_USED, DRONE_MAX_SPEED, \
    EMERGENCY_RADIUS2, SAFE_RADIUS_FROM_MONSTERS2, HASH_MAP_NORM, X_MIN, Y_MIN, X_MAX, Y_MAX, D_MAX, LIGHT_RADIUS2
from bots.fall_challenge_2023.challengelibs.asset import Creature, RadarBlip, MyDrone, Drone, Unit


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


def connect_units(units_to_connect: List[Unit], total_units_count: int, min_dist=800/D_MAX,
                  hash_map_norm=HASH_MAP_NORM, d_max=D_MAX, max_score=96) -> Union[None, AdjacencyMatrix]:

    nb_units_to_connect = len(units_to_connect)
    if nb_units_to_connect == 0:
        return None

    edges = []
    for i, unit in enumerate(units_to_connect):
        unit_value = unit.value if unit.value else 0
        nb_connected_neighbors = 0
        neighbors = units_to_connect.copy()
        neighbors.pop(i)
        if len(neighbors) > 0:
            ordered_neighbors = sorted(neighbors, key=lambda u: hash_map_norm[u.position - unit.position])
            while nb_connected_neighbors < len(ordered_neighbors):
                neighbor = ordered_neighbors[nb_connected_neighbors]
                nb_connected_neighbors += 1
                neighbor_value = neighbor.value
                if neighbor_value:
                    if neighbor_value > 0:
                        dist = max(hash_map_norm[neighbor.position - unit.position] / d_max, min_dist)
                        weight = dist / ((unit_value + neighbor_value) / max_score)
                        edges.append(Edge(from_node=unit.idt, to_node=neighbor.idt, directed=True, weight=weight))

    return create_adjacency_matrix_from_edges(edges=edges, nodes_number=total_units_count)


def optimized_next_target(drone: MyDrone, drone_target: Creature, creatures_connected_to_drone: List[Creature],
                          total_units_count: int):
    adjacency_matrix = connect_units(units_to_connect=[drone, *creatures_connected_to_drone],
                                     total_units_count=total_units_count)
    predecessors = dijkstra(adjacency_matrix.sparce_matrix, return_predecessors=True)[1]
    predecessor_idt = drone_target.idt
    while predecessor_idt != drone.idt:
        next_target_idt = predecessor_idt
        predecessor_idt = predecessors[drone.idt, next_target_idt]
    return next_target_idt


def optimize_path_with_targets(drone: MyDrone, first_target: Creature, final_target: Creature,
                               hash_map_norm=HASH_MAP_NORM) -> Point:
    vector_to_final_target = final_target.next_position - drone.position
    vector_to_first_target = first_target.next_position - drone.position
    cos = vector_to_final_target.dot(vector_to_first_target)

    if cos > 0:
        dist_to_final_target = hash_map_norm[vector_to_final_target]
        dist_to_first_target = hash_map_norm[vector_to_final_target]

        cos = min(cos / (dist_to_final_target * dist_to_first_target), 1)
        sin = math.sqrt(1 - cos ** 2)

        d_min = min(dist_to_first_target, dist_to_final_target)
        max_deviation = int(round(sin * d_min))
        if max_deviation > 1500:
            return first_target.next_position
        elif max_deviation > 750:
            return drone.position + (1/2) * (vector_to_final_target + vector_to_first_target)
        else:
            return final_target.next_position

    return first_target.next_position
