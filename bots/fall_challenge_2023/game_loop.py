import sys
from typing import List, Dict

import numpy as np

from bots.fall_challenge_2023.challengelibs.act import Action, choose_action_for_drones
from bots.fall_challenge_2023.challengelibs.asset import Creature, Score
from bots.fall_challenge_2023.challengelibs.algorithms import (avoid_monsters, save_points, find_valuable_target,
                                                               just_do_something, deny_valuable_fish_for_foe)
from bots.fall_challenge_2023.challengelibs.game_assets import AssetType, GameAssets
from bots.fall_challenge_2023.challengelibs.map import evaluate_positions_of_creatures, evaluate_monsters_to_avoid
from bots.fall_challenge_2023.challengelibs.score import update_saved_scans, update_trophies_for_all, \
    evaluate_extra_scores_for_multiple_scenarios, compute_score
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER, OWNERS, CORNERS, \
    CREATURE_HABITATS_PER_KIND, MAX_SPEED_PER_KIND, MAX_NUMBER_OF_RADAR_BLIPS_USED, COLORS, KINDS, \
    EMPTY_ARRAY_CREATURES, Kind


class GameLoop:
    __slots__ = (
    "init_inputs", "nb_turns", "turns_inputs", "game_assets", "empty_array_saved_creatures",
    "max_number_of_radar_blips_used", "max_speed_per_kind", "corners", "my_owner", "foe_owner", "owners",
    "owners_scores", "owners_scores_computed", "owners_extra_score_with_all_unsaved_creatures", "owners_max_possible_score",
    "owners_bonus_score_left", "my_drones_idt_play_order", "monsters", "total_units_count")
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.empty_array_saved_creatures = EMPTY_ARRAY_CREATURES
        self.max_number_of_radar_blips_used = MAX_NUMBER_OF_RADAR_BLIPS_USED
        self.max_speed_per_kind = MAX_SPEED_PER_KIND
        self.corners = CORNERS
        self.my_owner = MY_OWNER
        self.foe_owner = FOE_OWNER
        self.owners = OWNERS

        self.game_assets = GameAssets()
        self.owners_scores: Dict[int, int] = {}
        self.owners_scores_computed: Dict[int, Score] = {}
        self.owners_extra_score_with_all_unsaved_creatures: Dict[int, Score] = {}
        self.owners_max_possible_score: Dict[int, Score] = {}
        self.owners_bonus_score_left: Dict[int, Dict[str, int]] = {}
        self.my_drones_idt_play_order: List[int] = []
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

        self.total_units_count = creature_count + 4

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
            zone = radar_blip.zones[-i - 1]
            creature_max_speed = self.max_speed_per_kind[creature.kind]
            radar_blip.zones[-i - 1] = [zone[0] - creature_max_speed,
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
        for creature in self.game_assets.get_all(asset_type=AssetType.CREATURE).values():
            creature.visible = False
            creature.escaped = True

        self.nb_turns += 1

        self.owners_scores[self.my_owner] = int(self.get_turn_input())
        self.owners_scores[self.foe_owner] = int(self.get_turn_input())

        my_scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=self.my_owner)
        my_saved_creatures = my_scans.saved_creatures
        my_newly_saved_creatures = np.zeros_like(self.empty_array_saved_creatures)

        my_scan_count = int(self.get_turn_input())
        for i in range(my_scan_count):
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=int(self.get_turn_input()))
            creature_color, creature_kind = creature.color, creature.kind
            if update_saved_scans(my_saved_creatures, creature_color, creature_kind):
                my_newly_saved_creatures[creature_color, creature_kind] = self.my_owner

        foe_scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=self.foe_owner)
        foe_saved_creatures = foe_scans.saved_creatures
        foe_newly_saved_creatures = np.zeros_like(self.empty_array_saved_creatures)

        foe_scan_count = int(self.get_turn_input())
        for i in range(foe_scan_count):
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=int(self.get_turn_input()))
            creature_color, creature_kind = creature.color, creature.kind
            if update_saved_scans(foe_saved_creatures, creature_color, creature_kind):
                foe_newly_saved_creatures[creature_color, creature_kind] = self.foe_owner

        update_trophies_for_all(my_saved_creatures=my_saved_creatures, foe_saved_creatures=foe_saved_creatures,
                                my_newly_saved_creatures=my_newly_saved_creatures,
                                foe_newly_saved_creatures=foe_newly_saved_creatures,
                                trophies=self.game_assets.get(AssetType.TROPHIES, 42))

        my_drone_count = int(self.get_turn_input())
        self.my_drones_idt_play_order = []
        for i in range(my_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            drone = self.game_assets.get(asset_type=AssetType.MY_DRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.new_asset(asset_type=AssetType.MY_DRONE, idt=drone_idt)
            drone.x = drone_x
            drone.y = drone_y
            drone.emergency = emergency
            drone.battery = battery
            drone.unsaved_creatures_idt = set()
            self.my_drones_idt_play_order.append(drone_idt)

        foe_drone_count = int(self.get_turn_input())
        for i in range(foe_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            drone = self.game_assets.get(asset_type=AssetType.FOE_DRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.new_asset(asset_type=AssetType.FOE_DRONE, idt=drone_idt)
            drone.x = drone_x
            drone.y = drone_y
            drone.emergency = emergency
            drone.battery = battery
            drone.unsaved_creatures_idt = set()

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

            for owner in self.owners:
                self.owners_scores_computed[owner] = compute_score(owner=owner, saved_creatures=scans[owner].saved_creatures,
                                                                   creatures_win_by=trophies.creatures_win_by,
                                                                   colors_win_by=trophies.colors_win_by,
                                                                   kinds_win_by=trophies.kinds_win_by)

            # note : extra scores for creatures or drones are directly stored in these assets
            self.owners_extra_score_with_all_unsaved_creatures, self.owners_max_possible_score, self.owners_bonus_score_left = (
                evaluate_extra_scores_for_multiple_scenarios(creatures=creatures, my_drones=my_drones,
                                                             foe_drones=foe_drones, scans=scans,
                                                             trophies=trophies,
                                                             current_owners_scores=self.owners_scores_computed))

            evaluate_positions_of_creatures(creatures=creatures, radar_blips=radar_blips,
                                            my_drones=my_drones, nb_turns=self.nb_turns)

            evaluate_monsters_to_avoid(my_drones=my_drones, monsters=self.monsters)

            default_action = Action(move=False, light=False)

            save_actions = save_points(my_drones=my_drones, owners_scores_computed=self.owners_scores_computed,
                                       owners_max_possible_score=self.owners_max_possible_score,
                                       owners_extra_score_with_all_unsaved_creatures=self.owners_extra_score_with_all_unsaved_creatures,
                                       owners_bonus_score_left=self.owners_bonus_score_left)

            deny_actions = deny_valuable_fish_for_foe(my_drones=my_drones, creatures=creatures, foe_drones=foe_drones)

            find_actions = find_valuable_target(my_drones=my_drones, creatures=creatures, total_units_count=self.total_units_count)

            just_do_something_actions = {}
            if len(deny_actions) < 2 and len(save_actions) < 2 and len(find_actions) < 2:
                just_do_something_actions = just_do_something(my_drones=my_drones, creatures=creatures)

            actions_priorities = [save_actions, deny_actions, find_actions, just_do_something_actions]
            my_drones_action = choose_action_for_drones(my_drones=my_drones, actions_priorities=actions_priorities,
                                                        default_action=default_action)

            for drone_idt in self.my_drones_idt_play_order:
                my_drone = my_drones[drone_idt]
                safe_action = avoid_monsters(my_drone, my_drones_action[drone_idt], default_action)
                my_drone.light_on = safe_action.light
                print(safe_action)
