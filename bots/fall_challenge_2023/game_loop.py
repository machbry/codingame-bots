import sys
from typing import List, Union

import numpy as np

from botlibs.trigonometry import Point, Vector
from bots.fall_challenge_2023.challengelibs.act import Action
from bots.fall_challenge_2023.challengelibs.game_assets import AssetType, GameAssets
from bots.fall_challenge_2023.challengelibs.map import get_closest_unit_from
from bots.fall_challenge_2023.challengelibs.score import evaluate_extra_score_for_owner_creature, order_assets
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER, OWNERS, HASH_MAP_NORMS, D_MAX, CORNERS, \
    CREATURE_HABITATS_PER_KIND, LIGHT_RADIUS, DRONE_SPEED, SAFE_RADIUS_FROM_MONSTERS

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

        self.visible_monsters = []
        self.my_drones_scan_count = 0
        self.my_scan_count = 0
        self.drones_scan_count = {}  # TODO : REMOVE

        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]
            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind
            creature.habitat = CREATURE_HABITATS_PER_KIND[kind]

            for owner in OWNERS:
                scan = self.game_assets.new_asset(asset_type=AssetType.SCANS, idt=owner)
                scan.owner = owner
                scan.saved_creatures = np.zeros(shape=(4, 3))

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

        creature_saved = scans.saved_creatures[creature.color, creature.kind]

        if creature_saved == 1:
            return

        scans.saved_creatures[creature.color, creature.kind] = 1
        creature.saved_by_owners.append(owner)

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

        self.drones_scan_count[drone_idt] = 0

    def update(self):
        self.nb_turns += 1

        my_score = int(self.get_turn_input())
        foe_score = int(self.get_turn_input())

        self.my_scan_count = int(self.get_turn_input())
        for i in range(self.my_scan_count):
            creature_idt = int(self.get_turn_input())
            self.update_saved_scan(owner=MY_OWNER, creature_idt=creature_idt)

        foe_scan_count = int(self.get_turn_input())
        for i in range(foe_scan_count):
            creature_idt = int(self.get_turn_input())
            self.update_saved_scan(owner=FOE_OWNER, creature_idt=creature_idt)

        my_drone_count = int(self.get_turn_input())
        for i in range(my_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            self.update_drone(drone_idt, drone_x, drone_y, emergency, battery, AssetType.MYDRONE)

        foe_drone_count = int(self.get_turn_input())
        for i in range(foe_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            self.update_drone(drone_idt, drone_x, drone_y, emergency, battery, AssetType.FOEDRONE)

        drone_scan_count = int(self.get_turn_input())
        self.my_drones_scan_count = 0
        for i in range(drone_scan_count):
            drone_idt, creature_idt = [int(j) for j in self.get_turn_input().split()]

            drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_idt)
            else:
                self.my_drones_scan_count += 1

            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)

            drone.unsaved_creatures_idt.add(creature_idt)
            creature.scanned_by_drones.add(drone_idt)

            self.drones_scan_count[drone_idt] += 1  # TODO : REMOVE

        visible_creature_count = int(self.get_turn_input())
        self.visible_monsters = []
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

            # EVALUATE NEXT POSITION
            creature_next_position = creature.position + creature.speed
            creature.next_x = creature_next_position.x
            creature.next_y = creature_next_position.y

            # VISIBLE MONSTERS
            if creature.kind == -1:
                self.visible_monsters.append(creature)

        radar_blip_count = int(self.get_turn_input())
        self.my_drones_radar_count = {drone_idt: {radar: 0 for radar in CORNERS.keys()} for drone_idt in
                                 self.game_assets.get_all(AssetType.MYDRONE).keys()}  # TODO : REMOVE
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

            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.escaped = False

            # TODO : REMOVE
            if drone_idt not in creature.scanned_by_drones:
                self.my_drones_radar_count[drone_idt][radar] += 1

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

            self.drones_scan_count = {}  # TODO : REMOVE

            # RESET ASSETS - END

            # UPDATE ASSETS - BEGIN

            self.update()

            # UPDATE ASSETS - END

            # COMPUTE EXTRA METRICS FOR ASSETS - BEGIN

            my_drones = self.game_assets.get_all(AssetType.MYDRONE)
            foe_drones = self.game_assets.get_all(AssetType.FOEDRONE)
            creatures = self.game_assets.get_all(AssetType.CREATURE)
            all_drones = [*my_drones.values(), *foe_drones.values()]

            # EVALUATE EXTRA SCORES - BEGIN
            # TODO : matrix representations & calculus for scores, combinaisons for colors & kinds
            ordered_drones_from_top_to_bottom = order_assets(all_drones, 'y')

            for creature in creatures.values():
                creature.eval_saved_by_owners = creature.saved_by_owners.copy()
                creature.extra_scores = {owner: 0 for owner in OWNERS}

            for drone in ordered_drones_from_top_to_bottom:
                drone.extra_score_with_unsaved_creatures = 0
                owner = drone.owner
                for creature_idt in drone.unsaved_creatures_idt:
                    creature = self.game_assets.get(AssetType.CREATURE, creature_idt)
                    extra_score = evaluate_extra_score_for_owner_creature(creature_kind=creature.kind,
                                                                          creature_escaped=creature.escaped,
                                                                          creature_saved_by_owners=creature.eval_saved_by_owners,
                                                                          owner=owner)
                    drone.extra_score_with_unsaved_creatures += extra_score
                    creature.eval_saved_by_owners.append(owner)

            for creature in creatures.values():
                for owner in OWNERS:
                    extra_score = evaluate_extra_score_for_owner_creature(creature_kind=creature.kind,
                                                                          creature_escaped=creature.escaped,
                                                                          creature_saved_by_owners=creature.eval_saved_by_owners,
                                                                          owner=owner)
                    creature.extra_scores[owner] += extra_score

            # EVALUATE EXTRA SCORES - END

            # EVALUATE POSITIONS OF UNVISIBLE CREATURES - BEGIN

            for creature_idt, creature in creatures.items():
                if not creature.visible:
                    possible_zones = [creature.habitat]
                    for drone_idt, drone in my_drones.items():
                        radar_idt = hash((drone_idt, creature_idt))
                        radar_blip = self.game_assets.get(asset_type=AssetType.RADARBLIP, idt=radar_idt)
                        possible_zones.append(radar_blip.zones[-1])
                    intersection = np.array(possible_zones)
                    creature.next_x = (np.max(intersection[:, 0]) + np.min(intersection[:, 2])) / 2
                    creature.next_y = (np.max(intersection[:, 1]) + np.min(intersection[:, 3])) / 2

            # EVALUATE POSITIONS OF UNVISIBLE CREATURES - END

            # CHECK IF MONSTERS ARE TOO CLOSE TO MY_DRONES - BEGIN

            my_drones_to_flee_from_monsters = {}
            for my_drone in my_drones.values():
                my_drone.has_to_flee_from = []
                for monster in self.visible_monsters:
                    if HASH_MAP_NORMS[monster.position - my_drone.position] <= SAFE_RADIUS_FROM_MONSTERS:
                        my_drone.has_to_flee_from.append(monster)

            # CHECK IF MONSTERS ARE TOO CLOSE TO MY_DRONES - END

            # COMPUTE EXTRA METRICS FOR ASSETS - END

            # COMPUTE ALGORITHMS FOR DRONE TO ACT - BEGIN
            drones_targets = {}
            for drone_idt, drone in my_drones.items():
                eligible_targets, drone_target, d_min = {}, None, D_MAX
                for creature_idt, creature in creatures.items():
                    if drone_idt not in creature.scanned_by_drones and creature.kind != -1 and not creature.escaped:
                        eligible_targets[creature_idt] = creature
                drones_targets[drone_idt] = get_closest_unit_from(drone, eligible_targets)

            for drone_idt, drone in my_drones.items():
                drone_has_to_flee_from = drone.has_to_flee_from
                if len(drone_has_to_flee_from) > 0:
                    flee_direction = Vector(0, 0)
                    for creature in drone_has_to_flee_from:
                        flee_direction += drone.position - creature.position
                    action = Action(target=drone.position + ((DRONE_SPEED ** (1/2)) / flee_direction.norm) * flee_direction, comment="FLEE")
                elif self.drones_scan_count[drone_idt] >= 4 or (self.my_scan_count + self.my_drones_scan_count >= 12):
                    action = Action(target=Point(drone.x, 499), comment="SAVE")
                else:
                    drone_target = drones_targets[drone_idt]
                    if drone_target is None:
                        max_radar_count = 0
                        radar_chosen = None
                        for radar, radar_count in self.my_drones_radar_count[drone_idt].items():
                            if radar_count >= max_radar_count:
                                radar_chosen = radar
                                max_radar_count = radar_count
                        drone_target = CORNERS[radar_chosen]
                    action = Action(target=drone_target, light=True, comment="EXPLORE")

                print(action)

            # COMPUTE ALGORITHMS FOR DRONE TO ACT - END
