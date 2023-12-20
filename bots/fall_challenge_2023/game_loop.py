import sys
from typing import List

from bots.fall_challenge_2023.challengelibs.game_assets import GameAssets, AssetType
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER, HASH_MAP_NORMS, D_MAX


class GameLoop:
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.game_assets = GameAssets()
        self.hash_map_norms = HASH_MAP_NORMS

        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_id, color, kind = [int(j) for j in self.get_init_input().split()]
            self.game_assets.create(asset_type=AssetType.CREATURE, idt=creature_id,
                                    attr_kwargs={"color": color, "kind": kind, "visible": False})

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
                scan_idt = hash((MY_OWNER, creature_id))
                self.game_assets.update(asset_type=AssetType.SCAN, idt=scan_idt,
                                        attr_kwargs={"owner": MY_OWNER, "creature_idt": creature_id})

                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_id)
                creature.scanned_by.add(MY_OWNER)

            foe_scan_count = int(self.get_turn_input())
            for i in range(foe_scan_count):
                creature_id = int(self.get_turn_input())
                self.game_assets.update(asset_type=AssetType.SCAN, idt=hash((FOE_OWNER, creature_id)),
                                        attr_kwargs={"owner": FOE_OWNER, "creature_idt": creature_id})

                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_id)
                creature.scanned_by.add(FOE_OWNER)

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
            for i in range(drone_scan_count):
                drone_id, creature_id = [int(j) for j in self.get_turn_input().split()]

            visible_creature_count = int(self.get_turn_input())
            for i in range(visible_creature_count):
                creature_id, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in
                                                                                 self.get_turn_input().split()]
                self.game_assets.update(asset_type=AssetType.CREATURE, idt=creature_id,
                                        attr_kwargs={"x": creature_x, "y": creature_y, "vx": creature_vx,
                                                     "vy": creature_vy, "visible": True})

            radar_blip_count = int(self.get_turn_input())
            for i in range(radar_blip_count):
                inputs = self.get_turn_input().split()
                drone_id = int(inputs[0])
                creature_id = int(inputs[1])
                radar = inputs[2]

            if GameLoop.LOG:
                self.print_turn_logs()

            # LOOK FOR TARGET
            my_drones = self.game_assets.get_all(AssetType.MYDRONE)
            creatures = self.game_assets.get_all(AssetType.CREATURE)

            drones_targets = {}
            for drone_id, drone in my_drones.items():
                drone_target, d_min = None, D_MAX
                for creature_id, creature in creatures.items():
                    if MY_OWNER not in creature.scanned_by:
                        drone_to_creature_vector = creature.position - drone.position
                        drone_to_creature_distance = self.hash_map_norms[drone_to_creature_vector]
                        if drone_to_creature_distance <= d_min:
                            d_min = drone_to_creature_distance
                            drone_target = creature
                drones_targets[drone_id] = drone_target

            for drone_id, drone in my_drones.items():
                # MOVE <x> <y> <light (1|0)> | WAIT <light (1|0)>
                drone_target = drones_targets[drone_id]
                if drone_target is None:
                    print(f"MOVE {drone.x} 0 0")
                else:
                    print(f"MOVE {drone_target.x} {drone_target.y} 0")
