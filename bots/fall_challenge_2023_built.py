import sys
from typing import List

class GameLoop:
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            (creature_id, color, kind) = [int(j) for j in self.get_init_input().split()]
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

    def start(self):
        while GameLoop.RUNNING:
            self.nb_turns += 1
            my_score = int(self.get_turn_input())
            foe_score = int(self.get_turn_input())
            my_scan_count = int(self.get_turn_input())
            for i in range(my_scan_count):
                creature_id = int(self.get_turn_input())
            foe_scan_count = int(self.get_turn_input())
            for i in range(foe_scan_count):
                creature_id = int(self.get_turn_input())
            my_drone_count = int(self.get_turn_input())
            for i in range(my_drone_count):
                (drone_id, drone_x, drone_y, emergency, battery) = [int(j) for j in self.get_turn_input().split()]
            foe_drone_count = int(self.get_turn_input())
            for i in range(foe_drone_count):
                (drone_id, drone_x, drone_y, emergency, battery) = [int(j) for j in self.get_turn_input().split()]
            drone_scan_count = int(self.get_turn_input())
            for i in range(drone_scan_count):
                (drone_id, creature_id) = [int(j) for j in self.get_turn_input().split()]
            visible_creature_count = int(self.get_turn_input())
            for i in range(visible_creature_count):
                (creature_id, creature_x, creature_y, creature_vx, creature_vy) = [int(j) for j in self.get_turn_input().split()]
            radar_blip_count = int(self.get_turn_input())
            for i in range(radar_blip_count):
                inputs = self.get_turn_input().split()
                drone_id = int(inputs[0])
                creature_id = int(inputs[1])
                radar = inputs[2]
            if GameLoop.LOG:
                print(self.nb_turns, file=sys.stderr, flush=True)
                print(self.turns_inputs, file=sys.stderr, flush=True)
            if GameLoop.RESET_TURNS_INPUTS:
                self.turns_inputs = []
            for i in range(my_drone_count):
                print('WAIT 1')
GameLoop().start()