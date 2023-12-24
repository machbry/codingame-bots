import math
import sys
from enum import Enum
from dataclasses import field, dataclass
from typing import Set, Any, Literal, Dict, Union, List

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
MAP_CENTER = Point(X_MAX / 2, Y_MAX / 2)
CORNERS = {'TL': Point(X_MIN, Y_MIN + 2500), 'TR': Point(X_MAX, Y_MIN + 2500), 'BR': Point(X_MAX, Y_MAX), 'BL': Point(X_MIN, Y_MAX)}
SCORE_BY_TYPE = {0: 1, 1: 2, 2: 3}
SCORE_FOR_FULL_COLOR = 3
SCORE_FOR_FULL_TYPE = 4
SCORE_MULTIPLIER_FIRST = 2

@dataclass(slots=True)
class Asset:
    idt: int

@dataclass(slots=True)
class Scores:
    me: int = 0
    foe: int = 0

@dataclass(slots=True)
class Scan(Asset):
    owner: int = None
    creature_idt: int = None
    drone_idt: int = None
    saved: bool = False

@dataclass(slots=True)
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

@dataclass(slots=True)
class Creature(Unit):
    color: int = None
    kind: int = None
    visible: bool = False
    escaped: bool = False
    scans_idt: Set[int] = field(default_factory=set)
    scanned_by: Set[int] = field(default_factory=set)
    my_extra_score: int = 0
    foe_extra_score: int = 0

@dataclass(slots=True)
class Drone(Unit):
    emergency: int = None
    battery: int = None
    my_extra_score: int = 0
    foe_extra_score: int = 0

@dataclass(slots=True)
class MyDrone(Drone):
    owner: int = MY_OWNER

@dataclass(slots=True)
class FoeDrone(Drone):
    owner: int = FOE_OWNER

@dataclass(slots=True)
class RadarBlip(Asset):
    drone_idt: int = None
    creature_idt: int = None
    radar: str = None

@dataclass
class Action:
    move: bool = True
    target: Union[Point, Unit] = MAP_CENTER
    light: bool = False
    comment: Union[int, str] = None

    def __repr__(self):
        instruction = f'MOVE {self.target.x} {self.target.y}' if self.move else 'WAIT'
        instruction = f'{instruction} {(1 if self.light else 0)}'
        if self.comment:
            instruction = f'{instruction} {self.comment}'
        return instruction

class AssetType(Enum):
    SCORES = Scores
    SCAN = Scan
    CREATURE = Creature
    MYDRONE = MyDrone
    FOEDRONE = FoeDrone
    RADARBLIP = RadarBlip

class Singleton(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance

class GameAssets(Singleton):

    def __init__(self):
        self.assets: Dict[str, Dict[int, Any]] = {asset_type.name: {} for asset_type in AssetType.__iter__()}

    def new_asset(self, asset_type: AssetType, idt: int):
        asset = asset_type.value(idt=idt)
        self.assets[asset_type.name][idt] = asset
        return asset

    def get(self, asset_type: AssetType, idt: int) -> Union[Creature, MyDrone, FoeDrone, Scan, RadarBlip]:
        return self.assets[asset_type.name].get(idt)

    def delete(self, asset_type: AssetType, idt: int):
        del self.assets[asset_type.name][idt]

    def get_all(self, asset_type: AssetType):
        return self.assets[asset_type.name]

def get_closest_unit_from(unit: Unit, other_units: Dict[int, Unit]):
    d_min = D_MAX
    closest_unit = None
    for other_unit_idt, other_unit in other_units.items():
        if unit.idt != other_unit.idt:
            try:
                unit_to_other_unit_vector = other_unit.position - unit.position
            except (AttributeError, TypeError):
                continue
            unit_to_other_unit_distance = HASH_MAP_NORMS[unit_to_other_unit_vector]
            if unit_to_other_unit_distance < d_min:
                d_min = unit_to_other_unit_distance
                closest_unit = other_unit
    return closest_unit

def order_drones_from_top_to_bottom(drones: List[Drone]) -> List[Drone]:
    return sorted(drones, key=lambda drone: drone.y)

def evaluate_extra_scores_for_creature(creature: Creature, current_scores: Scores, game_assets=GameAssets()) -> Scores:
    creature_kind = creature.kind
    if creature.kind == -1:
        return Scores(0, 0)
    if creature.escaped:
        return Scores(0, 0)
    creature_scanned_by = creature.scanned_by
    scanned_by_me = MY_OWNER in creature_scanned_by
    scanned_by_foe = FOE_OWNER in creature_scanned_by
    if scanned_by_me:
        if scanned_by_foe:
            return Scores(0, 0)
        my_extra_score = 0
        ordered_drones = order_drones_from_top_to_bottom(game_assets.get_all(asset_type=AssetType.FOEDRONE).values())
        foe_extra_score = SCORE_BY_TYPE[creature_kind]
    elif scanned_by_foe:
        foe_extra_score = 0
        ordered_drones = order_drones_from_top_to_bottom(game_assets.get_all(asset_type=AssetType.MYDRONE).values())
        my_extra_score = SCORE_BY_TYPE[creature_kind]
    else:
        all_drones = [*game_assets.get_all(asset_type=AssetType.FOEDRONE).values(), *game_assets.get_all(asset_type=AssetType.MYDRONE).values()]
        ordered_drones = order_drones_from_top_to_bottom(all_drones)
        my_extra_score = foe_extra_score = SCORE_BY_TYPE[creature_kind]
    return Scores(my_extra_score, foe_extra_score)
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
        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]
            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind
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
            self.current_scores = Scores(me=my_score, foe=foe_score)
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
                creature.scanned_by.add(scan.owner)
            for creature in self.game_assets.get_all(asset_type=AssetType.CREATURE).values():
                creature.visible = False
                creature.escaped = True
            visible_creature_count = int(self.get_turn_input())
            for i in range(visible_creature_count):
                creature_idt, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in self.get_turn_input().split()]
                creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
                creature.x = creature_x
                creature.y = creature_y
                creature.vx = creature_vx
                creature.vy = creature_vy
                creature.visible = True
            radar_blip_count = int(self.get_turn_input())
            my_drones_radar_count = {drone_idt: {radar: 0 for radar in CORNERS.keys()} for drone_idt in self.game_assets.get_all(AssetType.MYDRONE).keys()}
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
                    if MY_OWNER not in creature.scanned_by:
                        my_drones_radar_count[drone_idt][radar] += 1
            if GameLoop.LOG:
                self.print_turn_logs()
            my_drones = self.game_assets.get_all(AssetType.MYDRONE)
            creatures = self.game_assets.get_all(AssetType.CREATURE)
            for creature_idt, creature in creatures.items():
                extra_scores = evaluate_extra_scores_for_creature(creature, self.current_scores, self.game_assets)
                creature.my_extra_score = extra_scores.me
                creature.foe_extra_score = extra_scores.foe
            drones_targets = {}
            for drone_idt, drone in my_drones.items():
                eligible_targets, drone_target, d_min = ({}, None, D_MAX)
                for creature_idt, creature in creatures.items():
                    if MY_OWNER not in creature.scanned_by and creature.kind != -1 and (not creature.escaped):
                        eligible_targets[creature_idt] = creature
                drones_targets[drone_idt] = get_closest_unit_from(drone, eligible_targets)
            for drone_idt, drone in my_drones.items():
                if drones_scan_count[drone_idt] >= 4 or my_scan_count + my_drones_scan_count >= 12:
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
GameLoop().start()