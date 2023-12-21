import sys
from typing import List

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
            creature_id, color, kind = [int(j) for j in self.get_init_input().split()]
            self.game_assets.create(asset_type=AssetType.CREATURE, idt=creature_id,
                                    attr_kwargs={"color": color, "kind": kind, "visible": False})
            self.creatures_idt.add(creature_id)

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
        # TODO : IMPROVE UPDATE OF RELATION BETWEEN SCAN AND CREATURE
        scan_idt = hash((owner, creature_idt))
        self.game_assets.update(asset_type=AssetType.SCAN, idt=scan_idt,
                                attr_kwargs={"owner": owner, "creature_idt": creature_idt, "saved": True})

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
                creature_id = int(self.get_turn_input())
                self.update_saved_scans(owner=MY_OWNER, creature_idt=creature_id)

            foe_scan_count = int(self.get_turn_input())
            for i in range(foe_scan_count):
                creature_id = int(self.get_turn_input())
                self.update_saved_scans(owner=FOE_OWNER, creature_idt=creature_id)

            my_drone_count = int(self.get_turn_input())
            for i in range(my_drone_count):
                drone_id, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
                self.game_assets.update(asset_type=AssetType.MYDRONE, idt=drone_id,
                                        attr_kwargs={"x": drone_x, "y": drone_y, "emergency": emergency,
                                                     "battery": battery})

            foe_drone_count = int(self.get_turn_input())
            for i in range(foe_drone_count):
                drone_id, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
                self.game_assets.update(asset_type=AssetType.FOEDRONE, idt=drone_id,
                                        attr_kwargs={"x": drone_x, "y": drone_y, "emergency": emergency,
                                                     "battery": battery})

            drone_scan_count = int(self.get_turn_input())
            my_drone_scan_count = 0
            for i in range(drone_scan_count):
                drone_id, creature_id = [int(j) for j in self.get_turn_input().split()]
                drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_id)
                if drone is None:
                    drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_id)
                else:
                    my_drone_scan_count += 1

                # TODO : IMPROVE UPDATE OF RELATION BETWEEN SCAN AND CREATURE
                scan_idt = hash((drone.owner, creature_id))
                self.game_assets.update(asset_type=AssetType.SCAN, idt=scan_idt,
                                        attr_kwargs={"owner": drone.owner, "creature_idt": creature_id,
                                                     "drone_idt": drone_id})

                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_id)
                creature.scans_idt.add(scan_idt)

            visible_creature_count = int(self.get_turn_input())
            unvisible_creatures = self.creatures_idt.copy()
            for i in range(visible_creature_count):
                creature_id, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in
                                                                                 self.get_turn_input().split()]
                unvisible_creatures.remove(creature_id)
                self.game_assets.update(asset_type=AssetType.CREATURE, idt=creature_id,
                                        attr_kwargs={"x": creature_x, "y": creature_y, "vx": creature_vx,
                                                     "vy": creature_vy, "visible": True})

            for creature_id in unvisible_creatures:
                self.game_assets.update(asset_type=AssetType.CREATURE, idt=creature_id,
                                        attr_kwargs={"visible": False})

            my_drones = self.game_assets.get_all(AssetType.MYDRONE)

            radar_blip_count = int(self.get_turn_input())
            my_drones_radar_count = {drone_idt: {radar: 0 for radar in CORNERS.keys()} for drone_idt in my_drones.keys()}
            for i in range(radar_blip_count):
                inputs = self.get_turn_input().split()
                drone_id = int(inputs[0])
                creature_id = int(inputs[1])
                radar = inputs[2]

                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_id)
                creature_scanned_by = [self.game_assets.get(AssetType.SCAN, scan_idt).owner for scan_idt in
                                       creature.scans_idt]  # TODO : improve
                if MY_OWNER not in creature_scanned_by:
                    my_drones_radar_count[drone_id][radar] += 1

            if GameLoop.LOG:
                self.print_turn_logs()

            # LOOK FOR TARGET
            creatures = self.game_assets.get_all(AssetType.CREATURE)

            drones_targets = {}
            for drone_id, drone in my_drones.items():
                eligible_targets, drone_target, d_min = {}, None, D_MAX
                for creature_id, creature in creatures.items():
                    creature_scanned_by = [self.game_assets.get(AssetType.SCAN, scan_idt).owner for scan_idt in
                                           creature.scans_idt]  # TODO : improve
                    if MY_OWNER not in creature_scanned_by:
                        eligible_targets[creature_id] = creature
                drones_targets[drone_id] = get_closest_unit_from(drone, eligible_targets)

            for drone_id, drone in my_drones.items():
                # MOVE <x> <y> <light (1|0)> | WAIT <light (1|0)>
                if my_drone_scan_count >= 4 or (my_scan_count + my_drone_scan_count >= 12):
                    print(f"MOVE {drone.x} {495} 0")
                else:
                    drone_target = drones_targets[drone_id]
                    if drone_target is None:
                        max_radar_count = 0
                        radar_chosen = None
                        for radar, radar_count in my_drones_radar_count[drone_id].items():
                            if radar_count >= max_radar_count:
                                radar_chosen = radar
                                max_radar_count = radar_count
                        drone_target = CORNERS[radar_chosen]
                    print(f"MOVE {drone_target.x} {drone_target.y} 1")
