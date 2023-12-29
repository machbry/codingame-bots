import math
import numpy as np
import sys
from enum import Enum
from dataclasses import field, dataclass
from typing import Union, Any, Literal, Tuple, Dict, List, Set

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

class Color(Enum):
    ROSE = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3
KINDS = np.array([[Kind.ZERO.value, Kind.ONE.value, Kind.TWO.value]])
COLORS = np.array([[Color.ROSE.value], [Color.YELLOW.value], [Color.GREEN.value], [Color.BLUE.value]])
EMPTY_ARRAY_CREATURES = np.zeros(shape=(len(Color), len(Kind) - 1))
SCORE_BY_KIND = np.array([[1], [2], [3]])
SCORE_FOR_FULL_COLOR = 3
SCORE_FOR_FULL_KIND = 4
ACTIVATE_COLORS = np.array([[1], [1], [1]])
ACTIVATE_KINDS = np.array([[1, 1, 1, 1]])
CREATURE_HABITATS_PER_KIND = {Kind.MONSTER.value: [X_MIN, 2500, X_MAX, 10000], Kind.ZERO.value: [X_MIN, 2500, X_MAX, 5000], Kind.ONE.value: [X_MIN, 5000, X_MAX, 7500], Kind.TWO.value: [X_MIN, 7500, X_MAX, 10000]}
MAX_SPEED_PER_KIND = {Kind.MONSTER.value: 540, Kind.ZERO.value: 400, Kind.ONE.value: 400, Kind.TWO.value: 400}
LIGHT_RADIUS = HASH_MAP_NORMS[Vector(0, 800)]
AUGMENTED_LIGHT_RADIUS = HASH_MAP_NORMS[Vector(0, 2000)]
EMERGENCY_RADIUS = HASH_MAP_NORMS[Vector(0, 500)]
DRONE_SPEED = HASH_MAP_NORMS[Vector(0, 600)]
AGGRESSIVE_MONSTER_SPEED = HASH_MAP_NORMS[Vector(0, 540)]
NON_AGGRESSIVE_MONSTER_SPEED = HASH_MAP_NORMS[Vector(0, 270)]
SAFE_RADIUS_FROM_MONSTERS = HASH_MAP_NORMS[Vector(0, 500 + 540)]
FLEE_RADIUS_FROM_MONSTERS = HASH_MAP_NORMS[Vector(0, 500 + 270 + 600)]
MAX_NUMBER_OF_RADAR_BLIPS_USED = 3

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

    def log(self):
        return f'{self.idt}'

@dataclass(slots=True)
class Creature(Unit):
    color: int = None
    kind: int = None
    habitat: List[int] = None
    visible: bool = False
    escaped: bool = False
    extra_scores: Dict[int, int] = field(default_factory=dict)
    last_turn_visible: int = None

    @property
    def my_extra_score(self):
        return self.extra_scores[MY_OWNER]

    @property
    def foe_extra_score(self):
        return self.extra_scores[FOE_OWNER]

@dataclass(slots=True)
class Drone(Unit):
    emergency: int = None
    battery: int = None
    unsaved_creatures_idt: Set[int] = field(default_factory=set)
    eval_unsaved_creatures_idt: Set[int] = field(default_factory=set)
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

    def copy(self):
        return Scans(idt=self.idt, owner=self.owner, saved_creatures=self.saved_creatures.copy())

@dataclass(slots=True)
class Trophies(Asset):
    creatures_win_by: np.ndarray = None
    colors_win_by: np.ndarray = None
    kinds_win_by: np.ndarray = None

    def copy(self):
        return Trophies(idt=self.idt, creatures_win_by=self.creatures_win_by.copy(), colors_win_by=self.colors_win_by.copy(), kinds_win_by=self.kinds_win_by.copy())

@dataclass(slots=True)
class Score:
    base_creatures: int = 0
    bonus_creatures: int = 0
    base_colors: int = 0
    bonus_colors: int = 0
    base_kinds: int = 0
    bonus_kinds: int = 0

    @property
    def base(self):
        return self.base_creatures + self.base_colors + self.base_kinds

    @property
    def bonus(self):
        return self.bonus_creatures + self.bonus_colors + self.bonus_kinds

    @property
    def creatures(self):
        return self.base_creatures + self.bonus_creatures

    @property
    def colors(self):
        return self.base_colors + self.bonus_colors

    @property
    def kinds(self):
        return self.base_kinds + self.bonus_kinds

    @property
    def total(self):
        return self.base + self.bonus

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

def order_assets(assets: List[Asset], on_attr: str, ascending: bool=True):
    return sorted(assets, key=lambda asset: getattr(asset, on_attr), reverse=not ascending)

def use_light_to_find_a_target(drone: Drone, target: Creature, hash_map_norms=HASH_MAP_NORMS, augmented_light_radius=AUGMENTED_LIGHT_RADIUS):
    battery = drone.battery
    if battery >= 10 and drone.y > 4000:
        return True
    if drone.battery >= 5:
        distance_to_target = hash_map_norms[target.position - drone.position]
        if distance_to_target <= augmented_light_radius and (not target.visible):
            return True
    return False

class AssetType(Enum):
    CREATURE = Creature
    MY_DRONE = MyDrone
    FOE_DRONE = FoeDrone
    RADAR_BLIP = RadarBlip
    SCANS = Scans
    TROPHIES = Trophies

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

    def get(self, asset_type: AssetType, idt: int) -> Union[Creature, MyDrone, FoeDrone, RadarBlip, Scans, Trophies]:
        return self.assets[asset_type.name].get(idt)

    def delete(self, asset_type: AssetType, idt: int):
        del self.assets[asset_type.name][idt]

    def get_all(self, asset_type: AssetType):
        return self.assets[asset_type.name]

def update_saved_scans(saved_creatures: np.ndarray, creature_color: int, creature_kind: int):
    creature_saved = saved_creatures[creature_color, creature_kind]
    if creature_saved == 1:
        return False
    saved_creatures[creature_color, creature_kind] = 1
    return True

def update_trophies(owner: int, saved_creatures: np.ndarray, newly_saved_creatures: np.ndarray, creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray, activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS, score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):
    newly_completed_creatures = newly_saved_creatures == owner
    creatures_trophies_available = creatures_win_by == 0
    creatures_win_by[newly_completed_creatures & creatures_trophies_available] = owner
    completed_colors = saved_creatures.dot(activate_colors) == score_for_full_color
    colors_trophies_available = colors_win_by == 0
    colors_win_by[completed_colors & colors_trophies_available] = owner
    completed_kinds = activate_kinds.dot(saved_creatures) == score_for_full_kind
    kinds_trophies_available = kinds_win_by == 0
    kinds_win_by[completed_kinds & kinds_trophies_available] = owner

def compute_score(owner: int, saved_creatures: np.ndarray, creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray, score_by_kind=SCORE_BY_KIND, activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS, score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):
    score = Score()
    creatures_activated = saved_creatures.dot(score_by_kind)
    bonus_saved_creatures = np.zeros_like(saved_creatures)
    bonus_saved_creatures[creatures_win_by == owner] = 1
    bonus_creatures_activated = bonus_saved_creatures.dot(score_by_kind)
    colors_activated = saved_creatures.dot(activate_colors)
    completed_colors = colors_activated == score_for_full_color
    owned_colors_trophies = colors_win_by == owner
    kinds_activated = activate_kinds.dot(saved_creatures)
    completed_kinds = kinds_activated == score_for_full_kind
    owned_kinds_trophies = kinds_win_by == owner
    score.base_creatures = creatures_activated.sum()
    score.bonus_creatures = bonus_creatures_activated.sum()
    score.base_colors = colors_activated[completed_colors].sum()
    score.bonus_colors = score_for_full_color * colors_win_by[owned_colors_trophies].size
    score.base_kinds = kinds_activated[completed_kinds].sum()
    score.bonus_kinds = score_for_full_kind * kinds_win_by[owned_kinds_trophies].size
    return score

class ScoreSimulation:
    __slots__ = ('simulation_scenario', 'owners_saved_creatures', 'creatures_win_by', 'colors_win_by', 'kinds_win_by', 'empty_array_creatures', 'newly_saved_creatures', 'owners_in_scenario', 'simulation_done')

    def __init__(self, simulation_scenario: List[Tuple[int, List[Creature]]], owners_saved_creatures: Dict[int, np.ndarray], creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray):
        self.simulation_scenario = simulation_scenario
        self.owners_saved_creatures = {owner: saved_creatures.copy() for owner, saved_creatures in owners_saved_creatures.items()}
        self.creatures_win_by = creatures_win_by.copy()
        self.colors_win_by = colors_win_by.copy()
        self.kinds_win_by = kinds_win_by.copy()
        self.empty_array_creatures = EMPTY_ARRAY_CREATURES
        self.newly_saved_creatures = None
        self.owners_in_scenario = set()
        self.simulation_done = False

    def do_simulation(self):
        for owner, creatures_to_save in self.simulation_scenario:
            self.owners_in_scenario.add(owner)
            self.newly_saved_creatures = np.zeros_like(EMPTY_ARRAY_CREATURES)
            for creature in creatures_to_save:
                if update_saved_scans(self.owners_saved_creatures[owner], creature.color, creature.kind):
                    self.newly_saved_creatures[creature.color, creature.kind] = owner
            update_trophies(owner=owner, saved_creatures=self.owners_saved_creatures[owner], newly_saved_creatures=self.newly_saved_creatures, creatures_win_by=self.creatures_win_by, colors_win_by=self.colors_win_by, kinds_win_by=self.kinds_win_by)
        self.simulation_done = True

    def compute_new_score(self):
        if not self.simulation_done:
            self.do_simulation()
        new_score_per_owner = {owner: compute_score(owner=owner, saved_creatures=self.owners_saved_creatures[owner], creatures_win_by=self.creatures_win_by, colors_win_by=self.colors_win_by, kinds_win_by=self.kinds_win_by) for owner in self.owners_in_scenario}
        return new_score_per_owner

    def scans_and_trophies_after_simulation(self):
        if not self.simulation_done:
            self.do_simulation()
        return {'owners_saved_creatures': self.owners_saved_creatures, 'creatures_win_by': self.creatures_win_by, 'colors_win_by': self.colors_win_by, 'kinds_win_by': self.kinds_win_by}
GAME_ASSETS = GameAssets()

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'game_assets', 'hash_map_norms', 'empty_array_saved_creatures', 'max_number_of_radar_blips_used', 'max_speed_per_kind', 'corners', 'my_owner', 'foe_owner', 'owners', 'flee_radius_from_monsters', 'safe_radius_from_monsters', 'map_center', 'drone_speed', 'owners_scores', 'owners_extra_score_with_all_unsaved_creatures', 'owners_max_possible_score', 'my_drones_idt_play_order', 'newly_saved_creatures', 'monsters')
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.game_assets = GAME_ASSETS
        self.hash_map_norms = HASH_MAP_NORMS
        self.empty_array_saved_creatures = EMPTY_ARRAY_CREATURES
        self.max_number_of_radar_blips_used = MAX_NUMBER_OF_RADAR_BLIPS_USED
        self.max_speed_per_kind = MAX_SPEED_PER_KIND
        self.corners = CORNERS
        self.my_owner = MY_OWNER
        self.foe_owner = FOE_OWNER
        self.owners = OWNERS
        self.flee_radius_from_monsters = FLEE_RADIUS_FROM_MONSTERS
        self.safe_radius_from_monsters = SAFE_RADIUS_FROM_MONSTERS
        self.map_center = MAP_CENTER
        self.drone_speed = DRONE_SPEED
        self.owners_scores = {}
        self.owners_extra_score_with_all_unsaved_creatures = {}
        self.owners_max_possible_score = {}
        self.my_drones_idt_play_order = []
        self.newly_saved_creatures = np.zeros_like(self.empty_array_saved_creatures)
        self.monsters = []
        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]
            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind
            creature.habitat = CREATURE_HABITATS_PER_KIND[kind]
            if creature.kind == -1:
                self.monsters.append(creature)
            for owner in self.owners:
                scans = self.game_assets.new_asset(asset_type=AssetType.SCANS, idt=owner)
                scans.owner = owner
                scans.saved_creatures = np.zeros_like(self.empty_array_saved_creatures)
        trophies = self.game_assets.new_asset(asset_type=AssetType.TROPHIES, idt=42)
        trophies.creatures_win_by = np.zeros_like(self.empty_array_saved_creatures)
        trophies.colors_win_by = np.zeros_like(COLORS)
        trophies.kinds_win_by = np.zeros_like(KINDS)
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

    def update_drone(self, drone_idt, drone_x, drone_y, emergency, battery, asset_type: Union[AssetType.MY_DRONE, AssetType.FOE_DRONE]):
        drone = self.game_assets.get(asset_type=asset_type, idt=drone_idt)
        if drone is None:
            drone = self.game_assets.new_asset(asset_type=asset_type, idt=drone_idt)
        drone.x = drone_x
        drone.y = drone_y
        drone.emergency = emergency
        drone.battery = battery
        drone.unsaved_creatures_idt = set()

    def update_visible_creature(self, creature_idt, creature_x, creature_y, creature_vx, creature_vy):
        creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
        creature.x = creature_x
        creature.y = creature_y
        creature.vx = creature_vx
        creature.vy = creature_vy
        creature.visible = True
        creature.last_turn_visible = self.nb_turns

    def update_radar_blip(self, drone_idt, creature_idt, radar):
        radar_idt = hash((drone_idt, creature_idt))
        radar_blip = self.game_assets.get(asset_type=AssetType.RADAR_BLIP, idt=radar_idt)
        if radar_blip is None:
            radar_blip = self.game_assets.new_asset(asset_type=AssetType.RADAR_BLIP, idt=radar_idt)
            radar_blip.drone_idt = drone_idt
            radar_blip.creature_idt = creature_idt
        creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=creature_idt)
        creature.escaped = False
        radar_blip_zones = radar_blip.zones
        n = min(len(radar_blip_zones), self.max_number_of_radar_blips_used - 1)
        for i in range(0, n):
            zone = radar_blip.zones[-i - 1]
            creature_max_speed = self.max_speed_per_kind[creature.kind]
            radar_blip.zones[-i - 1] = [zone[0] - creature_max_speed, zone[1] - creature_max_speed, zone[2] + creature_max_speed, zone[3] + creature_max_speed]
        drone = self.game_assets.get(asset_type=AssetType.MY_DRONE, idt=drone_idt)
        if drone is None:
            drone = self.game_assets.get(asset_type=AssetType.FOE_DRONE, idt=drone_idt)
        zone_corner = self.corners[radar]
        drone_x, drone_y = (drone.x, drone.y)
        zone_corner_x, zone_corner_y = (zone_corner.x, zone_corner.y)
        zone_x_min = min(drone_x, zone_corner_x)
        zone_y_min = min(drone_y, zone_corner_y)
        zone_x_max = max(drone_x, zone_corner_x)
        zone_y_max = max(drone_y, zone_corner_y)
        radar_blip.zones.append([zone_x_min, zone_y_min, zone_x_max, zone_y_max])

    def update_assets(self):
        self.newly_saved_creatures = np.zeros_like(self.empty_array_saved_creatures)
        for creature in self.game_assets.get_all(asset_type=AssetType.CREATURE).values():
            creature.visible = False
            creature.escaped = True
        self.nb_turns += 1
        self.owners_scores[self.my_owner] = int(self.get_turn_input())
        self.owners_scores[self.foe_owner] = int(self.get_turn_input())
        trophies = self.game_assets.get(AssetType.TROPHIES, 42)
        creatures_win_by = trophies.creatures_win_by
        colors_win_by = trophies.colors_win_by
        kinds_win_by = trophies.kinds_win_by
        my_scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=self.my_owner)
        my_saved_creatures = my_scans.saved_creatures
        foe_scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=self.foe_owner)
        foe_saved_creatures = foe_scans.saved_creatures
        my_scan_count = int(self.get_turn_input())
        for i in range(my_scan_count):
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=int(self.get_turn_input()))
            creature_color, creature_kind = (creature.color, creature.kind)
            if update_saved_scans(my_saved_creatures, creature_color, creature_kind):
                self.newly_saved_creatures[creature_color, creature_kind] = self.my_owner
        update_trophies(owner=self.my_owner, saved_creatures=my_saved_creatures, newly_saved_creatures=self.newly_saved_creatures, creatures_win_by=creatures_win_by, colors_win_by=colors_win_by, kinds_win_by=kinds_win_by)
        foe_scan_count = int(self.get_turn_input())
        for i in range(foe_scan_count):
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=int(self.get_turn_input()))
            creature_color, creature_kind = (creature.color, creature.kind)
            if update_saved_scans(foe_saved_creatures, creature_color, creature_kind):
                self.newly_saved_creatures[creature_color, creature_kind] = self.foe_owner
        update_trophies(owner=self.foe_owner, saved_creatures=foe_saved_creatures, newly_saved_creatures=self.newly_saved_creatures, creatures_win_by=creatures_win_by, colors_win_by=colors_win_by, kinds_win_by=kinds_win_by)
        my_drone_count = int(self.get_turn_input())
        self.my_drones_idt_play_order = []
        for i in range(my_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            self.update_drone(drone_idt, drone_x, drone_y, emergency, battery, AssetType.MY_DRONE)
            self.my_drones_idt_play_order.append(drone_idt)
        foe_drone_count = int(self.get_turn_input())
        for i in range(foe_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            self.update_drone(drone_idt, drone_x, drone_y, emergency, battery, AssetType.FOE_DRONE)
        drone_scan_count = int(self.get_turn_input())
        for i in range(drone_scan_count):
            drone_idt, creature_idt = [int(j) for j in self.get_turn_input().split()]
            drone = self.game_assets.get(asset_type=AssetType.MY_DRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.get(asset_type=AssetType.FOE_DRONE, idt=drone_idt)
            drone.unsaved_creatures_idt.add(creature_idt)
        visible_creature_count = int(self.get_turn_input())
        for i in range(visible_creature_count):
            creature_idt, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in self.get_turn_input().split()]
            self.update_visible_creature(creature_idt, creature_x, creature_y, creature_vx, creature_vy)
        radar_blip_count = int(self.get_turn_input())
        for i in range(radar_blip_count):
            inputs = self.get_turn_input().split()
            drone_idt, creature_idt, radar = (int(inputs[0]), int(inputs[1]), inputs[2])
            self.update_radar_blip(drone_idt, creature_idt, radar)
        if GameLoop.LOG:
            self.print_turn_logs()

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()
            creatures = self.game_assets.get_all(AssetType.CREATURE)
            my_drones = self.game_assets.get_all(AssetType.MY_DRONE)
            foe_drones = self.game_assets.get_all(AssetType.FOE_DRONE)
            all_drones = [*my_drones.values(), *foe_drones.values()]
            scans = self.game_assets.get_all(AssetType.SCANS)
            trophies = self.game_assets.get(AssetType.TROPHIES, 42)
            my_score_computed = compute_score(owner=self.my_owner, saved_creatures=scans[self.my_owner].saved_creatures, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
            foe_score_computed = compute_score(owner=self.foe_owner, saved_creatures=scans[self.foe_owner].saved_creatures, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
            my_drones_from_top_to_bottom = order_assets(my_drones.values(), 'y')
            foe_drones_from_top_to_bottom = order_assets(foe_drones.values(), 'y')
            ordered_drones_from_top_to_bottom = order_assets(all_drones, 'y')
            for creature in creatures.values():
                creature.extra_scores = {owner: 0 for owner in self.owners}
            self.owners_extra_score_with_all_unsaved_creatures = {owner: 0 for owner in self.owners}
            self.owners_max_possible_score = {owner: 0 for owner in self.owners}
            unsaved_creatures_idt = {}
            for owner, ordered_drones in [(self.my_owner, my_drones_from_top_to_bottom), (self.foe_owner, foe_drones_from_top_to_bottom)]:
                unsaved_creatures_idt[owner] = set()
                for drone in ordered_drones:
                    drone.eval_unsaved_creatures_idt = set()
                    for creature_idt in drone.unsaved_creatures_idt:
                        if creature_idt not in unsaved_creatures_idt[owner]:
                            drone.eval_unsaved_creatures_idt.add(creature_idt)
                            unsaved_creatures_idt[owner].add(creature_idt)
            for drone in ordered_drones_from_top_to_bottom:
                owner = drone.owner
                creatures_to_save = [creatures[creature_idt] for creature_idt in drone.eval_unsaved_creatures_idt]
                drone_extra_score = 0
                if len(creatures_to_save) > 0:
                    score_simulation = ScoreSimulation(simulation_scenario=[(owner, creatures_to_save)], owners_saved_creatures={owner: scans[owner].saved_creatures}, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
                    drone_extra_score = score_simulation.compute_new_score()[owner].total - self.owners_scores[owner]
                drone.extra_score_with_unsaved_creatures = drone_extra_score
            for owner in self.owners:
                creatures_to_save = [creatures[creature_idt] for creature_idt in unsaved_creatures_idt[owner]]
                if len(creatures_to_save) > 0:
                    score_simulation = ScoreSimulation(simulation_scenario=[(owner, creatures_to_save)], owners_saved_creatures={owner: scans[owner].saved_creatures}, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
                    owner_extra_score = score_simulation.compute_new_score()[owner].total - self.owners_scores[owner]
                    self.owners_extra_score_with_all_unsaved_creatures[owner] = owner_extra_score
            simulation_scenario = [(drone.owner, [creatures[creature_idt] for creature_idt in drone.eval_unsaved_creatures_idt]) for drone in ordered_drones_from_top_to_bottom]
            owners_saved_creatures = {owner: scans[owner].saved_creatures for owner in self.owners}
            score_simulation = ScoreSimulation(simulation_scenario=simulation_scenario, owners_saved_creatures=owners_saved_creatures, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
            new_owners_scores = {owner: score_simulation.compute_new_score()[owner].total for owner in self.owners}
            new_state = score_simulation.scans_and_trophies_after_simulation()
            creatures_left_to_saved = {owner: [] for owner in self.owners}
            for creature in creatures.values():
                for owner in self.owners:
                    creature_scanned_but_not_saved_by_owner = creature.idt in unsaved_creatures_idt[owner]
                    if creature.kind == Kind.MONSTER.value:
                        pass
                    elif creature.escaped and (not creature_scanned_but_not_saved_by_owner):
                        pass
                    else:
                        creatures_left_to_saved[owner].append(creature)
                        if not creature_scanned_but_not_saved_by_owner:
                            score_simulation = ScoreSimulation(simulation_scenario=[(owner, [creature])], **new_state)
                            new_owner_score = score_simulation.compute_new_score()[owner].total
                            creature_extra_score = new_owner_score - new_owners_scores[owner]
                            creature.extra_scores[owner] = creature_extra_score
            for owner in self.owners:
                score_simulation = ScoreSimulation(simulation_scenario=[(owner, creatures_left_to_saved[owner])], owners_saved_creatures={owner: scans[owner].saved_creatures}, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
                self.owners_max_possible_score[owner] = score_simulation.compute_new_score()[owner].total
            for creature_idt, creature in creatures.items():
                if not creature.visible:
                    possible_zones = [creature.habitat]
                    for drone_idt, drone in my_drones.items():
                        radar_idt = hash((drone_idt, creature_idt))
                        radar_blip = self.game_assets.get(asset_type=AssetType.RADAR_BLIP, idt=radar_idt)
                        if radar_blip is not None:
                            radar_blip_zones = radar_blip.zones
                            n = min(len(radar_blip_zones), self.max_number_of_radar_blips_used)
                            for i in range(0, n):
                                possible_zones.append(radar_blip_zones[-i - 1])
                    intersection = np.array(possible_zones)
                    x_min = np.max(intersection[:, 0])
                    y_min = np.max(intersection[:, 1])
                    x_max = np.min(intersection[:, 2])
                    y_max = np.min(intersection[:, 3])
                    if creature.last_turn_visible:
                        last_seen_turns = self.nb_turns - creature.last_turn_visible
                        current_x_projection = creature.x + last_seen_turns * creature.vx
                        current_y_projection = creature.y + last_seen_turns * creature.vy
                        if x_min <= current_x_projection <= x_max and y_min <= current_y_projection <= y_max:
                            creature.x = current_x_projection
                            creature.y = current_y_projection
                        else:
                            creature.x = (x_min + x_max) / 2
                            creature.y = (y_min + y_max) / 2
                    else:
                        creature.x = (x_min + x_max) / 2
                        creature.y = (y_min + y_max) / 2
            for my_drone in my_drones.values():
                my_drone.has_to_flee_from = []
                for monster in self.monsters:
                    if self.hash_map_norms[monster.position - my_drone.position] <= self.flee_radius_from_monsters:
                        my_drone.has_to_flee_from.append(monster)
            default_action = Action(move=False, light=False)
            my_drones_action = {drone_idt: default_action for drone_idt in self.my_drones_idt_play_order}
            unassigned_drones = {drone_idt: drone for drone_idt, drone in my_drones.items() if drone.emergency == 0}
            for drone_idt, drone in unassigned_drones.copy().items():
                drone_has_to_flee_from = drone.has_to_flee_from
                if len(drone_has_to_flee_from) == 1:
                    del unassigned_drones[drone_idt]
                    monster = drone_has_to_flee_from[0]
                    vector_to_creature = monster.position - drone.position
                    distance_to_creature = self.hash_map_norms[vector_to_creature]
                    if distance_to_creature > self.safe_radius_from_monsters:
                        v = 1 / distance_to_creature ** (1 / 2) * vector_to_creature
                        flee_vectors = [Vector(v.y, -v.x), Vector(-v.y, v.x)]
                        flee_vector = flee_vectors[0]
                        vector_to_center = self.map_center - drone.position
                        cos_with_center = flee_vector.dot(vector_to_center)
                        if flee_vectors[1].dot(vector_to_center) > cos_with_center:
                            flee_vector = flee_vectors[1]
                        my_drones_action[drone_idt] = Action(target=drone.position + self.drone_speed ** (1 / 2) * flee_vector, comment=f'FLEE FROM {monster.log()}')
                    else:
                        flee_vector = -1 * vector_to_creature
                        my_drones_action[drone_idt] = Action(target=drone.position + self.drone_speed ** (1 / 2) / distance_to_creature ** (1 / 2) * flee_vector, comment=f'FLEE FROM {monster.log()}')
                elif len(drone_has_to_flee_from) > 1:
                    del unassigned_drones[drone_idt]
                    flee_vector = Vector(0, 0)
                    comment = ''
                    for monster in drone_has_to_flee_from:
                        flee_vector += drone.position - monster.position
                        comment = f'{comment} {monster.log()}'
                    my_drones_action[drone_idt] = Action(target=drone.position + self.drone_speed ** (1 / 2) / flee_vector.norm * flee_vector, comment=f'FLEE FROM{comment}')
            if len(unassigned_drones) > 0:
                extra_score_to_win = self.owners_max_possible_score[self.foe_owner] - self.owners_scores[self.my_owner] + 1
                extra_score_if_all_my_drones_save = self.owners_extra_score_with_all_unsaved_creatures[self.my_owner]
                if len(unassigned_drones) == len(my_drones) and extra_score_if_all_my_drones_save >= extra_score_to_win:
                    for drone in my_drones.values():
                        if len(drone.unsaved_creatures_idt) > 0:
                            my_drones_action[drone.idt] = Action(target=Point(drone.x, 499), comment=f'SAVE {extra_score_if_all_my_drones_save} ({extra_score_to_win})')
                            del unassigned_drones[drone.idt]
                else:
                    ordered_my_drones_with_most_extra_score = order_assets(unassigned_drones.values(), on_attr='extra_score_with_unsaved_creatures', ascending=False)
                    for drone in ordered_my_drones_with_most_extra_score:
                        drone_extra_score = drone.extra_score_with_unsaved_creatures
                        if drone_extra_score >= 20 or drone_extra_score >= extra_score_to_win:
                            my_drones_action[drone.idt] = Action(target=Point(drone.x, 499), comment=f'SAVE {drone.extra_score_with_unsaved_creatures} ({extra_score_to_win})')
                            del unassigned_drones[drone.idt]
            if len(unassigned_drones) > 0:
                nb_find_actions = 0
                ordered_creatures_with_most_extra_score = order_assets(creatures.values(), on_attr='my_extra_score', ascending=False)
                creatures_with_extra_score = [creature for creature in ordered_creatures_with_most_extra_score if creature.my_extra_score > 0]
                nb_creatures_with_extra_score = len(creatures_with_extra_score)
                if nb_creatures_with_extra_score == 1:
                    drone_target = ordered_creatures_with_most_extra_score[0]
                    for drone_idt, drone in unassigned_drones.items():
                        light = use_light_to_find_a_target(drone, drone_target)
                        my_drones_action[drone_idt] = Action(target=drone_target, light=light, comment=f'FIND {drone_target.log()}')
                elif nb_creatures_with_extra_score > 1:
                    x_median = np.median([creature.x for creature in creatures_with_extra_score])
                    creatures_with_extra_score_left = [creature for creature in creatures_with_extra_score if creature.x <= x_median]
                    creatures_with_extra_score_right = [creature for creature in creatures_with_extra_score if creature.x > x_median]
                    left_target = creatures_with_extra_score_left[0]
                    if len(creatures_with_extra_score_right) == 0:
                        right_target = creatures_with_extra_score_left[1]
                        if left_target.x > right_target.x:
                            left_target = creatures_with_extra_score_left[1]
                            right_target = creatures_with_extra_score_left[0]
                    else:
                        right_target = creatures_with_extra_score_right[0]
                    my_drones_from_left_to_right = order_assets(my_drones.values(), 'x')
                    drone_left_idt = my_drones_from_left_to_right[0].idt
                    drone_right_idt = my_drones_from_left_to_right[-1].idt
                    drone_left = unassigned_drones.get(drone_left_idt)
                    if drone_left is not None:
                        light = use_light_to_find_a_target(drone_left, left_target)
                        my_drones_action[drone_left_idt] = Action(target=left_target, light=light, comment=f'FIND {left_target.log()}')
                    drone_right = unassigned_drones.get(drone_right_idt)
                    if drone_right is not None:
                        light = use_light_to_find_a_target(drone_right, right_target)
                        my_drones_action[drone_right_idt] = Action(target=right_target, light=light, comment=f'FIND {right_target.log()}')
                else:
                    for drone_idt, drone in unassigned_drones.items():
                        if drone.extra_score_with_unsaved_creatures > 0:
                            my_drones_action[drone.idt] = Action(target=Point(drone.x, 499), comment=f'SAVE {drone.extra_score_with_unsaved_creatures}')
                        else:
                            drone_target = order_assets(creatures.values(), on_attr='foe_extra_score', ascending=False)[nb_find_actions]
                            nb_find_actions += 1
                            my_drones_action[drone.idt] = Action(target=drone_target, light=True, comment=f'FIND {drone_target.log()}')
            for drone_idt in self.my_drones_idt_play_order:
                print(my_drones_action[drone_idt])
GameLoop().start()