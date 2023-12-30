import sys
from typing import List, Union, Dict

import numpy as np

from botlibs.trigonometry import Point, Vector
from bots.fall_challenge_2023.challengelibs.act import Action, order_assets
from bots.fall_challenge_2023.challengelibs.asset import Creature
from bots.fall_challenge_2023.challengelibs.algorithms import use_light_to_find_a_target
from bots.fall_challenge_2023.challengelibs.game_assets import AssetType, GameAssets
from bots.fall_challenge_2023.challengelibs.map import evaluate_positions_of_creatures
from bots.fall_challenge_2023.challengelibs.score import update_trophies, update_saved_scans, ScoreSimulation, \
    evaluate_extra_scores_for_multiple_scenarios
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER, OWNERS, HASH_MAP_NORMS, CORNERS, \
    CREATURE_HABITATS_PER_KIND, DRONE_SPEED, SAFE_RADIUS_FROM_MONSTERS, MAP_CENTER, \
    FLEE_RADIUS_FROM_MONSTERS, MAX_SPEED_PER_KIND, MAX_NUMBER_OF_RADAR_BLIPS_USED, COLORS, KINDS, \
    EMPTY_ARRAY_CREATURES, Kind

GAME_ASSETS = GameAssets()


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "game_assets", "hash_map_norms", "empty_array_saved_creatures",
                 "max_number_of_radar_blips_used", "max_speed_per_kind", "corners", "my_owner", "foe_owner", "owners",
                 "flee_radius_from_monsters", "safe_radius_from_monsters", "map_center", "drone_speed", "owners_scores",
                 "owners_extra_score_with_all_unsaved_creatures", "owners_max_possible_score", "my_drones_idt_play_order",
                 "newly_saved_creatures", "monsters")
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.game_assets = GAME_ASSETS
        self.hash_map_norms = HASH_MAP_NORMS
        self.empty_array_saved_creatures = EMPTY_ARRAY_CREATURES
        self.max_number_of_radar_blips_used = MAX_NUMBER_OF_RADAR_BLIPS_USED
        self.max_speed_per_kind = MAX_SPEED_PER_KIND
        self.corners = CORNERS
        self.my_owner = MY_OWNER
        self.foe_owner = FOE_OWNER
        self.owners = OWNERS
        self.flee_radius_from_monsters = FLEE_RADIUS_FROM_MONSTERS
        self.safe_radius_from_monsters = SAFE_RADIUS_FROM_MONSTERS
        self.map_center = MAP_CENTER
        self.drone_speed = DRONE_SPEED

        self.owners_scores: Dict[int, int] = {}
        self.owners_extra_score_with_all_unsaved_creatures: Dict[int, int] = {}
        self.owners_max_possible_score: Dict[int, int] = {}
        self.my_drones_idt_play_order: List[int] = []
        self.newly_saved_creatures: np.ndarray = np.zeros_like(self.empty_array_saved_creatures)
        self.monsters: List[Creature] = []

        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]
            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind
            creature.habitat = CREATURE_HABITATS_PER_KIND[kind]

            if creature.kind == Kind.MONSTER.value:
                self.monsters.append(creature)

            for owner in self.owners:
                scans = self.game_assets.new_asset(asset_type=AssetType.SCANS, idt=owner)
                scans.owner = owner
                scans.saved_creatures = np.zeros_like(self.empty_array_saved_creatures)

        trophies = self.game_assets.new_asset(asset_type=AssetType.TROPHIES, idt=42)
        trophies.creatures_win_by = np.zeros_like(self.empty_array_saved_creatures)
        trophies.colors_win_by = np.zeros_like(COLORS)
        trophies.kinds_win_by = np.zeros_like(KINDS)

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

    def update_drone(self, drone_idt, drone_x, drone_y, emergency, battery,
                     asset_type: Union[AssetType.MY_DRONE, AssetType.FOE_DRONE]):
        drone = self.game_assets.get(asset_type=asset_type, idt=drone_idt)
        if drone is None:
            drone = self.game_assets.new_asset(asset_type=asset_type, idt=drone_idt)
        drone.x = drone_x
        drone.y = drone_y
        drone.emergency = emergency
        drone.battery = battery
        drone.unsaved_creatures_idt = set()

    def update_visible_creature(self, creature_idt, creature_x, creature_y, creature_vx, creature_vy):
        creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
        creature.x = creature_x
        creature.y = creature_y
        creature.vx = creature_vx
        creature.vy = creature_vy
        creature.visible = True
        creature.last_turn_visible = self.nb_turns

    def update_radar_blip(self, drone_idt, creature_idt, radar):
        radar_idt = hash((drone_idt, creature_idt))
        radar_blip = self.game_assets.get(asset_type=AssetType.RADAR_BLIP, idt=radar_idt)
        if radar_blip is None:
            radar_blip = self.game_assets.new_asset(asset_type=AssetType.RADAR_BLIP, idt=radar_idt)
            radar_blip.drone_idt = drone_idt
            radar_blip.creature_idt = creature_idt

        creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
        creature.escaped = False

        radar_blip_zones = radar_blip.zones
        n = min(len(radar_blip_zones), self.max_number_of_radar_blips_used - 1)
        for i in range(0, n):
            zone = radar_blip.zones[-i-1]
            creature_max_speed = self.max_speed_per_kind[creature.kind]
            radar_blip.zones[-i-1] = [zone[0] - creature_max_speed,
                                      zone[1] - creature_max_speed,
                                      zone[2] + creature_max_speed,
                                      zone[3] + creature_max_speed]

        drone = self.game_assets.get(asset_type=AssetType.MY_DRONE, idt=drone_idt)
        if drone is None:
            drone = self.game_assets.get(asset_type=AssetType.FOE_DRONE, idt=drone_idt)

        zone_corner = self.corners[radar]
        drone_x, drone_y = drone.x, drone.y
        zone_corner_x, zone_corner_y = zone_corner.x, zone_corner.y
        zone_x_min = min(drone_x, zone_corner_x)
        zone_y_min = min(drone_y, zone_corner_y)
        zone_x_max = max(drone_x, zone_corner_x)
        zone_y_max = max(drone_y, zone_corner_y)
        radar_blip.zones.append([zone_x_min, zone_y_min, zone_x_max, zone_y_max])

    def update_assets(self):
        self.newly_saved_creatures = np.zeros_like(self.empty_array_saved_creatures)

        for creature in self.game_assets.get_all(asset_type=AssetType.CREATURE).values():
            creature.visible = False
            creature.escaped = True

        self.nb_turns += 1

        self.owners_scores[self.my_owner] = int(self.get_turn_input())
        self.owners_scores[self.foe_owner] = int(self.get_turn_input())

        trophies = self.game_assets.get(AssetType.TROPHIES, 42)
        creatures_win_by = trophies.creatures_win_by
        colors_win_by = trophies.colors_win_by
        kinds_win_by = trophies.kinds_win_by

        my_scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=self.my_owner)
        my_saved_creatures = my_scans.saved_creatures

        foe_scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=self.foe_owner)
        foe_saved_creatures = foe_scans.saved_creatures

        my_scan_count = int(self.get_turn_input())
        for i in range(my_scan_count):
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=int(self.get_turn_input()))
            creature_color, creature_kind = creature.color, creature.kind
            if update_saved_scans(my_saved_creatures, creature_color, creature_kind):
                self.newly_saved_creatures[creature_color, creature_kind] = self.my_owner

        update_trophies(owner=self.my_owner, saved_creatures=my_saved_creatures,
                        newly_saved_creatures=self.newly_saved_creatures,
                        creatures_win_by=creatures_win_by, colors_win_by=colors_win_by, kinds_win_by=kinds_win_by)

        foe_scan_count = int(self.get_turn_input())
        for i in range(foe_scan_count):
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=int(self.get_turn_input()))
            creature_color, creature_kind = creature.color, creature.kind
            if update_saved_scans(foe_saved_creatures, creature_color, creature_kind):
                self.newly_saved_creatures[creature_color, creature_kind] = self.foe_owner

        update_trophies(owner=self.foe_owner, saved_creatures=foe_saved_creatures,
                        newly_saved_creatures=self.newly_saved_creatures,
                        creatures_win_by=creatures_win_by, colors_win_by=colors_win_by, kinds_win_by=kinds_win_by)

        my_drone_count = int(self.get_turn_input())
        self.my_drones_idt_play_order = []
        for i in range(my_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            self.update_drone(drone_idt, drone_x, drone_y, emergency, battery, AssetType.MY_DRONE)
            self.my_drones_idt_play_order.append(drone_idt)

        foe_drone_count = int(self.get_turn_input())
        for i in range(foe_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            self.update_drone(drone_idt, drone_x, drone_y, emergency, battery, AssetType.FOE_DRONE)

        drone_scan_count = int(self.get_turn_input())
        for i in range(drone_scan_count):
            drone_idt, creature_idt = [int(j) for j in self.get_turn_input().split()]
            drone = self.game_assets.get(asset_type=AssetType.MY_DRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.get(asset_type=AssetType.FOE_DRONE, idt=drone_idt)
            drone.unsaved_creatures_idt.add(creature_idt)

        visible_creature_count = int(self.get_turn_input())
        for i in range(visible_creature_count):
            creature_idt, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in
                                                                              self.get_turn_input().split()]
            self.update_visible_creature(creature_idt, creature_x, creature_y, creature_vx, creature_vy)

        radar_blip_count = int(self.get_turn_input())
        for i in range(radar_blip_count):
            inputs = self.get_turn_input().split()
            drone_idt, creature_idt, radar = int(inputs[0]), int(inputs[1]), inputs[2]
            self.update_radar_blip(drone_idt, creature_idt, radar)

        if GameLoop.LOG:
            self.print_turn_logs()

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def start(self):
        while GameLoop.RUNNING:

            self.update_assets()

            creatures = self.game_assets.get_all(AssetType.CREATURE)
            my_drones = self.game_assets.get_all(AssetType.MY_DRONE)
            foe_drones = self.game_assets.get_all(AssetType.FOE_DRONE)
            radar_blips = self.game_assets.get_all(AssetType.RADAR_BLIP)
            scans = self.game_assets.get_all(AssetType.SCANS)
            trophies = self.game_assets.get(AssetType.TROPHIES, 42)

            # note : extra scores for creatures or drones are directly stored in these assets
            self.owners_extra_score_with_all_unsaved_creatures, self.owners_max_possible_score = (
                evaluate_extra_scores_for_multiple_scenarios(creatures=creatures, my_drones=my_drones,
                                                             foe_drones=foe_drones, scans=scans,
                                                             trophies=trophies, current_owners_scores=self.owners_scores))

            evaluate_positions_of_creatures(creatures=creatures, radar_blips=radar_blips,
                                            my_drones=my_drones, nb_turns=self.nb_turns)

            # CHECK IF MONSTERS ARE TOO CLOSE TO MY_DRONES - BEGIN

            for my_drone in my_drones.values():
                my_drone.has_to_flee_from = []
                for monster in self.monsters:
                    if monster.last_turn_visible:
                        if self.nb_turns - monster.last_turn_visible <= 3:
                            if self.hash_map_norms[monster.position - my_drone.position] <= self.flee_radius_from_monsters:
                                my_drone.has_to_flee_from.append(monster)

            # CHECK IF MONSTERS ARE TOO CLOSE TO MY_DRONES - END

            # COMPUTE EXTRA METRICS FOR ASSETS - END

            # COMPUTE ALGORITHMS FOR DRONE TO ACT - BEGIN
            default_action = Action(move=False, light=False)
            my_drones_action = {drone_idt: default_action for drone_idt in self.my_drones_idt_play_order}
            unassigned_drones = {drone_idt: drone for drone_idt, drone in my_drones.items() if drone.emergency == 0}

            # FLEE FROM MONSTERS
            for drone_idt, drone in unassigned_drones.copy().items():
                drone_has_to_flee_from = drone.has_to_flee_from
                if len(drone_has_to_flee_from) == 1:
                    del unassigned_drones[drone_idt]
                    monster = drone_has_to_flee_from[0]
                    vector_to_creature = monster.position - drone.position
                    distance_to_creature = self.hash_map_norms[vector_to_creature]

                    if distance_to_creature > self.safe_radius_from_monsters:
                        v = (1 / distance_to_creature ** (1 / 2)) * vector_to_creature
                        flee_vectors = [Vector(v.y, -v.x), Vector(-v.y, v.x)]
                        flee_vector = flee_vectors[0]
                        vector_to_center = self.map_center - drone.position
                        cos_with_center = flee_vector.dot(vector_to_center)
                        if flee_vectors[1].dot(vector_to_center) > cos_with_center:
                            flee_vector = flee_vectors[1]
                        my_drones_action[drone_idt] = Action(target=drone.position + (self.drone_speed ** (1 / 2)) * flee_vector,
                                                             comment=f"FLEE FROM {monster.log()}")
                    else:
                        flee_vector = -1 * vector_to_creature
                        my_drones_action[drone_idt] = Action(target=drone.position + ((self.drone_speed ** (1 / 2)) / (distance_to_creature ** (1 / 2))) * flee_vector,
                                                             comment=f"FLEE FROM {monster.log()}")
                elif len(drone_has_to_flee_from) > 1:
                    del unassigned_drones[drone_idt]
                    flee_vector = Vector(0, 0)
                    comment = ""
                    for monster in drone_has_to_flee_from:
                        flee_vector += drone.position - monster.position
                        comment = f"{comment} {monster.log()}"
                    my_drones_action[drone_idt] = Action(target=drone.position + ((self.drone_speed ** (1 / 2)) / flee_vector.norm) * flee_vector,
                                                         comment=f"FLEE FROM{comment}")

            # GO SAVING ?
            if len(unassigned_drones) > 0:
                extra_score_to_win = self.owners_max_possible_score[self.foe_owner] - self.owners_scores[self.my_owner] + 1

                extra_score_if_all_my_drones_save = self.owners_extra_score_with_all_unsaved_creatures[self.my_owner]
                if len(unassigned_drones) == len(my_drones) and extra_score_if_all_my_drones_save >= extra_score_to_win:
                    for drone in my_drones.values():
                        if len(drone.unsaved_creatures_idt) > 0:
                            my_drones_action[drone.idt] = Action(target=Point(drone.x, 499),
                                                                 comment=f"SAVE {extra_score_if_all_my_drones_save} ({extra_score_to_win})")
                            del unassigned_drones[drone.idt]

                else:
                    ordered_my_drones_with_most_extra_score = order_assets(unassigned_drones.values(), on_attr='extra_score_with_unsaved_creatures', ascending=False)
                    for drone in ordered_my_drones_with_most_extra_score:
                        drone_extra_score = drone.extra_score_with_unsaved_creatures
                        if drone_extra_score >= 20 or drone_extra_score >= extra_score_to_win:
                            my_drones_action[drone.idt] = Action(target=Point(drone.x, 499), comment=f"SAVE {drone.extra_score_with_unsaved_creatures} ({extra_score_to_win})")
                            del unassigned_drones[drone.idt]

            # EXPLORE TOWARDS ?
            if len(unassigned_drones) > 0:
                nb_find_actions = 0

                ordered_creatures_with_most_extra_score = order_assets(creatures.values(), on_attr='my_extra_score', ascending=False)
                creatures_with_extra_score = [creature for creature in ordered_creatures_with_most_extra_score if creature.my_extra_score > 0]
                nb_creatures_with_extra_score = len(creatures_with_extra_score)

                if nb_creatures_with_extra_score == 1:
                    drone_target = ordered_creatures_with_most_extra_score[0]
                    for drone_idt, drone in unassigned_drones.items():
                        light = use_light_to_find_a_target(drone, drone_target)
                        my_drones_action[drone_idt] = Action(target=drone_target, light=light, comment=f"FIND {drone_target.log()}")

                elif nb_creatures_with_extra_score > 1:
                    x_median = np.median([creature.x for creature in creatures_with_extra_score])

                    creatures_with_extra_score_left = [creature for creature in creatures_with_extra_score if creature.x <= x_median]
                    creatures_with_extra_score_right = [creature for creature in creatures_with_extra_score if creature.x > x_median]

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

                    drone_left = unassigned_drones.get(drone_left_idt)
                    if drone_left is not None:
                        light = use_light_to_find_a_target(drone_left, left_target)
                        my_drones_action[drone_left_idt] = Action(target=left_target, light=light, comment=f"FIND {left_target.log()}")

                    drone_right = unassigned_drones.get(drone_right_idt)
                    if drone_right is not None:
                        light = use_light_to_find_a_target(drone_right, right_target)
                        my_drones_action[drone_right_idt] = Action(target=right_target, light=light, comment=f"FIND {right_target.log()}")

                else:
                    for drone_idt, drone in unassigned_drones.items():
                        if drone.extra_score_with_unsaved_creatures > 0:
                            my_drones_action[drone.idt] = Action(target=Point(drone.x, 499), comment=f"SAVE {drone.extra_score_with_unsaved_creatures}")
                        else:
                            drone_target = order_assets(creatures.values(), on_attr='foe_extra_score', ascending=False)[nb_find_actions]
                            nb_find_actions += 1
                            my_drones_action[drone.idt] = Action(target=drone_target, light=True, comment=f"FIND {drone_target.log()}")

            # COMPUTE ALGORITHMS FOR DRONE TO ACT - END

            for drone_idt in self.my_drones_idt_play_order:
                print(my_drones_action[drone_idt])
