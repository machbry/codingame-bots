from typing import List

from bots.summer_challenge_2026.challengelibs.logger import log


class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'actions', 'width', 'height', 'lines')

    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.actions: list[str] = []

        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.lines = []
        for i in range(self.height):
            line = self.get_init_input()
            self.lines.append(line)

        if GameLoop.LOG:
            self.print_init_logs()

    def get_init_input(self):
        result = input()
        self.init_inputs.append(result)
        return result

    def get_turn_input(self):
        result = input()
        self.turns_inputs.append(result)
        return result

    def print_init_logs(self):
        log(self.init_inputs)

    def print_turn_logs(self):
        log(self.nb_turns)
        log(self.turns_inputs)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def update_assets(self):
        self.nb_turns += 1

        for i in range(2):
            plum, lemon, apple, banana, iron, wood = [int(j) for j in self.get_turn_input().split()]
        
        trees_count = int(self.get_turn_input())
        for i in range(trees_count):
            inputs = self.get_turn_input().split()
            _type = inputs[0]
            x = int(inputs[1])
            y = int(inputs[2])
            size = int(inputs[3])
            health = int(inputs[4])
            fruits = int(inputs[5])
            cooldown = int(inputs[6])
        
        trolls_count = int(self.get_turn_input())
        for i in range(trolls_count):
            _id, player, x, y, movement_speed, carry_capacity, harvest_power, chop_power, carry_plum, carry_lemon, carry_apple, carry_banana, carry_iron, carry_wood = [int(j) for j in self.get_turn_input().split()]

        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()

            print("MOVE 0 7 7")

