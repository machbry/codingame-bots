from typing import Dict, List, Union
import math

import numpy as np
from scipy.sparse.csgraph import dijkstra

from botlibs.graph.classes import AdjacencyMatrix, Edge
from botlibs.graph.create import create_adjacency_matrix_from_edges
from botlibs.trigonometry import Vector, Point
from bots.fall_challenge_2023.singletons import HASH_MAP_NORM2, MAX_NUMBER_OF_RADAR_BLIPS_USED, DRONE_MAX_SPEED, \
    EMERGENCY_RADIUS2, SAFE_RADIUS_FROM_MONSTERS2, HASH_MAP_NORM, X_MIN, Y_MIN, X_MAX, Y_MAX, D_MAX, LIGHT_RADIUS2, \
    MAP_GRID_STEP, MAP_INDICES, Y_ONES, X_ONES
from bots.fall_challenge_2023.challengelibs.asset import Creature, RadarBlip, MyDrone, Drone, Unit


def update_map_grid_zone_value(map_grid: np.ndarray, x_min: int = X_MIN, y_min: int = Y_MIN, x_max: int = X_MAX,
                               y_max: int = Y_MAX, value: int = 0, map_grip_step=MAP_GRID_STEP):
    map_grid[int(np.floor(y_min / map_grip_step)):int(np.ceil(y_max / map_grip_step)),
             int(np.floor(x_min / map_grip_step)):int(np.ceil(x_max / map_grip_step))] = value


def get_map_grid_value(map_grid: np.ndarray, x: int, y: int, map_grip_step=MAP_GRID_STEP):
    return map_grid[int(np.floor(y / map_grip_step)), int(np.floor(x / map_grip_step))]


def evaluate_positions_of_creatures(creatures: Dict[int, Creature], radar_blips: Dict[int, RadarBlip],
                                    my_drones: Dict[int, MyDrone], nb_turns: int,
                                    max_number_of_radar_blips_used=MAX_NUMBER_OF_RADAR_BLIPS_USED,
                                    trust_area_limit=LIGHT_RADIUS2, x_min=X_MIN, y_min=Y_MIN, x_max=X_MAX,
                                    y_max=Y_MAX, normal_light_radius=800, agumented_light_radius=2000,
                                    map_indices=MAP_INDICES, x_ones=X_ONES, y_ones=Y_ONES, map_grip_step=MAP_GRID_STEP):

    # TODO : add collisions with habitat limits to projections

    for creature_idt, creature in creatures.items():
        if not creature.visible:
            creature.trust_in_position = False
            possible_zones = [creature.habitat]

            current_excluded_zones = creature.excluded_zones.copy()
            creature.excluded_zones = []
            for current_excluded_zone in current_excluded_zones:  # TODO : take in account foe last scans
                new_x_min = current_excluded_zone[0] + normal_light_radius/2
                new_y_min = current_excluded_zone[1] + normal_light_radius/2
                new_x_max = current_excluded_zone[2] - normal_light_radius/2
                new_y_max = current_excluded_zone[3] - normal_light_radius/2

                if new_x_min < new_x_max and new_y_min < new_y_max:
                    creature.excluded_zones.append([new_x_min,
                                                    new_y_min,
                                                    new_x_max,
                                                    new_y_max])

            for drone_idt, drone in my_drones.items():
                radar_blip = radar_blips.get(hash((drone_idt, creature_idt)))
                if radar_blip is not None:
                    radar_blip_zones = radar_blip.zones
                    n = min(len(radar_blip_zones), max_number_of_radar_blips_used)
                    for i in range(0, n):
                        possible_zones.append(radar_blip_zones[-i - 1])

                light_radius = agumented_light_radius if drone.light_on else normal_light_radius
                x, y = drone.x, drone.y
                light_x_min = max(x - light_radius, x_min)
                light_y_min = max(y - light_radius, y_min)
                light_x_max = min(x + light_radius, x_max)
                light_y_max = min(y + light_radius, y_max)
                creature.excluded_zones.append([light_x_min, light_y_min, light_x_max, light_y_max])

            intersection = np.array(possible_zones)
            inter_x_min = np.max(intersection[:, 0])
            inter_y_min = np.max(intersection[:, 1])
            inter_x_max = np.min(intersection[:, 2])
            inter_y_max = np.min(intersection[:, 3])

            map_grid = creature.map_grid
            map_grid.fill(0)
            update_map_grid_zone_value(map_grid=map_grid, x_min=inter_x_min, y_min=inter_y_min, x_max=inter_x_max,
                                       y_max=inter_y_max, value=1)

            excluded_zones_in_intersection = False
            for excluded_zone in creature.excluded_zones:
                ex_x_min = excluded_zone[0]
                ex_y_min = excluded_zone[1]
                ex_x_max = excluded_zone[2]
                ex_y_max = excluded_zone[3]

                if (ex_x_min < inter_x_max and ex_y_min < inter_y_max) or (ex_x_max > inter_x_min and ex_y_max > inter_y_min):
                    excluded_zones_in_intersection = True
                    update_map_grid_zone_value(map_grid=map_grid, x_min=ex_x_min, y_min=ex_y_min, x_max=ex_x_max,
                                               y_max=ex_y_max, value=0)

            if excluded_zones_in_intersection:
                try:
                    x_bar = int(round(map_grip_step * x_ones.dot(map_grid).dot(map_indices)[0] / (x_ones.dot(map_grid).sum())))
                    y_bar = int(round(map_grip_step * map_indices.dot(map_grid.dot(y_ones))[0] / (map_grid.dot(y_ones).sum())))
                except ValueError:
                    x_bar = int(round((inter_x_min + inter_x_max) / 2))
                    y_bar = int(round((inter_y_min + inter_y_max) / 2))
            else:
                x_bar = int(round((inter_x_min + inter_x_max) / 2))
                y_bar = int(round((inter_y_min + inter_y_max) / 2))

            if creature.last_turn_visible:
                last_seen_turns = nb_turns - creature.last_turn_visible
                current_x_projection = creature.x + last_seen_turns * creature.vx
                current_y_projection = creature.y + last_seen_turns * creature.vy
                if (inter_x_min <= current_x_projection <= inter_x_max) and (inter_y_min <= current_y_projection <= inter_y_max):
                    if get_map_grid_value(map_grid, current_x_projection, current_y_projection) == 1:
                        creature.x = current_x_projection
                        creature.y = current_y_projection
                        creature.next_x = current_x_projection + creature.vx
                        creature.next_y = current_y_projection + creature.vy
                        creature.trust_in_position = True
                else:
                    creature.x = creature.next_x = x_bar
                    creature.y = creature.next_y = y_bar

                    if excluded_zones_in_intersection:
                        creature_area = map_grid.sum() * map_grip_step ** 2
                    else:
                        creature_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)

                    if creature_area < trust_area_limit:
                        creature.trust_in_position = True
            else:
                creature.x = creature.next_x = x_bar
                creature.y = creature.next_y = y_bar

                if excluded_zones_in_intersection:
                    creature_area = map_grid.sum() * map_grip_step ** 2
                else:
                    creature_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)

                if creature_area < trust_area_limit:
                    creature.trust_in_position = True

        else:
            creature.trust_in_position = True
            creature.excluded_zones = []
            creature.next_x = creature.x + creature.vx
            creature.next_y = creature.y + creature.vy


def evaluate_monsters_to_avoid(my_drones: Dict[int, MyDrone], monsters: List[Creature],
                               hash_map_norm2=HASH_MAP_NORM2, safe_radius_from_monsters=SAFE_RADIUS_FROM_MONSTERS2):
    for drone in my_drones.values():
        drone.has_to_avoid = []
        for monster in monsters:
            if monster.last_turn_visible:
                if monster.trust_in_position:
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

    b = 2 * (x * vx + y * vy)
    c = hash_map_norm2[Vector(x, y)] - collision_range
    delta = b ** 2 - 4 * a * c

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


def connect_units(units_to_connect: List[Unit], total_units_count: int, min_dist=800 / D_MAX,
                  hash_map_norm=HASH_MAP_NORM, d_max=D_MAX, max_value=96) -> Union[None, AdjacencyMatrix]:
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
                        weight = dist / ((unit_value + neighbor_value) / max_value)
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
            return drone.position + (1 / 2) * (vector_to_final_target + vector_to_first_target)
        else:
            return final_target.next_position

    return first_target.next_position
