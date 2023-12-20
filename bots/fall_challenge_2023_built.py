import sys
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Set, Dict, List, Literal

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

    def dot(self, vector):
        return self.x * vector.x + self.y * vector.y

    @property
    def norm2(self):
        return self.dot(self)

    @property
    def norm(self):
        return self.norm2 ** (1 / 2)

class HashMapNorms(object):

    def __new__(cls, norm_name: Literal['norm', 'norm2']):
        if not hasattr(cls, 'instance'):
            cls.instance = super(HashMapNorms, cls).__new__(cls)
        return cls.instance

    def __init__(self, norm_name: Literal['norm', 'norm2']):
        self.hasp_map: Dict[int, float] = {}
        self.norm_name = norm_name

    def _norm_of_vector(self, vector: Vector):
        vector_hash = hash(vector)
        try:
            return self.hasp_map[vector_hash]
        except KeyError:
            norm = getattr(vector, self.norm_name)
            self.hasp_map[vector_hash] = norm
            return norm

    def __getitem__(self, vector: Vector):
        return self._norm_of_vector(vector)
HASH_MAP_NORMS = HashMapNorms(norm_name='norm2')
MY_OWNER = 1
FOE_OWNER = 2
X_MIN = 0
Y_MIN = 0
X_MAX = 10000
Y_MAX = 10000
D_MAX = HASH_MAP_NORMS[Vector(X_MAX, Y_MAX)]

@dataclass
class Asset:
    idt: int

@dataclass
class Scan(Asset):
    owner: int = None
    creature_idt: int = None
    drone_idt: int = None
    saved: bool = False

@dataclass
class Unit(Asset):
    x: int = None
    y: int = None
    vx: int = None
    vy: int = None

    @property
    def position(self):
        return Point(self.x, self.y)

    @property
    def speed(self):
        return Vector(self.vx, self.vy)

@dataclass
class Creature(Unit):
    color: int = None
    kind: int = None
    visible: bool = False
    scans_idt: Set[int] = field(default_factory=set)

@dataclass
class Drone(Unit):
    emergency: int = None
    battery: int = None

@dataclass
class MyDrone(Drone):
    owner: int = MY_OWNER

@dataclass
class FoeDrone(Drone):
    owner: int = FOE_OWNER

class AssetType(Enum):
    CREATURE = Creature
    MYDRONE = MyDrone
    FOEDRONE = FoeDrone
    SCAN = Scan

class Singleton(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance

class GameAssets(Singleton):

    def __init__(self):
        self.assets: Dict[str, Dict[int, Any]] = {asset_type.name: {} for asset_type in AssetType.__iter__()}

    def create(self, asset_type: AssetType, idt: int, attr_kwargs: Dict[str, Any]):
        attr_kwargs['idt'] = idt
        asset = asset_type.value(**attr_kwargs)
        self.assets[asset_type.name][idt] = asset

    def update(self, asset_type: AssetType, idt: int, attr_kwargs: Dict[str, Any]):
        asset = self.assets[asset_type.name].get(idt)
        if asset is None:
            self.create(asset_type, idt, attr_kwargs)
        else:
            for (name, value) in attr_kwargs.items():
                setattr(asset, name, value)

    def get(self, asset_type: AssetType, idt: int):
        return self.assets[asset_type.name].get(idt)

    def delete(self, asset_type: AssetType, idt: int):
        del self.assets[asset_type.name][idt]

    def get_all(self, asset_type: AssetType):
        return self.assets[asset_type.name]
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
            (creature_id, color, kind) = [int(j) for j in self.get_init_input().split()]
            self.game_assets.create(asset_type=AssetType.CREATURE, idt=creature_id, attr_kwargs={'color': color, 'kind': kind, 'visible': False})
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
        scan_idt = hash((owner, creature_idt))
        self.game_assets.update(asset_type=AssetType.SCAN, idt=scan_idt, attr_kwargs={'owner': owner, 'creature_idt': creature_idt, 'saved': True})
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
                (drone_id, drone_x, drone_y, emergency, battery) = [int(j) for j in self.get_turn_input().split()]
                self.game_assets.update(asset_type=AssetType.MYDRONE, idt=drone_id, attr_kwargs={'x': drone_x, 'y': drone_y, 'emergency': emergency, 'battery': battery})
            foe_drone_count = int(self.get_turn_input())
            for i in range(foe_drone_count):
                (drone_id, drone_x, drone_y, emergency, battery) = [int(j) for j in self.get_turn_input().split()]
                self.game_assets.update(asset_type=AssetType.FOEDRONE, idt=drone_id, attr_kwargs={'x': drone_x, 'y': drone_y, 'emergency': emergency, 'battery': battery})
            drone_scan_count = int(self.get_turn_input())
            for i in range(drone_scan_count):
                (drone_id, creature_id) = [int(j) for j in self.get_turn_input().split()]
                drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_id)
                if drone is None:
                    drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_id)
                scan_idt = hash((drone.owner, creature_id))
                self.game_assets.update(asset_type=AssetType.SCAN, idt=scan_idt, attr_kwargs={'owner': drone.owner, 'creature_idt': creature_id, 'drone_idt': drone_id})
                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_id)
                creature.scans_idt.add(scan_idt)
            visible_creature_count = int(self.get_turn_input())
            unvisible_creatures = self.creatures_idt.copy()
            for i in range(visible_creature_count):
                (creature_id, creature_x, creature_y, creature_vx, creature_vy) = [int(j) for j in self.get_turn_input().split()]
                unvisible_creatures.remove(creature_id)
                self.game_assets.update(asset_type=AssetType.CREATURE, idt=creature_id, attr_kwargs={'x': creature_x, 'y': creature_y, 'vx': creature_vx, 'vy': creature_vy, 'visible': True})
            for creature_id in unvisible_creatures:
                self.game_assets.update(asset_type=AssetType.CREATURE, idt=creature_id, attr_kwargs={'visible': False})
            radar_blip_count = int(self.get_turn_input())
            for i in range(radar_blip_count):
                inputs = self.get_turn_input().split()
                drone_id = int(inputs[0])
                creature_id = int(inputs[1])
                radar = inputs[2]
            if GameLoop.LOG:
                self.print_turn_logs()
            my_drones = self.game_assets.get_all(AssetType.MYDRONE)
            creatures = self.game_assets.get_all(AssetType.CREATURE)
            drones_targets = {}
            for (drone_id, drone) in my_drones.items():
                (drone_target, d_min) = (None, D_MAX)
                for (creature_id, creature) in creatures.items():
                    creature_scanned_by = [self.game_assets.get(AssetType.SCAN, scan_idt).owner for scan_idt in creature.scans_idt]
                    if creature.visible and MY_OWNER not in creature_scanned_by:
                        drone_to_creature_vector = creature.position - drone.position
                        drone_to_creature_distance = self.hash_map_norms[drone_to_creature_vector]
                        if drone_to_creature_distance <= d_min:
                            d_min = drone_to_creature_distance
                            drone_target = creature
                drones_targets[drone_id] = drone_target
            for (drone_id, drone) in my_drones.items():
                drone_target = drones_targets[drone_id]
                if drone_target is None:
                    print(f'WAIT 1')
                else:
                    print(f'MOVE {drone_target.x} {drone_target.y} 0 {drone_target.idt}')
GameLoop().start()