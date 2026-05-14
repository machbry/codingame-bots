import sys
from enum import Enum
from typing import List

class BoxType(Enum):
    GRASS = '.'
    MY_SHACK = '0'
    ENNEMY_SHACK = '1'

class ActionType(Enum):
    MOVE = 'MOVE'
    HARVEST = 'HARVEST'
    DROP = 'DROP'
    WAIT = 'WAIT'
    MSG = 'MSG'

class Coordinates:
    __slots__ = ('x', 'y')

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Grid:
    __slots__ = 'lines'

    def __init__(self, lines: list[str]):
        self.lines = lines

    def player_shack_coordinates(self, player: int) -> Coordinates:
        looking_for_box_type = BoxType.MY_SHACK if player == 0 else BoxType.ENNEMY_SHACK
        for y, line in enumerate(self.lines):
            for x, car in enumerate(line):
                if car == looking_for_box_type.value:
                    return Coordinates(x, y)

class Action:
    __slots__ = ('action_type', 'coordinates', '_id', 'text')

    def __init__(self, action_type: ActionType=ActionType.WAIT, coordinates: Coordinates=None, _id: int=None, text: str=None):
        self.action_type = action_type
        self.coordinates = coordinates
        self._id = _id
        self.text = text

    def __repr__(self):
        attrs = [self.action_type.value, self._id, self.coordinates.x if self.coordinates else None, self.coordinates.y if self.coordinates else None, self.text]
        not_null_attrs = [attr for attr in attrs if attr is not None]
        return ' '.join(not_null_attrs)

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
    __slots__ = ('_id', 'player', 'coordinates', 'movement_speed', 'carry_capacity', 'harvest_power', 'chop_power', 'carry_plum', 'carry_lemon', 'carry_apple', 'carry_banana', 'carry_iron', 'carry_wood')

    def __init__(self, _id: int, player: int, coordinates: Coordinates, movement_speed: int, carry_capacity: int, harvest_power: int, chop_power: int, carry_plum: int, carry_lemon: int, carry_apple: int, carry_banana: int, carry_iron: int, carry_wood: int):
        self._id = _id
        self.player = player
        self.coordinates = coordinates
        self.movement_speed = movement_speed
        self.carry_capacity = carry_capacity
        self.harvest_power = harvest_power
        self.chop_power = chop_power
        self.carry_plum = carry_plum
        self.carry_lemon = carry_lemon
        self.carry_apple = carry_apple
        self.carry_banana = carry_banana
        self.carry_iron = carry_iron
        self.carry_wood = carry_wood

    @property
    def is_my_troll(self) -> bool:
        return self.player == 0

def log(message):
    print(message, file=sys.stderr, flush=True)

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'actions', 'width', 'height', 'lines', 'grid', 'my_chack_coordinates', 'trees', 'trolls')
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.actions: list[Action] = []
        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.lines = []
        for i in range(self.height):
            line = self.get_init_input()
            self.lines.append(line)
        self.grid = Grid(lines=self.lines)
        self.my_chack_coordinates = self.grid.player_shack_coordinates(player=0)
        self.trees: list[Tree] = []
        self.trolls: list[Troll] = []
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
            troll = Troll(_id=_id, player=player, coordinates=Coordinates(x, y), movement_speed=movement_speed, carry_capacity=carry_capacity, harvest_power=harvest_power, chop_power=chop_power, carry_plum=carry_plum, carry_lemon=carry_lemon, carry_apple=carry_apple, carry_banana=carry_banana, carry_iron=carry_iron, carry_wood=carry_wood)
            self.trolls.append(troll)
        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()
            my_trolls = [troll for troll in self.trolls if troll.is_my_troll]
            self.actions = []
            for troll in my_trolls:
                troll_action = Action()
                self.actions.append(troll_action)
            for action in self.actions:
                print(action)
GameLoop().start()