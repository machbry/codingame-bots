from typing import List, Dict
import math

import numpy as np

from botlibs.trigonometry import Vector, Point
from bots.fall_challenge_2023.challengelibs.act import Action
from bots.fall_challenge_2023.challengelibs.asset import Drone, Creature, MyDrone, Asset
from bots.fall_challenge_2023.challengelibs.map import is_next_position_safe, get_drone_next_position_with_target
from bots.fall_challenge_2023.singletons import HASH_MAP_NORM2, AUGMENTED_LIGHT_RADIUS, MY_OWNER, FOE_OWNER, ROTATE_2D_MATRIX


def use_light_to_find_a_target(drone: Drone, target: Creature, hash_map_norm2=HASH_MAP_NORM2,
                               augmented_light_radius=AUGMENTED_LIGHT_RADIUS):
    battery = drone.battery
    if battery >= 10 and drone.y > 4000:
        return True
    if drone.battery >= 5:
        distance_to_target = hash_map_norm2[target.position - drone.position]
        if distance_to_target <= augmented_light_radius and not target.visible:
            return True
    return False


def save_points(my_drones: Dict[int, MyDrone], owners_scores: Dict[int, int], owners_max_possible_score: Dict[int, int],
                owners_extra_score_with_all_unsaved_creatures: Dict[int, int], my_owner=MY_OWNER, foe_owner=FOE_OWNER):
    actions = {}

    extra_score_to_win = owners_max_possible_score[foe_owner] - owners_scores[my_owner] + 1  # TODO : bonus scores are shared
    extra_score_if_all_my_drones_save = owners_extra_score_with_all_unsaved_creatures[my_owner]

    if extra_score_if_all_my_drones_save >= extra_score_to_win:
        for drone in my_drones.values():
            if len(drone.unsaved_creatures_idt) > 0:
                actions[drone.idt] = Action(target=Point(drone.x, 499),
                                            comment=f"SAVE {extra_score_if_all_my_drones_save} ({extra_score_to_win})")

    else:
        ordered_my_drones_with_most_extra_score = order_assets(my_drones.values(),
                                                               on_attr='extra_score_with_unsaved_creatures',
                                                               ascending=False)
        for drone in ordered_my_drones_with_most_extra_score:
            drone_extra_score = drone.extra_score_with_unsaved_creatures
            if drone_extra_score >= 20 or drone_extra_score >= extra_score_to_win:
                actions[drone.idt] = Action(target=Point(drone.x, 499),
                                            comment=f"SAVE {drone.extra_score_with_unsaved_creatures} ({extra_score_to_win})")

    return actions


def find_valuable_target(my_drones: Dict[int, MyDrone], creatures: Dict[int, Creature]):
    actions = {}

    ordered_creatures_with_most_extra_score = order_assets(creatures.values(), on_attr='my_extra_score',
                                                           ascending=False)
    creatures_with_extra_score = [creature for creature in ordered_creatures_with_most_extra_score if
                                  creature.my_extra_score > 0]
    nb_creatures_with_extra_score = len(creatures_with_extra_score)

    if nb_creatures_with_extra_score == 1:
        drone_target = ordered_creatures_with_most_extra_score[0]
        for drone_idt, drone in my_drones.items():
            light = use_light_to_find_a_target(drone, drone_target)
            actions[drone_idt] = Action(target=drone_target, light=light,
                                        comment=f"FIND {drone_target.log()}")

    elif nb_creatures_with_extra_score > 1:
        x_median = np.median([creature.x for creature in creatures_with_extra_score])

        creatures_with_extra_score_left = [creature for creature in creatures_with_extra_score if
                                           creature.x <= x_median]
        creatures_with_extra_score_right = [creature for creature in creatures_with_extra_score if
                                            creature.x > x_median]

        left_target = creatures_with_extra_score_left[0]
        if len(creatures_with_extra_score_right) == 0:
            right_target = creatures_with_extra_score_left[1]
            if left_target.x > right_target.x:
                left_target = creatures_with_extra_score_left[1]
                right_target = creatures_with_extra_score_left[0]
        else:
            right_target = creatures_with_extra_score_right[0]

        my_drones_from_left_to_right = order_assets(my_drones.values(), 'x')
        drone_left_idt = my_drones_from_left_to_right[0].idt
        drone_right_idt = my_drones_from_left_to_right[-1].idt

        drone_left = my_drones.get(drone_left_idt)
        if drone_left is not None:
            light = use_light_to_find_a_target(drone_left, left_target)
            actions[drone_left_idt] = Action(target=left_target, light=light,
                                             comment=f"FIND {left_target.log()}")

        drone_right = my_drones.get(drone_right_idt)
        if drone_right is not None:
            light = use_light_to_find_a_target(drone_right, right_target)
            actions[drone_right_idt] = Action(target=right_target, light=light,
                                              comment=f"FIND {right_target.log()}")

    return actions


def just_do_something(my_drones: Dict[int, MyDrone], creatures: Dict[int, Creature]):
    actions = {}

    nb_find_actions = 0
    for drone_idt, drone in my_drones.items():
        if drone.extra_score_with_unsaved_creatures > 0:
            actions[drone.idt] = Action(target=Point(drone.x, 499),
                                        comment=f"SAVE {drone.extra_score_with_unsaved_creatures}")
        else:
            drone_target = order_assets(creatures.values(), on_attr='foe_extra_score', ascending=False)[
                nb_find_actions]
            nb_find_actions += 1
            actions[drone.idt] = Action(target=drone_target, light=True,
                                        comment=f"FIND {drone_target.log()}")

    return actions


def avoid_monsters(drone: MyDrone, aimed_action: Action, default_action: Action, hash_map_norm2=HASH_MAP_NORM2,
                   rotate_matrix=ROTATE_2D_MATRIX, theta_increment=math.pi/8):

    safe_action = aimed_action
    drone_has_to_avoid = drone.has_to_avoid

    if len(drone.has_to_avoid) == 0:
        return safe_action

    target_position = aimed_action.target_position
    drone_next_position = get_drone_next_position_with_target(drone, target_position)

    if is_next_position_safe(drone, drone_next_position):
        return safe_action

    if len(drone_has_to_avoid) > 0:
        speed_wanted = Vector(drone.vx, drone.vy)

        thetas = [theta for theta in np.arange(theta_increment, math.pi + theta_increment, theta_increment)]
        for theta in thetas:
            next_positions_to_try = [drone.position + round(rotate_matrix.rotate_vector(speed_wanted, theta)),
                                     drone.position + round(rotate_matrix.rotate_vector(speed_wanted, -theta))]

            next_positions_to_try = sorted(next_positions_to_try, key=lambda p: hash_map_norm2[target_position - p])

            for next_position in next_positions_to_try:
                if is_next_position_safe(drone, next_position):
                    safe_action.target = next_position
                    return safe_action

    return default_action


def order_assets(assets: List[Asset], on_attr: str, ascending: bool = True):
    return sorted(assets, key=lambda asset: getattr(asset, on_attr), reverse=not ascending)
