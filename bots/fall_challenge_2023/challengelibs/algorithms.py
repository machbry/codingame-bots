from typing import List, Dict, Union
import math

import numpy as np

from botlibs.trigonometry import Vector, Point
from bots.fall_challenge_2023.challengelibs.act import Action
from bots.fall_challenge_2023.challengelibs.asset import Drone, Creature, MyDrone, Asset, Score
from bots.fall_challenge_2023.challengelibs.map import is_next_position_safe, get_drone_next_position_with_target, \
    optimized_next_target, optimize_path_with_targets
from bots.fall_challenge_2023.singletons import HASH_MAP_NORM2, AUGMENTED_LIGHT_RADIUS2, MY_OWNER, FOE_OWNER, \
    ROTATE_2D_MATRIX, Kind, LIMIT_DISTANCE_FROM_EDGE_TO_DENY, X_MAX, SCARE_FROM_DISTANCE, LIMIT_DISTANCE_TO_DENY2, \
    DRONE_MAX_SPEED


def use_light_to_find_a_target(drone: Drone, target: Creature, hash_map_norm2=HASH_MAP_NORM2,
                               augmented_light_radius=AUGMENTED_LIGHT_RADIUS2):
    battery = drone.battery
    if battery >= 10 and drone.y > 4000:
        return True
    if drone.battery >= 5:
        distance_to_target = hash_map_norm2[target.position - drone.position]
        if distance_to_target <= augmented_light_radius and not target.visible:
            return True
    return False


def save_points(my_drones: Dict[int, MyDrone], owners_scores_computed: Dict[int, Score],
                owners_max_possible_score: Dict[int, Score],
                owners_extra_score_with_all_unsaved_creatures: Dict[int, Score],
                owners_bonus_score_left: Dict[int, Dict[str, int]],
                my_owner=MY_OWNER, foe_owner=FOE_OWNER):
    actions = {}

    my_total_max_score = owners_max_possible_score[my_owner].total

    my_max_possible_unshared = owners_max_possible_score[my_owner].base + owners_scores_computed[my_owner].bonus + \
                               owners_bonus_score_left[my_owner]["unshared"]  # M
    foe_max_possible_unshared = owners_max_possible_score[foe_owner].base + owners_scores_computed[foe_owner].bonus + \
                                owners_bonus_score_left[foe_owner]["unshared"]  # F
    bonus_shared_left = owners_bonus_score_left[my_owner]["shared"]  # S
    # M + X > F + Y = F + S - X
    # X + Y = S
    X = (bonus_shared_left + foe_max_possible_unshared - my_max_possible_unshared) / 2
    Y = bonus_shared_left - X
    my_extra_score_to_win = foe_max_possible_unshared + Y - owners_scores_computed[my_owner].total + 1

    extra_score_if_all_my_drones_save = owners_extra_score_with_all_unsaved_creatures[my_owner].total

    if extra_score_if_all_my_drones_save >= my_extra_score_to_win:
        for drone in my_drones.values():
            if len(drone.unsaved_creatures_idt) > 0:
                actions[drone.idt] = Action(target=Point(drone.x, 499),
                                            comment=f"SAVE {drone.extra_score_with_unsaved_creatures:.0f}/{extra_score_if_all_my_drones_save:.0f}/{my_extra_score_to_win:.0f}/{my_total_max_score:.0f}")

    else:
        ordered_my_drones_with_most_extra_score = order_assets(my_drones.values(),
                                                               on_attr='extra_score_with_unsaved_creatures',
                                                               ascending=False)
        for drone in ordered_my_drones_with_most_extra_score:
            drone_extra_score = drone.extra_score_with_unsaved_creatures
            if drone_extra_score >= 20 or drone_extra_score >= my_extra_score_to_win:
                actions[drone.idt] = Action(target=Point(drone.x, 499),
                                            comment=f"SAVE {drone.extra_score_with_unsaved_creatures:.0f}/{extra_score_if_all_my_drones_save:.0f}/{my_extra_score_to_win:.0f}/{my_total_max_score:.0f}")

    return actions


def find_valuable_target(my_drones: Dict[int, MyDrone], creatures: Dict[int, Creature], total_units_count: int,
                         hash_map_norm2=HASH_MAP_NORM2):
    actions = {}

    ordered_creatures_with_most_extra_score = order_assets(creatures.values(), on_attr='my_extra_score',
                                                           ascending=False)
    creatures_with_extra_score = [creature for creature in ordered_creatures_with_most_extra_score if
                                  creature.my_extra_score > 0]
    nb_creatures_with_extra_score = len(creatures_with_extra_score)

    if nb_creatures_with_extra_score == 1:
        drone_target = ordered_creatures_with_most_extra_score[0]
        closest_drone = sorted(my_drones.values(), key=lambda drone: hash_map_norm2[drone_target.next_position - drone.position])[0]
        light = use_light_to_find_a_target(closest_drone, drone_target)
        actions[closest_drone.idt] = Action(target=drone_target.next_position, light=light,
                                            comment=f"FIND {drone_target.log()}")

    elif nb_creatures_with_extra_score > 1:
        creatures_x = [creature.x for creature in creatures_with_extra_score]
        x_min = np.min(creatures_x)
        x_median = np.median(creatures_x)
        x_max = np.max(creatures_x)

        if x_median == x_min or x_median == x_max:
            x_median = (x_max + x_min) / 2

        creatures_with_extra_score_left = [creature for creature in creatures_with_extra_score if
                                           creature.x < x_median]
        creatures_with_extra_score_right = [creature for creature in creatures_with_extra_score if
                                            creature.x > x_median]
        creatures_with_extra_score_median = [creature for creature in creatures_with_extra_score if
                                             creature.x == x_median]

        for creature in creatures_with_extra_score_median:
            nb_creatures_on_the_left = len(creatures_with_extra_score_left)
            nb_creatures_on_the_right = len(creatures_with_extra_score_right)
            if nb_creatures_on_the_left <= nb_creatures_on_the_right:
                creatures_with_extra_score_left.append(creature)
            else:
                creatures_with_extra_score_right.append(creature)

        left_target = creatures_with_extra_score_left[0]
        right_target = creatures_with_extra_score_right[0]

        my_drones_from_left_to_right = order_assets(my_drones.values(), 'x')
        drone_left = my_drones_from_left_to_right[0]
        drone_right = my_drones_from_left_to_right[-1]

        next_left_target = creatures[optimized_next_target(drone=drone_left, drone_target=left_target,
                                                           creatures_connected_to_drone=creatures_with_extra_score_left,
                                                           total_units_count=total_units_count)]

        next_right_target = creatures[optimized_next_target(drone=drone_right, drone_target=right_target,
                                                            creatures_connected_to_drone=creatures_with_extra_score_right,
                                                            total_units_count=total_units_count)]

        optimized_left_target = optimize_path_with_targets(drone=drone_left, first_target=next_left_target,
                                                           final_target=left_target)
        light = use_light_to_find_a_target(drone_left, next_left_target)
        actions[drone_left.idt] = Action(target=optimized_left_target, light=light,
                                         comment=f"FIND {left_target.log()} ({next_left_target.log()})")

        optimized_right_target = optimize_path_with_targets(drone=drone_right, first_target=next_right_target,
                                                            final_target=right_target)
        light = use_light_to_find_a_target(drone_right, next_right_target)
        actions[drone_right.idt] = Action(target=optimized_right_target, light=light,
                                          comment=f"FIND {right_target.log()} ({next_right_target.log()})")

    return actions


def deny_valuable_fish_for_foe(my_drones: Dict[int, MyDrone], creatures: Dict[int, Creature], nb_turns: int,
                               hash_map_norm2=HASH_MAP_NORM2, monster_kind=Kind.MONSTER.value, x_max=X_MAX,
                               x_center=X_MAX/2, limit_distance_from_edge=LIMIT_DISTANCE_FROM_EDGE_TO_DENY,
                               scare_from=SCARE_FROM_DISTANCE, limit_distance_to_deny=LIMIT_DISTANCE_TO_DENY2):
    actions = {}

    fishes_close_to_edge = [creature for creature in creatures.values()
                            if ((nb_turns - creature.last_turn_visible <= 3) if creature.last_turn_visible else False)
                            and (creature.kind != monster_kind) and (creature.foe_extra_score > 0) and
                            (creature.next_x < limit_distance_from_edge or x_max - creature.next_x < limit_distance_from_edge)]

    if len(fishes_close_to_edge) > 0:
        fishes_with_most_extra_for_foe: List[Creature] = order_assets(fishes_close_to_edge, on_attr='foe_extra_score',
                                                                      ascending=False)

        for fish in fishes_with_most_extra_for_foe:
            closest_drone = sorted(my_drones.values(), key=lambda drone: hash_map_norm2[fish.next_position - drone.position])[0]
            if hash_map_norm2[fish.next_position - closest_drone.position] < limit_distance_to_deny:
                edge_direction = 1 if fish.next_x > x_center else -1
                if not actions.get(closest_drone.idt):
                    target = fish.next_position - edge_direction * Vector(scare_from, 0)
                    actions[closest_drone.idt] = Action(target=target, comment=f"DENY {fish.log()}")

    return actions


def just_do_something(my_drones: Dict[int, MyDrone], creatures: Dict[int, Creature], x_center=X_MAX/2,
                      scare_from=SCARE_FROM_DISTANCE):
    actions = {}

    nb_find_actions = 0
    for drone_idt, drone in my_drones.items():
        if drone.extra_score_with_unsaved_creatures > 0:
            actions[drone.idt] = Action(target=Point(drone.x, 499),
                                        comment=f"SAVE {drone.extra_score_with_unsaved_creatures:.0f}")
        else:
            drone_target = order_assets(creatures.values(), on_attr='foe_extra_score', ascending=False)[
                nb_find_actions]
            nb_find_actions += 1
            edge_direction = 1 if drone_target.next_x > x_center else -1
            target = drone_target.next_position - edge_direction * Vector(scare_from, 0)
            actions[drone_idt] = Action(target=target, light=True, comment=f"DENY {drone_target.log()}")

    return actions


def avoid_monsters(drone: MyDrone, aimed_action: Action, default_action: Action, hash_map_norm2=HASH_MAP_NORM2,
                   rotate_matrix=ROTATE_2D_MATRIX, theta_increment=math.pi / 16, drone_max_speed=DRONE_MAX_SPEED):
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
        speeds_to_try = [speed_wanted, (drone_max_speed / speed_wanted.norm) * speed_wanted, (1/2) * speed_wanted]
        for speed in speeds_to_try:
            thetas = [theta for theta in np.arange(theta_increment, math.pi + theta_increment, theta_increment)]
            for theta in thetas:
                next_positions_to_try = [drone.position + round(rotate_matrix.rotate_vector(speed, theta)),
                                         drone.position + round(rotate_matrix.rotate_vector(speed, -theta))]

                next_positions_to_try = sorted(next_positions_to_try, key=lambda p: hash_map_norm2[target_position - p])

                for next_position in next_positions_to_try:
                    if is_next_position_safe(drone, next_position):
                        safe_action.target = next_position
                        return safe_action

    return default_action


def order_assets(assets: List[Union[Asset, Creature, Drone, MyDrone]], on_attr: str, ascending: bool = True) -> List[Union[Asset, Creature, Drone, MyDrone]]:
    return sorted(assets, key=lambda asset: getattr(asset, on_attr), reverse=not ascending)
