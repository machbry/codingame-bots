import sys
from typing import List, Union

import numpy as np

from botlibs.trigonometry import Point, Vector
from bots.fall_challenge_2023.challengelibs.act import Action, order_assets
from bots.fall_challenge_2023.challengelibs.game_assets import AssetType, GameAssets
from bots.fall_challenge_2023.challengelibs.score import evaluate_extra_score_for_owner_creature, update_trophies
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER, OWNERS, HASH_MAP_NORMS, CORNERS, \
    CREATURE_HABITATS_PER_KIND, DRONE_SPEED, SAFE_RADIUS_FROM_MONSTERS, MAP_CENTER, \
    FLEE_RADIUS_FROM_MONSTERS, MAX_SPEED_PER_KIND, Color, Kind

GAME_ASSETS = GameAssets()


class GameLoop:
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.game_assets = GAME_ASSETS
        self.hash_map_norms = HASH_MAP_NORMS

        self.my_drones_idt_play_order = []

        self.monsters = []

        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]
            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind
            creature.habitat = CREATURE_HABITATS_PER_KIND[kind]

            if creature.kind == -1:
                self.monsters.append(creature)

            for owner in OWNERS:
                scans = self.game_assets.new_asset(asset_type=AssetType.SCANS, idt=owner)
                scans.owner = owner
                scans.saved_creatures = np.zeros(shape=(len(Color), len(Kind) - 1))

        for color in Color:
            self.game_assets.new_asset(asset_type=AssetType.COLORSTROPHY, idt=color.value)

        for kind in Kind:
            if kind != Kind.MONSTER.value:
                self.game_assets.new_asset(asset_type=AssetType.KINDSTROPHY, idt=kind.value)

        if GameLoop.LOG:
            print(self.init_inputs, file=sys.stderr, flush=True)

    def get_init_input(self):
        result = input()
        self.init_inputs.append(result)
        return result

    def get_turn_input(self):
        result = input()
        self.turns_inputs.append(result)
        return result

    def update_saved_scan(self, owner: int, creature_idt: int):
        scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=owner)
        creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)

        saved_creatures = scans.saved_creatures
        creature_saved = saved_creatures[creature.color, creature.kind]

        if creature_saved == 1:
            return

        creature.saved_by_owners.append(owner)

        creature_color, creature_kind = creature.color, creature.kind
        saved_creatures[creature_color, creature_kind] = 1

    def update_drone(self, drone_idt, drone_x, drone_y, emergency, battery,
                     asset_type: Union[AssetType.MYDRONE, AssetType.FOEDRONE]):
        drone = self.game_assets.get(asset_type=asset_type, idt=drone_idt)
        if drone is None:
            drone = self.game_assets.new_asset(asset_type=asset_type, idt=drone_idt)
        drone.x = drone_x
        drone.y = drone_y
        drone.emergency = emergency
        drone.battery = battery

        if drone.emergency == 1:
            drone.unsaved_creatures_idt = set()

    def update(self):
        self.nb_turns += 1

        my_score = int(self.get_turn_input())
        foe_score = int(self.get_turn_input())

        my_scan_count = int(self.get_turn_input())
        for i in range(my_scan_count):
            creature_idt = int(self.get_turn_input())
            self.update_saved_scan(owner=MY_OWNER, creature_idt=creature_idt)

        foe_scan_count = int(self.get_turn_input())
        for i in range(foe_scan_count):
            creature_idt = int(self.get_turn_input())
            self.update_saved_scan(owner=FOE_OWNER, creature_idt=creature_idt)

        colors_trophies = self.game_assets.get_all(AssetType.COLORSTROPHY)
        kinds_trophies = self.game_assets.get_all(AssetType.KINDSTROPHY)
        for owner in OWNERS:
            saved_creatures = self.game_assets.get(AssetType.SCANS, owner).saved_creatures
            update_trophies(owner, saved_creatures, colors_trophies, kinds_trophies)

        my_drone_count = int(self.get_turn_input())
        self.my_drones_idt_play_order = []
        for i in range(my_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            self.update_drone(drone_idt, drone_x, drone_y, emergency, battery, AssetType.MYDRONE)
            self.my_drones_idt_play_order.append(drone_idt)

        foe_drone_count = int(self.get_turn_input())
        for i in range(foe_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            self.update_drone(drone_idt, drone_x, drone_y, emergency, battery, AssetType.FOEDRONE)

        drone_scan_count = int(self.get_turn_input())
        for i in range(drone_scan_count):
            drone_idt, creature_idt = [int(j) for j in self.get_turn_input().split()]

            drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_idt)

            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)

            drone.unsaved_creatures_idt.add(creature_idt)
            creature.scanned_by_drones.add(drone_idt)

        visible_creature_count = int(self.get_turn_input())
        for i in range(visible_creature_count):
            creature_idt, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in
                                                                              self.get_turn_input().split()]
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.x = creature_x
            creature.y = creature_y
            creature.vx = creature_vx
            creature.vy = creature_vy
            creature.visible = True
            creature.last_turn_visible = self.nb_turns

        radar_blip_count = int(self.get_turn_input())
        for i in range(radar_blip_count):
            inputs = self.get_turn_input().split()
            drone_idt = int(inputs[0])
            creature_idt = int(inputs[1])
            radar = inputs[2]

            radar_idt = hash((drone_idt, creature_idt))
            radar_blip = self.game_assets.get(asset_type=AssetType.RADARBLIP, idt=radar_idt)
            if radar_blip is None:
                radar_blip = self.game_assets.new_asset(asset_type=AssetType.RADARBLIP, idt=radar_idt)
                radar_blip.drone_idt = drone_idt
                radar_blip.creature_idt = creature_idt

            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.escaped = False

            if len(radar_blip.zones) > 0:
                previous_zone = radar_blip.zones[-1]
                creature_max_speed = MAX_SPEED_PER_KIND[creature.kind]
                radar_blip.zones[-1] = [previous_zone[0] - creature_max_speed,
                                        previous_zone[1] - creature_max_speed,
                                        previous_zone[2] + creature_max_speed,
                                        previous_zone[3] + creature_max_speed]

            drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_idt)

            zone_corner = CORNERS[radar]
            drone_x, drone_y = drone.x, drone.y
            zone_corner_x, zone_corner_y = zone_corner.x, zone_corner.y
            zone_x_min = min(drone_x, zone_corner_x)
            zone_y_min = min(drone_y, zone_corner_y)
            zone_x_max = max(drone_x, zone_corner_x)
            zone_y_max = max(drone_y, zone_corner_y)
            radar_blip.zones.append([zone_x_min, zone_y_min, zone_x_max, zone_y_max])

        if GameLoop.LOG:
            self.print_turn_logs()

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def start(self):
        while GameLoop.RUNNING:
            # RESET ASSETS - BEGIN

            for creature in self.game_assets.get_all(asset_type=AssetType.CREATURE).values():
                creature.scanned_by_drones = set()
                creature.visible = False
                creature.escaped = True

            # RESET ASSETS - END

            self.update()

            # COMPUTE EXTRA METRICS FOR ASSETS - BEGIN

            creatures = self.game_assets.get_all(AssetType.CREATURE)
            my_drones = self.game_assets.get_all(AssetType.MYDRONE)
            foe_drones = self.game_assets.get_all(AssetType.FOEDRONE)
            all_drones = [*my_drones.values(), *foe_drones.values()]

            # EVALUATE EXTRA SCORES - BEGIN
            # TODO : matrix representations & calculus for scores, combinaisons for colors & kinds
            # TODO : can be done later
            ordered_drones_from_top_to_bottom = order_assets(all_drones, 'y')

            # INIT
            for creature in creatures.values():
                creature.eval_saved_by_owners = creature.saved_by_owners.copy()
                creature.extra_scores = {owner: 0 for owner in OWNERS}

            # EVALUATE EXTRA SCORE FOR UNSAVED CREATURES FOR EACH DRONE
            # SIMULATE THAT EACH DRONE SAVES ITS SCANS (FROM TOP TO BOTTOM)
            for drone in ordered_drones_from_top_to_bottom:
                drone.extra_score_with_unsaved_creatures = 0
                owner = drone.owner
                for creature_idt in drone.unsaved_creatures_idt:
                    creature = self.game_assets.get(AssetType.CREATURE, creature_idt)
                    extra_score = evaluate_extra_score_for_owner_creature(creature_kind=creature.kind,
                                                                          creature_escaped=creature.escaped,
                                                                          creature_saved_by_owners=creature.saved_by_owners,
                                                                          owner=owner)
                    drone.extra_score_with_unsaved_creatures += extra_score
                    creature.eval_saved_by_owners.append(owner)

            # EVALUATE EXTRA SCORE IF CREATURE SAVED BY AN OWNER
            for creature in creatures.values():
                for owner in OWNERS:
                    extra_score = evaluate_extra_score_for_owner_creature(creature_kind=creature.kind,
                                                                          creature_escaped=creature.escaped,
                                                                          creature_saved_by_owners=creature.eval_saved_by_owners,
                                                                          owner=owner)
                    creature.extra_scores[owner] += extra_score

            # EVALUATE EXTRA SCORES - END

            # EVALUATE POSITIONS OF UNVISIBLE CREATURES - BEGIN
            # TODO : use zones lightened by drones to eliminates possible zones

            for creature_idt, creature in creatures.items():
                if not creature.visible:
                    possible_zones = [creature.habitat]
                    for drone_idt, drone in my_drones.items():
                        radar_idt = hash((drone_idt, creature_idt))
                        radar_blip = self.game_assets.get(asset_type=AssetType.RADARBLIP, idt=radar_idt)
                        if radar_blip is not None:
                            radar_blip_zones = radar_blip.zones
                            n = min(len(radar_blip_zones), 2)  # TODO : create constant for max number of zones
                            for i in range(0, n):
                                possible_zones.append(radar_blip_zones[-i-1])

                    intersection = np.array(possible_zones)
                    x_min = np.max(intersection[:, 0])
                    y_min = np.max(intersection[:, 1])
                    x_max = np.min(intersection[:, 2])
                    y_max = np.min(intersection[:, 3])

                    if creature.last_turn_visible:
                        last_seen_turns = self.nb_turns - creature.last_turn_visible
                        current_x_projection = creature.x + last_seen_turns * creature.vx
                        current_y_projection = creature.y + last_seen_turns * creature.vy
                        if (x_min <= current_x_projection <= x_max) and (y_min <= current_y_projection <= y_max):
                            creature.x = current_x_projection
                            creature.y = current_y_projection
                    else:
                        creature.x = (x_min + x_max) / 2
                        creature.y = (y_min + y_max) / 2

            # EVALUATE POSITIONS OF UNVISIBLE CREATURES - END

            # CHECK IF MONSTERS ARE TOO CLOSE TO MY_DRONES - BEGIN

            for my_drone in my_drones.values():
                my_drone.has_to_flee_from = []
                for monster in self.monsters:
                    if HASH_MAP_NORMS[monster.position - my_drone.position] <= FLEE_RADIUS_FROM_MONSTERS:
                        my_drone.has_to_flee_from.append(monster)

            # CHECK IF MONSTERS ARE TOO CLOSE TO MY_DRONES - END

            # COMPUTE EXTRA METRICS FOR ASSETS - END

            # COMPUTE ALGORITHMS FOR DRONE TO ACT - BEGIN
            my_drones_action = {}
            unassigned_drones = my_drones.copy()

            # FLEE FROM MONSTERS - TODO : use trigo to solve this & take into account previous target
            for drone_idt, drone in my_drones.items():
                drone_has_to_flee_from = drone.has_to_flee_from
                if len(drone_has_to_flee_from) == 1:
                    del unassigned_drones[drone_idt]
                    vector_to_creature = drone_has_to_flee_from[0].position - drone.position
                    distance_to_creature = HASH_MAP_NORMS[vector_to_creature]
                    if distance_to_creature > SAFE_RADIUS_FROM_MONSTERS:
                        v = (1 / distance_to_creature ** (1 / 2)) * vector_to_creature
                        flee_vectors = [Vector(v.y, -v.x), Vector(-v.y, v.x)]
                        flee_vector = flee_vectors[0]
                        vector_to_center = MAP_CENTER - drone.position
                        cos_with_center = flee_vector.dot(vector_to_center)
                        if flee_vectors[1].dot(vector_to_center) > cos_with_center:
                            flee_vector = flee_vectors[1]
                        my_drones_action[drone_idt] = Action(
                            target=drone.position + (DRONE_SPEED ** (1 / 2)) * flee_vector, comment="FLEE")
                    else:
                        flee_vector = -1 * vector_to_creature
                        my_drones_action[drone_idt] = Action(target=drone.position + (
                                    (DRONE_SPEED ** (1 / 2)) / (distance_to_creature ** (1 / 2))) * flee_vector,
                                                             comment="FLEE")
                elif len(drone_has_to_flee_from) > 1:
                    del unassigned_drones[drone_idt]
                    flee_vector = Vector(0, 0)
                    for creature in drone_has_to_flee_from:
                        flee_vector += drone.position - creature.position
                    my_drones_action[drone_idt] = Action(
                        target=drone.position + ((DRONE_SPEED ** (1 / 2)) / flee_vector.norm) * flee_vector,
                        comment="FLEE")

            if len(unassigned_drones) > 0:
                ordered_my_drones_with_most_extra_score = order_assets(unassigned_drones.values(), on_attr='extra_score_with_unsaved_creatures', ascending=False)
                for drone in ordered_my_drones_with_most_extra_score:
                    if drone.extra_score_with_unsaved_creatures >= 15:  # TODO : enhance algo to decide saving
                        my_drones_action[drone.idt] = Action(target=Point(drone.x, 499), comment=f"SAVE {drone.extra_score_with_unsaved_creatures}")
                        del unassigned_drones[drone.idt]

            if len(unassigned_drones) > 0:
                nb_find_actions = 0

                ordered_creatures_with_most_extra_score = order_assets(creatures.values(), on_attr='my_extra_score', ascending=False)
                creatures_with_extra_score = [creature for creature in ordered_creatures_with_most_extra_score if creature.my_extra_score > 0]
                nb_creatures_with_extra_score = len(creatures_with_extra_score)

                if nb_creatures_with_extra_score == 1:
                    drone_target = ordered_creatures_with_most_extra_score[0]
                    for drone_idt, drone in unassigned_drones.items():
                        my_drones_action[drone_idt] = Action(target=drone_target, light=True, comment=f"FIND {drone_target.idt}")
                elif nb_creatures_with_extra_score > 1:
                    unassigned_drones_idt = list(unassigned_drones.keys())

                    x_median = np.median([creature.x for creature in creatures_with_extra_score])

                    creatures_with_extra_score_left = [creature for creature in creatures_with_extra_score if creature.x <= x_median]
                    creatures_with_extra_score_right = [creature for creature in creatures_with_extra_score if creature.x > x_median]

                    left_target = creatures_with_extra_score_left[0]
                    if len(creatures_with_extra_score_right) == 0:
                        right_target = creatures_with_extra_score_left[1]
                    else:
                        right_target = creatures_with_extra_score_right[0]

                    my_drones_from_left_to_right = order_assets(my_drones.values(), 'x')
                    drone_left_idt = my_drones_from_left_to_right[0].idt
                    drone_right_idt = my_drones_from_left_to_right[-1].idt

                    if drone_left_idt in unassigned_drones_idt:
                        my_drones_action[drone_left_idt] = Action(target=left_target, light=True, comment=f"FIND {left_target.idt}")

                    if drone_right_idt in unassigned_drones_idt:
                        my_drones_action[drone_right_idt] = Action(target=right_target, light=True, comment=f"FIND {right_target.idt}")

                else:
                    for drone_idt, drone in unassigned_drones.items():
                        if drone.extra_score_with_unsaved_creatures > 0:
                            my_drones_action[drone.idt] = Action(target=Point(drone.x, 499), comment=f"SAVE {drone.extra_score_with_unsaved_creatures}")
                        else:
                            drone_target = order_assets(creatures.values(), on_attr='foe_extra_score', ascending=False)[nb_find_actions]
                            nb_find_actions += 1
                            my_drones_action[drone.idt] = Action(target=drone_target, light=True, comment=f"FIND {drone_target.idt}")

            # COMPUTE ALGORITHMS FOR DRONE TO ACT - END

            for drone_idt in self.my_drones_idt_play_order:
                print(my_drones_action[drone_idt])
