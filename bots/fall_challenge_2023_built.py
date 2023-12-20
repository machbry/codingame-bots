import math
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Dict

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if isinstance(other, Point):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, nombre):
        return Point(nombre * self.x, nombre * self.y)

    def __rmul__(self, nombre):
        return self * nombre

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def dist(self, point):
        return math.dist([self.x, self.y], [point.x, point.y])

class Vector(Point):

    def __init__(self, x, y):
        super().__init__(x, y)

    def __mul__(self, nombre):
        return Vector(nombre * self.x, nombre * self.y)

    @property
    def norm(self):
        return (self.x ** 2 + self.y ** 2) ** (1 / 2)

    def dot(self, vector):
        return self.x * vector.x + self.y * vector.y

@dataclass
class Unit:
    idt: int
    x: int = None
    y: int = None
    vx: int = None
    vy: int = None

    def position(self):
        return Point(self.x, self.y)

    def speed(self):
        return Vector(self.vx, self.vy)

    def __hash__(self):
        return hash(self.idt)

@dataclass
class Creature(Unit):
    color: int = (None,)
    kind: int = (None,)
    visible: bool = None

@dataclass
class Drone(Unit):
    emergency: int = (None,)
    battery: int = (None,)

@dataclass
class MyDrone(Drone):
    owner: int = 1

@dataclass
class FoeDrone(Drone):
    owner: int = 2

class DataType(Enum):
    CREATURE = Creature
    MYDRONE = MyDrone
    FOEDRONE = FoeDrone

class Singleton(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance

class GameData(Singleton):

    def __init__(self):
        self.data_sources: Dict[str, Dict[int, Any]] = {data_type.name: {} for data_type in DataType.__iter__()}

    def create(self, data_type: DataType, idt: int, attr_kwargs: Dict[str, Any]):
        attr_kwargs['idt'] = idt
        instance = data_type.value(**attr_kwargs)
        self.data_sources[data_type.name][idt] = instance

    def update(self, data_type: DataType, idt: int, attr_kwargs: Dict[str, Any]):
        instance = self.data_sources[data_type.name].get(idt)
        if instance is None:
            self.create(data_type, idt, attr_kwargs)
        else:
            for (name, value) in attr_kwargs.items():
                setattr(instance, name, value)

    def get(self, data_type: DataType, idt: int):
        return self.data_sources[data_type.name].get(idt)

    def delete(self, data_type: DataType, idt: int):
        del self.data_sources[data_type.name][idt]

class GameLoop:
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.game_data = GameData()
        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            (creature_id, color, kind) = [int(j) for j in self.get_init_input().split()]
            self.game_data.create(data_type=DataType.CREATURE, idt=creature_id, attr_kwargs={'color': color, 'kind': kind, 'visible': False})
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
                self.game_data.update(data_type=DataType.MYDRONE, idt=drone_id, attr_kwargs={'x': drone_x, 'y': drone_y, 'emergency': emergency, 'battery': battery})
            foe_drone_count = int(self.get_turn_input())
            for i in range(foe_drone_count):
                (drone_id, drone_x, drone_y, emergency, battery) = [int(j) for j in self.get_turn_input().split()]
                self.game_data.update(data_type=DataType.FOEDRONE, idt=drone_id, attr_kwargs={'x': drone_x, 'y': drone_y, 'emergency': emergency, 'battery': battery})
            drone_scan_count = int(self.get_turn_input())
            for i in range(drone_scan_count):
                (drone_id, creature_id) = [int(j) for j in self.get_turn_input().split()]
            visible_creature_count = int(self.get_turn_input())
            for i in range(visible_creature_count):
                (creature_id, creature_x, creature_y, creature_vx, creature_vy) = [int(j) for j in self.get_turn_input().split()]
                self.game_data.update(data_type=DataType.CREATURE, idt=creature_id, attr_kwargs={'x': creature_x, 'y': creature_y, 'vx': creature_vx, 'vy': creature_vy, 'visible': True})
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