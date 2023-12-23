import sys
from typing import List

from botlibs.trigonometry import Point
from bots.fall_challenge_2023.challengelibs.act import Action
from bots.fall_challenge_2023.challengelibs.game_assets import AssetType, GameAssets
from bots.fall_challenge_2023.challengelibs.map import get_closest_unit_from
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER, HASH_MAP_NORMS, D_MAX, CORNERS


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

        self.creatures_idt = set()
        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]

            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind
            creature.visible = False

            self.creatures_idt.add(creature_idt)

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

    def update_saved_scans(self, owner: int, creature_idt: int):
        scan_idt = hash((owner, creature_idt))

        scan = self.game_assets.get(asset_type=AssetType.SCAN, idt=scan_idt)
        if scan is None:
            scan = self.game_assets.new_asset(asset_type=AssetType.SCAN, idt=scan_idt)
        scan.owner = owner
        scan.creature_idt = creature_idt
        scan.saved = True

        creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
        creature.scans_idt.add(scan_idt)

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def start(self):
        while GameLoop.RUNNING:
            self.nb_turns += 1

            my_score = int(self.get_turn_input())
            foe_score = int(self.get_turn_input())

            my_scan_count = int(self.get_turn_input())
            for i in range(my_scan_count):
                creature_idt = int(self.get_turn_input())
                self.update_saved_scans(owner=MY_OWNER, creature_idt=creature_idt)

            foe_scan_count = int(self.get_turn_input())
            for i in range(foe_scan_count):
                creature_idt = int(self.get_turn_input())
                self.update_saved_scans(owner=FOE_OWNER, creature_idt=creature_idt)

            drones_scan_count = {}

            my_drone_count = int(self.get_turn_input())
            for i in range(my_drone_count):
                drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
                drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_idt)
                if drone is None:
                    drone = self.game_assets.new_asset(asset_type=AssetType.MYDRONE, idt=drone_idt)
                drone.x = drone_x
                drone.y = drone_y
                drone.emergency = emergency
                drone.battery = battery

                drones_scan_count[drone_idt] = 0

            foe_drone_count = int(self.get_turn_input())
            for i in range(foe_drone_count):
                drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
                drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_idt)
                if drone is None:
                    drone = self.game_assets.new_asset(asset_type=AssetType.FOEDRONE, idt=drone_idt)
                drone.x = drone_x
                drone.y = drone_y
                drone.emergency = emergency
                drone.battery = battery

                drones_scan_count[drone_idt] = 0

            drone_scan_count = int(self.get_turn_input())
            my_drones_scan_count = 0
            for i in range(drone_scan_count):
                drone_idt, creature_idt = [int(j) for j in self.get_turn_input().split()]
                drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_idt)
                if drone is None:
                    drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_idt)
                else:
                    my_drones_scan_count += 1
                drones_scan_count[drone_idt] += 1

                scan_idt = hash((drone.owner, creature_idt))
                scan = self.game_assets.get(asset_type=AssetType.SCAN, idt=scan_idt)
                if scan is None:
                    scan = self.game_assets.new_asset(asset_type=AssetType.SCAN, idt=scan_idt)
                scan.owner = drone.owner
                scan.creature_idt = creature_idt
                scan.drone_idt = drone_idt

                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
                creature.scans_idt.add(scan_idt)

            visible_creature_count = int(self.get_turn_input())
            unvisible_creatures = self.creatures_idt.copy()
            for i in range(visible_creature_count):
                creature_idt, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in
                                                                                 self.get_turn_input().split()]
                unvisible_creatures.remove(creature_idt)
                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
                creature.x = creature_x
                creature.y = creature_y
                creature.vx = creature_vx
                creature.vy = creature_vy
                creature.visible = True

            for creature_idt in unvisible_creatures:
                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
                creature.visible = False

            my_drones = self.game_assets.get_all(AssetType.MYDRONE)

            radar_blip_count = int(self.get_turn_input())
            my_drones_radar_count = {drone_idt: {radar: 0 for radar in CORNERS.keys()} for drone_idt in my_drones.keys()}
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
                radar_blip.radar = radar

                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
                creature_scanned_by = [self.game_assets.get(AssetType.SCAN, scan_idt).owner for scan_idt in
                                       creature.scans_idt]  # TODO : improve
                if MY_OWNER not in creature_scanned_by:
                    my_drones_radar_count[drone_idt][radar] += 1

            if GameLoop.LOG:
                self.print_turn_logs()

            creatures = self.game_assets.get_all(AssetType.CREATURE)

            drones_targets = {}
            for drone_idt, drone in my_drones.items():
                eligible_targets, drone_target, d_min = {}, None, D_MAX
                for creature_idt, creature in creatures.items():
                    creature_scanned_by = [self.game_assets.get(AssetType.SCAN, scan_idt).owner for scan_idt in
                                           creature.scans_idt]  # TODO : improve
                    if MY_OWNER not in creature_scanned_by:
                        eligible_targets[creature_idt] = creature
                drones_targets[drone_idt] = get_closest_unit_from(drone, eligible_targets)

            for drone_idt, drone in my_drones.items():
                # MOVE <x> <y> <light (1|0)> | WAIT <light (1|0)>
                if drones_scan_count[drone_idt] >= 4 or (my_scan_count + my_drones_scan_count >= 12):
                    action = Action(target=Point(drone.x, 499))
                else:
                    drone_target = drones_targets[drone_idt]
                    if drone_target is None:
                        max_radar_count = 0
                        radar_chosen = None
                        for radar, radar_count in my_drones_radar_count[drone_idt].items():
                            if radar_count >= max_radar_count:
                                radar_chosen = radar
                                max_radar_count = radar_count
                        drone_target = CORNERS[radar_chosen]
                    action = Action(target=drone_target, light=True)
                print(action)
