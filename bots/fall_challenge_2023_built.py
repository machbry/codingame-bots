import sys
import numpy as np
import math
from enum import Enum
from dataclasses import field, dataclass
from typing import Literal, List, Set, Union, Dict, Any

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
OWNERS = [MY_OWNER, FOE_OWNER]
X_MIN = 0
Y_MIN = 0
X_MAX = 10000
Y_MAX = 10000
D_MAX = HASH_MAP_NORMS[Vector(X_MAX, Y_MAX)]
MAP_CENTER = Point(X_MAX / 2, Y_MAX / 2)
CORNERS = {'TL': Point(X_MIN, Y_MIN), 'TR': Point(X_MAX, Y_MIN), 'BR': Point(X_MAX, Y_MAX), 'BL': Point(X_MIN, Y_MAX)}

class Kind(Enum):
    MONSTER = -1
    ZERO = 0
    ONE = 1
    TWO = 2
SCORE_BY_KIND = {Kind.MONSTER.value: 0, Kind.ZERO.value: 1, Kind.ONE.value: 2, Kind.TWO.value: 3}
SCORE_FOR_FULL_COLOR = 3
SCORE_FOR_FULL_KIND = 4
SCORE_MULTIPLIER_FIRST = 2
CREATURE_HABITATS_PER_KIND = {Kind.MONSTER.value: [X_MIN, 2500, X_MAX, 10000], Kind.ZERO.value: [X_MIN, 2500, X_MAX, 5000], Kind.ONE.value: [X_MIN, 5000, X_MAX, 7500], Kind.TWO.value: [X_MIN, 2500, X_MAX, 5000]}
LIGHT_RADIUS = HASH_MAP_NORMS[Vector(0, 800)]
AUGMENTED_LIGHT_RADIUS = HASH_MAP_NORMS[Vector(0, 2000)]
EMERGENCY_RADIUS = HASH_MAP_NORMS[Vector(0, 500)]
DRONE_SPEED = HASH_MAP_NORMS[Vector(0, 600)]
AGGRESSIVE_MONSTER_SPEED = HASH_MAP_NORMS[Vector(0, 540)]
NON_AGGRESSIVE_MONSTER_SPEED = HASH_MAP_NORMS[Vector(0, 270)]
SAFE_RADIUS_FROM_MONSTERS = HASH_MAP_NORMS[Vector(0, 500 + 540)]
FLEE_RADIUS_FROM_MONSTERS = HASH_MAP_NORMS[Vector(0, 500 + 540 + 600)]

@dataclass(slots=True)
class Asset:
    idt: int

@dataclass(slots=True)
class Unit(Asset):
    x: int = None
    y: int = None
    vx: int = None
    vy: int = None
    next_x: int = None
    next_y: int = None

    @property
    def position(self):
        return Point(self.x, self.y)

    @property
    def speed(self):
        return Vector(self.vx, self.vy)

    @property
    def next_position(self):
        return Point(self.next_x, self.next_y)

@dataclass(slots=True)
class Creature(Unit):
    color: int = None
    kind: int = None
    habitat: List[int] = None
    visible: bool = False
    escaped: bool = False
    scanned_by_drones: Set[int] = field(default_factory=set)
    saved_by_owners: List[int] = field(default_factory=list)
    eval_saved_by_owners: List[int] = field(default_factory=list)
    extra_scores: Dict[int, int] = field(default_factory=dict)
    last_turn_visible: int = None

@dataclass(slots=True)
class Drone(Unit):
    emergency: int = None
    battery: int = None
    unsaved_creatures_idt: Set[int] = field(default_factory=set)
    extra_score_with_unsaved_creatures: int = 0
    has_to_flee_from: List[Creature] = field(default_factory=list)

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
    zones: List[List[int]] = field(default_factory=list)

@dataclass(slots=True)
class Scans(Asset):
    owner: int = None
    saved_creatures: np.ndarray = None

@dataclass
class Action:
    move: bool = True
    target: Union[Point, Unit] = MAP_CENTER
    light: bool = False
    comment: Union[int, str] = None

    def __repr__(self):
        instruction = f'MOVE {int(self.target.x)} {int(self.target.y)}' if self.move else 'WAIT'
        instruction = f'{instruction} {(1 if self.light else 0)}'
        if self.comment:
            instruction = f'{instruction} {self.comment}'
        return instruction

class AssetType(Enum):
    CREATURE = Creature
    MYDRONE = MyDrone
    FOEDRONE = FoeDrone
    RADARBLIP = RadarBlip
    SCANS = Scans

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

    def get(self, asset_type: AssetType, idt: int) -> Union[Creature, MyDrone, FoeDrone, RadarBlip, Scans]:
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

def order_assets(drones: List[Asset], on_attr: str, ascending: bool=True):
    return sorted(drones, key=lambda drone: getattr(drone, on_attr), reverse=not ascending)

def evaluate_extra_score_for_owner_creature(creature_kind: int, creature_escaped: bool, creature_saved_by_owners: List[int], owner: int):
    if creature_kind == -1:
        return 0
    if creature_escaped:
        return 0
    if owner in creature_saved_by_owners:
        return 0
    if len(creature_saved_by_owners) > 0:
        return SCORE_BY_KIND[creature_kind]
    else:
        return SCORE_MULTIPLIER_FIRST * SCORE_BY_KIND[creature_kind]
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
        self.monsters = []
        self.my_drones_scan_count = 0
        self.my_scan_count = 0
        self.drones_scan_count = {}
        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]
            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind
            creature.habitat = CREATURE_HABITATS_PER_KIND[kind]
            if creature.kind == -1:
                self.monsters.append(creature)
            for owner in OWNERS:
                scan = self.game_assets.new_asset(asset_type=AssetType.SCANS, idt=owner)
                scan.owner = owner
                scan.saved_creatures = np.zeros(shape=(4, 3))
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
        scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=owner)
        creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
        creature_saved = scans.saved_creatures[creature.color, creature.kind]
        if creature_saved == 1:
            return
        scans.saved_creatures[creature.color, creature.kind] = 1
        creature.saved_by_owners.append(owner)

    def update_drone(self, drone_idt, drone_x, drone_y, emergency, battery, asset_type: Union[AssetType.MYDRONE, AssetType.FOEDRONE]):
        drone = self.game_assets.get(asset_type=asset_type, idt=drone_idt)
        if drone is None:
            drone = self.game_assets.new_asset(asset_type=asset_type, idt=drone_idt)
        drone.x = drone_x
        drone.y = drone_y
        drone.emergency = emergency
        drone.battery = battery
        if drone.emergency == 1:
            drone.unsaved_creatures_idt = set()
        self.drones_scan_count[drone_idt] = 0

    def update(self):
        self.nb_turns += 1
        my_score = int(self.get_turn_input())
        foe_score = int(self.get_turn_input())
        self.my_scan_count = int(self.get_turn_input())
        for i in range(self.my_scan_count):
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
        self.my_drones_scan_count = 0
        for i in range(drone_scan_count):
            drone_idt, creature_idt = [int(j) for j in self.get_turn_input().split()]
            drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_idt)
            else:
                self.my_drones_scan_count += 1
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
            drone.unsaved_creatures_idt.add(creature_idt)
            creature.scanned_by_drones.add(drone_idt)
            self.drones_scan_count[drone_idt] += 1
        visible_creature_count = int(self.get_turn_input())
        for i in range(visible_creature_count):
            creature_idt, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in self.get_turn_input().split()]
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.x = creature_x
            creature.y = creature_y
            creature.vx = creature_vx
            creature.vy = creature_vy
            creature.visible = True
            creature.last_turn_visible = self.nb_turns
            creature_next_position = creature.position + creature.speed
            creature.next_x = creature_next_position.x
            creature.next_y = creature_next_position.y
        radar_blip_count = int(self.get_turn_input())
        self.my_drones_radar_count = {drone_idt: {radar: 0 for radar in CORNERS.keys()} for drone_idt in self.game_assets.get_all(AssetType.MYDRONE).keys()}
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
            drone = self.game_assets.get(asset_type=AssetType.MYDRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.get(asset_type=AssetType.FOEDRONE, idt=drone_idt)
            zone_corner = CORNERS[radar]
            drone_x, drone_y = (drone.x, drone.y)
            zone_corner_x, zone_corner_y = (zone_corner.x, zone_corner.y)
            zone_x_min = min(drone_x, zone_corner_x)
            zone_y_min = min(drone_y, zone_corner_y)
            zone_x_max = max(drone_x, zone_corner_x)
            zone_y_max = max(drone_y, zone_corner_y)
            radar_blip.zones.append([zone_x_min, zone_y_min, zone_x_max, zone_y_max])
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.escaped = False
            if drone_idt not in creature.scanned_by_drones:
                self.my_drones_radar_count[drone_idt][radar] += 1
        if GameLoop.LOG:
            self.print_turn_logs()

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def start(self):
        while GameLoop.RUNNING:
            for creature in self.game_assets.get_all(asset_type=AssetType.CREATURE).values():
                creature.scanned_by_drones = set()
                creature.visible = False
                creature.escaped = True
            self.drones_scan_count = {}
            self.update()
            my_drones = self.game_assets.get_all(AssetType.MYDRONE)
            foe_drones = self.game_assets.get_all(AssetType.FOEDRONE)
            creatures = self.game_assets.get_all(AssetType.CREATURE)
            all_drones = [*my_drones.values(), *foe_drones.values()]
            ordered_drones_from_top_to_bottom = order_assets(all_drones, 'y')
            for creature in creatures.values():
                creature.eval_saved_by_owners = creature.saved_by_owners.copy()
                creature.extra_scores = {owner: 0 for owner in OWNERS}
            for drone in ordered_drones_from_top_to_bottom:
                drone.extra_score_with_unsaved_creatures = 0
                owner = drone.owner
                for creature_idt in drone.unsaved_creatures_idt:
                    creature = self.game_assets.get(AssetType.CREATURE, creature_idt)
                    extra_score = evaluate_extra_score_for_owner_creature(creature_kind=creature.kind, creature_escaped=creature.escaped, creature_saved_by_owners=creature.eval_saved_by_owners, owner=owner)
                    drone.extra_score_with_unsaved_creatures += extra_score
                    creature.eval_saved_by_owners.append(owner)
            for creature in creatures.values():
                for owner in OWNERS:
                    extra_score = evaluate_extra_score_for_owner_creature(creature_kind=creature.kind, creature_escaped=creature.escaped, creature_saved_by_owners=creature.eval_saved_by_owners, owner=owner)
                    creature.extra_scores[owner] += extra_score
            for creature_idt, creature in creatures.items():
                if not creature.visible:
                    possible_zones = [creature.habitat]
                    for drone_idt, drone in my_drones.items():
                        radar_idt = hash((drone_idt, creature_idt))
                        radar_blip = self.game_assets.get(asset_type=AssetType.RADARBLIP, idt=radar_idt)
                        if radar_blip is not None:
                            possible_zones.append(radar_blip.zones[-1])
                    intersection = np.array(possible_zones)
                    creature.next_x = (np.max(intersection[:, 0]) + np.min(intersection[:, 2])) / 2
                    creature.next_y = (np.max(intersection[:, 1]) + np.min(intersection[:, 3])) / 2
                else:
                    creature.next_x = creature.x + creature.vx
                    creature.next_y = creature.y + creature.vy
            my_drones_to_flee_from_monsters = {}
            for my_drone in my_drones.values():
                my_drone.has_to_flee_from = []
                for monster in self.monsters:
                    if monster.x:
                        if HASH_MAP_NORMS[monster.position - my_drone.position] <= FLEE_RADIUS_FROM_MONSTERS:
                            my_drone.has_to_flee_from.append(monster)
            drones_targets = {}
            for drone_idt, drone in my_drones.items():
                eligible_targets, drone_target, d_min = ({}, None, D_MAX)
                for creature_idt, creature in creatures.items():
                    if drone_idt not in creature.scanned_by_drones and creature.kind != -1 and (not creature.escaped):
                        eligible_targets[creature_idt] = creature
                drones_targets[drone_idt] = get_closest_unit_from(drone, eligible_targets)
            for drone_idt, drone in my_drones.items():
                drone_has_to_flee_from = drone.has_to_flee_from
                if len(drone_has_to_flee_from) == 1:
                    vector_to_creature = drone_has_to_flee_from[0].position - drone.position
                    distance_to_creature = HASH_MAP_NORMS[vector_to_creature]
                    if distance_to_creature > SAFE_RADIUS_FROM_MONSTERS:
                        v = 1 / distance_to_creature ** (1 / 2) * vector_to_creature
                        flee_vectors = [Vector(v.y, -v.x), Vector(-v.y, v.x)]
                        flee_vector = flee_vectors[0]
                        vector_to_center = MAP_CENTER - drone.position
                        cos_with_center = flee_vector.dot(vector_to_center)
                        if flee_vectors[1].dot(vector_to_center) > cos_with_center:
                            flee_vector = flee_vectors[1]
                        action = Action(target=drone.position + DRONE_SPEED ** (1 / 2) * flee_vector, comment='FLEE')
                    else:
                        flee_vector = -1 * vector_to_creature
                        action = Action(target=drone.position + DRONE_SPEED ** (1 / 2) / distance_to_creature ** (1 / 2) * flee_vector, comment='FLEE')
                elif len(drone_has_to_flee_from) > 1:
                    flee_vector = Vector(0, 0)
                    for creature in drone_has_to_flee_from:
                        flee_vector += drone.position - creature.position
                    action = Action(target=drone.position + DRONE_SPEED ** (1 / 2) / flee_vector.norm * flee_vector, comment='FLEE')
                elif self.drones_scan_count[drone_idt] >= 4 or self.my_scan_count + self.my_drones_scan_count >= 12:
                    action = Action(target=Point(drone.x, 499), comment='SAVE')
                else:
                    drone_target = drones_targets[drone_idt]
                    if drone_target is None:
                        max_radar_count = 0
                        radar_chosen = None
                        for radar, radar_count in self.my_drones_radar_count[drone_idt].items():
                            if radar_count >= max_radar_count:
                                radar_chosen = radar
                                max_radar_count = radar_count
                        drone_target = CORNERS[radar_chosen]
                    action = Action(target=drone_target, light=True, comment='EXPLORE')
                print(action)
GameLoop().start()