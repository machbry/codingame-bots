import sys
from enum import Enum
from typing import List

class Coordinates:
    __slots__ = ('x', 'y')

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Tree:
    __slots__ = ('coordinates', '_type', 'size', 'health', 'fruits', 'cooldown')

    def __init__(self, coordinates: Coordinates, _type: str, size: int, health: int, fruits: int, cooldown: int):
        self.coordinates = coordinates
        self._type = _type
        self.size = size
        self.health = health
        self.fruits = fruits
        self.cooldown = cooldown

    @property
    def can_be_harvested(self) -> bool:
        return self.fruits > 0

class Troll:
    __slots__ = ('_id', 'player', 'coordinates', 'movement_speed', 'carry_capacity', 'harvest_power', 'chop_power')

    def __init__(self, _id: int, player: int, coordinates: Coordinates, movement_speed: int, carry_capacity: int, harvest_power: int, chop_power: int):
        self._id = _id
        self.player = player
        self.coordinates = coordinates
        self.movement_speed = movement_speed
        self.carry_capacity = carry_capacity
        self.harvest_power = harvest_power
        self.chop_power = chop_power

    def harvest(self, tree: Tree) -> int:
        if not tree.can_be_harvested:
            return 0
        if self.coordinates != tree.coordinates:
            return 0
        return min(self.carry_capacity, self.harvest_power, tree.fruits)

def log(message):
    print(message, file=sys.stderr, flush=True)

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'actions', 'width', 'height', 'lines', 'trees', 'trolls')
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
        self.trees = []
        self.trolls = []
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
        self.trees = []
        for i in range(trees_count):
            inputs = self.get_turn_input().split()
            _type = inputs[0]
            x = int(inputs[1])
            y = int(inputs[2])
            size = int(inputs[3])
            health = int(inputs[4])
            fruits = int(inputs[5])
            cooldown = int(inputs[6])
            tree = Tree(coordinates=Coordinates(x, y), _type=_type, size=size, health=health, fruits=fruits, cooldown=cooldown)
            self.trees.append(tree)
        trolls_count = int(self.get_turn_input())
        self.trolls = []
        for i in range(trolls_count):
            _id, player, x, y, movement_speed, carry_capacity, harvest_power, chop_power, carry_plum, carry_lemon, carry_apple, carry_banana, carry_iron, carry_wood = [int(j) for j in self.get_turn_input().split()]
            troll = Troll(_id=_id, player=player, coordinates=Coordinates(x, y), movement_speed=movement_speed, carry_capacity=carry_capacity, harvest_power=harvest_power, chop_power=chop_power)
            self.trolls.append(troll)
        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()
            print('MOVE 0 7 7')
GameLoop().start()