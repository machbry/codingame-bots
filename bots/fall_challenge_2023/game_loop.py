import sys
from typing import List, Union

from botlibs.trigonometry import Point
from bots.fall_challenge_2023.challengelibs.act import Action
from bots.fall_challenge_2023.challengelibs.asset import Scores
from bots.fall_challenge_2023.challengelibs.game_assets import AssetType, GameAssets
from bots.fall_challenge_2023.challengelibs.map import get_closest_unit_from
from bots.fall_challenge_2023.challengelibs.score import evaluate_extra_score_for_owner_creature, order_assets
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
        self.current_scores = Scores()
        self.drones_scan_count = {}  # TODO : REMOVE

        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]
            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind

            for owner in [MY_OWNER, FOE_OWNER]:
                scan_idt = hash((owner, creature_idt))
                scan = self.game_assets.new_asset(asset_type=AssetType.SCAN, idt=scan_idt)
                scan.owner = owner
                scan.creature_idt = creature_idt

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
        scan_idt = hash((owner, creature_idt))

        scan = self.game_assets.get(asset_type=AssetType.SCAN, idt=scan_idt)

        if scan.saved:
            return

        scan.saved = True

        if scan.first_saved_by is None:
            scan.first_saved_by = owner
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.saved_by_owners.add(owner)

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
            drone.unsaved_scans_idt = set()

        self.drones_scan_count[drone_idt] = 0

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def start(self):
        while GameLoop.RUNNING:
            """ RESET ASSETS - BEGIN """

            for creature in self.game_assets.get_all(asset_type=AssetType.CREATURE).values():
                creature.scanned_by_drones = set()
                creature.visible = False
                creature.escaped = True

            for scan in self.game_assets.get_all(asset_type=AssetType.SCAN).values():
                scan.owned_by_drones = set()

            self.drones_scan_count = {}  # TODO : REMOVE

            """ RESET ASSETS - END """

            """ UPDATE ASSETS - BEGIN """

            self.nb_turns += 1

            my_score = int(self.get_turn_input())
            foe_score = int(self.get_turn_input())
            self.current_scores = Scores(me=my_score, foe=foe_score)

            my_scan_count = int(self.get_turn_input())
            for i in range(my_scan_count):
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
            my_drones_scan_count = 0
            for i in range(drone_scan_count):
                drone_idt, creature_idt = [int(j) for j in self.get_turn_input().split()]
                drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_idt)
                if drone is None:
                    drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_idt)
                else:
                    my_drones_scan_count += 1

                scan_idt = hash((drone.owner, creature_idt))
                scan = self.game_assets.get(asset_type=AssetType.SCAN, idt=scan_idt)
                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)

                drone.unsaved_scans_idt.add(scan_idt)
                scan.owned_by_drones.add(drone_idt)
                creature.scanned_by_drones.add(drone_idt)

                self.drones_scan_count[drone_idt] += 1  # TODO : REMOVE

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

            radar_blip_count = int(self.get_turn_input())
            my_drones_radar_count = {drone_idt: {radar: 0 for radar in CORNERS.keys()} for drone_idt in
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
                radar_blip.radar = radar

                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
                if creature is not None:
                    creature.escaped = False

                    # TODO : REMOVE
                    if drone_idt not in creature.scanned_by_drones:
                        my_drones_radar_count[drone_idt][radar] += 1

            if GameLoop.LOG:
                self.print_turn_logs()

            """ UPDATE ASSETS - END """

            """ COMPUTE EXTRA METRICS FOR ASSETS - BEGIN """

            my_drones = self.game_assets.get_all(AssetType.MYDRONE)
            foe_drones = self.game_assets.get_all(AssetType.FOEDRONE)
            creatures = self.game_assets.get_all(AssetType.CREATURE)

            all_drones = [*my_drones.values(), *foe_drones.values()]
            ordered_drones_from_top_to_bottom = order_assets(all_drones, 'y')

            for creature in creatures.values():
                creature.eval_saved_by_owners = creature.saved_by_owners.copy()

            for drone in ordered_drones_from_top_to_bottom:
                for scan_idt in drone.unsaved_scans_idt:
                    scan = self.game_assets.get(AssetType.SCAN, scan_idt)
                    unsaved_creature = self.game_assets.get(AssetType.CREATURE, scan.creature_idt)

                    unsaved_creature_saved_by_owners = unsaved_creature.eval_saved_by_owners

                    creature_saved_by_owner = drone.owner in unsaved_creature_saved_by_owners
                    creature_saved_by_other_owner = drone.owner in unsaved_creature_saved_by_owners

                    extra_score = evaluate_extra_score_for_owner_creature(creature_kind=unsaved_creature.kind,
                                                                          creature_escaped=unsaved_creature.escaped,
                                                                          creature_saved_by_owner=creature_saved_by_owner,
                                                                          creature_saved_by_other_owner=creature_saved_by_other_owner)
                    # TODO : WIP

            # POUR CHAQUE DRONE ORDONNE :
            #   RECUPERE LES CREATURES ASSOCIEES A SES SCANS NON SAUVEGARDES
            #   POUR CHAQUE CREATURE :
                #   CALCULE LE SCORE SUPPLEMENTAIRE
                #   MET A JOUR LE SET DEVAL


            """ COMPUTE EXTRA METRICS FOR ASSETS - END """

            """ COMPUTE ALGORITHMS FOR DRONE TO ACT - BEGIN """
            # TODO : MOVE ALGORITHM TO CHOSE ACTION
            drones_targets = {}
            for drone_idt, drone in my_drones.items():
                eligible_targets, drone_target, d_min = {}, None, D_MAX
                for creature_idt, creature in creatures.items():
                    if drone_idt not in creature.scanned_by_drones and creature.kind != -1 and not creature.escaped:
                        eligible_targets[creature_idt] = creature
                drones_targets[drone_idt] = get_closest_unit_from(drone, eligible_targets)

            for drone_idt, drone in my_drones.items():
                if self.drones_scan_count[drone_idt] >= 4 or (my_scan_count + my_drones_scan_count >= 12):
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

            """ COMPUTE ALGORITHMS FOR DRONE TO ACT - END """
