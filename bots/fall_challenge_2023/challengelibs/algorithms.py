from typing import List, Dict

import numpy as np

from botlibs.trigonometry import Vector, Point
from bots.fall_challenge_2023.challengelibs.act import Action
from bots.fall_challenge_2023.challengelibs.asset import Drone, Creature, MyDrone, Asset
from bots.fall_challenge_2023.singletons import HASH_MAP_NORMS, AUGMENTED_LIGHT_RADIUS, FLEE_RADIUS_FROM_MONSTERS, \
    SAFE_RADIUS_FROM_MONSTERS, MAP_CENTER, DRONE_MAX_SPEED, MY_OWNER, FOE_OWNER


def use_light_to_find_a_target(drone: Drone, target: Creature, hash_map_norms=HASH_MAP_NORMS,
                               augmented_light_radius=AUGMENTED_LIGHT_RADIUS):
    battery = drone.battery
    if battery >= 10 and drone.y > 4000:
        return True
    if drone.battery >= 5:
        distance_to_target = hash_map_norms[target.position - drone.position]
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


def flee_from_monsters(my_drones: Dict[int, MyDrone], monsters: List[Creature], nb_turns: int,
                       hash_map_norms=HASH_MAP_NORMS, flee_radius_from_monsters=FLEE_RADIUS_FROM_MONSTERS,
                       safe_radius_from_monsters=SAFE_RADIUS_FROM_MONSTERS, map_center=MAP_CENTER,
                       drone_speed=DRONE_MAX_SPEED):

    actions = {}

    for my_drone in my_drones.values():
        my_drone.has_to_flee_from = []
        for monster in monsters:
            if monster.last_turn_visible:
                if nb_turns - monster.last_turn_visible <= 3:
                    if hash_map_norms[monster.position - my_drone.position] <= flee_radius_from_monsters:
                        my_drone.has_to_flee_from.append(monster)

    for drone_idt, drone in my_drones.items():
        drone_has_to_flee_from = drone.has_to_flee_from
        if len(drone_has_to_flee_from) == 1:
            monster = drone_has_to_flee_from[0]
            vector_to_creature = monster.position - drone.position
            distance_to_creature = hash_map_norms[vector_to_creature]

            if distance_to_creature > safe_radius_from_monsters:
                v = (1 / distance_to_creature ** (1 / 2)) * vector_to_creature
                flee_vectors = [Vector(v.y, -v.x), Vector(-v.y, v.x)]
                flee_vector = flee_vectors[0]
                vector_to_center = map_center - drone.position
                cos_with_center = flee_vector.dot(vector_to_center)
                if flee_vectors[1].dot(vector_to_center) > cos_with_center:
                    flee_vector = flee_vectors[1]
                actions[drone_idt] = Action(
                    target=drone.position + (drone_speed ** (1 / 2)) * flee_vector,
                    comment=f"FLEE FROM {monster.log()}")
            else:
                flee_vector = -1 * vector_to_creature
                actions[drone_idt] = Action(target=drone.position + (
                        (drone_speed ** (1 / 2)) / (distance_to_creature ** (1 / 2))) * flee_vector,
                                                      comment=f"FLEE FROM {monster.log()}")
        elif len(drone_has_to_flee_from) > 1:
            flee_vector = Vector(0, 0)
            comment = ""
            for monster in drone_has_to_flee_from:
                flee_vector += drone.position - monster.position
                comment = f"{comment} {monster.log()}"
            actions[drone_idt] = Action(
                target=drone.position + ((drone_speed ** (1 / 2)) / flee_vector.norm) * flee_vector,
                comment=f"FLEE FROM{comment}")

    return actions


def order_assets(assets: List[Asset], on_attr: str, ascending: bool = True):
    return sorted(assets, key=lambda asset: getattr(asset, on_attr), reverse=not ascending)
