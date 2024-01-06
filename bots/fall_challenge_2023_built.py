import sys
import numpy as np
import math
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from enum import Enum
from dataclasses import asdict, dataclass, field
from typing import List, Tuple, Union, Set, Iterable, Callable, Any, Dict

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

    def __round__(self, n=None):
        return Point(round(self.x, n), round(self.y, n))

    def dist(self, point):
        return math.dist([self.x, self.y], [point.x, point.y])

class Vector(Point):

    def __init__(self, x, y):
        super().__init__(x, y)

    def __mul__(self, nombre):
        return Vector(nombre * self.x, nombre * self.y)

    def __round__(self, n=None):
        return Vector(round(self.x, n), round(self.y, n))

    def dot(self, vector):
        return self.x * vector.x + self.y * vector.y

    @property
    def norm2(self):
        return self.dot(self)

    @property
    def norm(self):
        return math.sqrt(self.norm2)

class VectorHashMap:

    def __init__(self, func_to_cache: Callable[[Vector], Any]):
        self.hasp_map: Dict[int, Any] = {}
        self.func_to_cache = func_to_cache

    def _apply_func(self, vector: Vector) -> Any:
        key = hash(vector)
        if key not in self.hasp_map:
            self.hasp_map[key] = self.func_to_cache(vector)
        return self.hasp_map[key]

    def __getitem__(self, vector):
        return self._apply_func(vector)

class Rotate2DMatrix:

    def __init__(self):
        self.matrix_hash_map: Dict[int, np.ndarray] = {}

    def get_rotate_matrix(self, theta: float):
        key = hash(theta % 2 * math.pi)
        if key not in self.matrix_hash_map:
            cos = math.cos(theta)
            sin = math.sin(theta)
            self.matrix_hash_map[key] = np.array([[cos, -sin], [sin, cos]])
        return self.matrix_hash_map[key]

    def rotate_vector(self, vector: Vector, theta: float):
        rotation_matrix = self.get_rotate_matrix(theta)
        rotation = rotation_matrix.dot(np.array([[vector.x], [vector.y]]))
        return Vector(rotation[0][0], rotation[1][0])
HASH_MAP_NORM2 = VectorHashMap(func_to_cache=lambda v: v.norm2)
HASH_MAP_NORM = VectorHashMap(func_to_cache=lambda v: math.sqrt(HASH_MAP_NORM2[v]))
ROTATE_2D_MATRIX = Rotate2DMatrix()
MY_OWNER = 1
FOE_OWNER = 2
OWNERS = [MY_OWNER, FOE_OWNER]
X_MIN = 0
Y_MIN = 0
X_MAX = 10000
Y_MAX = 10000
MAP_CENTER = Point(X_MAX / 2, Y_MAX / 2)
D_MAX = HASH_MAP_NORM[Vector(X_MAX, Y_MAX)]
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
LIGHT_RADIUS2 = HASH_MAP_NORM2[Vector(0, 800)]
AUGMENTED_LIGHT_RADIUS2 = HASH_MAP_NORM2[Vector(0, 2000)]
EMERGENCY_RADIUS2 = HASH_MAP_NORM2[Vector(0, 500)]
DRONE_MAX_SPEED = HASH_MAP_NORM[Vector(0, 600)]
SAFE_RADIUS_FROM_MONSTERS2 = HASH_MAP_NORM2[Vector(0, 500 + 540 + 600)]
FRIGHTEN_RADIUS_FROM_DRONE = HASH_MAP_NORM[Vector(0, 1400)]
MAX_NUMBER_OF_RADAR_BLIPS_USED = 3
LIMIT_DISTANCE_FROM_EDGE_TO_DENY = HASH_MAP_NORM[Vector(1500, 0)]
SCARE_FROM_DISTANCE = HASH_MAP_NORM[Vector(790, 0)]
LIMIT_DISTANCE_TO_DENY2 = HASH_MAP_NORM2[Vector(1500, 0)]

@dataclass(slots=True)
class Score:
    base_creatures: int = 0
    bonus_creatures: int = 0
    base_colors: int = 0
    bonus_colors: int = 0
    base_kinds: int = 0
    bonus_kinds: int = 0

    def __add__(self, other):
        other_dict = asdict(other)
        return Score(**{attr: value + other_dict[attr] for attr, value in asdict(self).items()})

    def __sub__(self, other):
        other_dict = asdict(other)
        return Score(**{attr: value - other_dict[attr] for attr, value in asdict(self).items()})

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

@dataclass(slots=True)
class Asset:
    idt: int

    @property
    def value(self):
        return None

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

    @property
    def value(self):
        return self.my_extra_score

@dataclass(slots=True)
class Drone(Unit):
    emergency: int = None
    battery: int = None
    light_on: bool = False
    unsaved_creatures_idt: Set[int] = field(default_factory=set)
    eval_unsaved_creatures_idt: Set[int] = field(default_factory=set)
    extra_score_with_unsaved_creatures: int = 0
    has_to_avoid: List[Creature] = field(default_factory=list)

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

@dataclass
class Action:
    move: bool = True
    target: Union[Point, Unit] = MAP_CENTER
    light: bool = False
    comment: Union[int, str] = None
    value: int = 0

    def __repr__(self):
        instruction = f'MOVE {int(self.target.x)} {int(self.target.y)}' if self.move else 'WAIT'
        instruction = f'{instruction} {(1 if self.light else 0)}'
        if self.comment:
            instruction = f'{instruction} {self.comment}'
        return instruction

    @property
    def target_position(self):
        return Point(self.target.x, self.target.y)

def choose_action_for_drones(my_drones: Dict[int, MyDrone], actions_priorities: List[Dict[int, Action]], default_action: Action):
    my_drones_action = {}
    for drone_idt, drone in my_drones.items():
        if drone.emergency == 0:
            action_chosen = None
            i, N = (0, len(actions_priorities))
            while not action_chosen and i < N:
                action_chosen = actions_priorities[i].get(drone_idt)
                i += 1
            if not action_chosen:
                action_chosen = default_action
        else:
            action_chosen = default_action
        my_drones_action[drone_idt] = action_chosen
    return my_drones_action

@dataclass(frozen=True)
class Edge:
    from_node: int
    to_node: int
    directed: bool = False
    weight: float = 1

class AdjacencyMatrix:

    def __init__(self, nodes_edges: np.ndarray):
        self.array: np.ndarray = nodes_edges

    @property
    def sparce_matrix(self) -> csr_matrix:
        return csr_matrix(self.array)

    def __getitem__(self, key):
        return self.array.__getitem__(key)

    def __setitem__(self, key, value: float):
        self.array.__setitem__(key, value)

    def update_edge(self, edge: Edge, weight: float):
        self[edge.from_node, edge.to_node] = weight
        if not edge.directed:
            self[edge.to_node, edge.from_node] = weight

    def add_edge(self, edge: Edge):
        self.update_edge(edge, edge.weight)

    def remove_edge(self, edge: Edge):
        self.update_edge(edge, 0)

def create_adjacency_matrix_from_edges(edges: Iterable[Edge], nodes_number: int) -> AdjacencyMatrix:
    adjacency_matrix = AdjacencyMatrix(np.zeros((nodes_number, nodes_number), dtype=float))
    for edge in edges:
        adjacency_matrix.add_edge(edge)
    return adjacency_matrix

def evaluate_positions_of_creatures(creatures: Dict[int, Creature], radar_blips: Dict[int, RadarBlip], my_drones: Dict[int, MyDrone], nb_turns: int, max_number_of_radar_blips_used=MAX_NUMBER_OF_RADAR_BLIPS_USED):
    for creature_idt, creature in creatures.items():
        if not creature.visible:
            possible_zones = [creature.habitat]
            for drone_idt, drone in my_drones.items():
                radar_blip = radar_blips.get(hash((drone_idt, creature_idt)))
                if radar_blip is not None:
                    radar_blip_zones = radar_blip.zones
                    n = min(len(radar_blip_zones), max_number_of_radar_blips_used)
                    for i in range(0, n):
                        possible_zones.append(radar_blip_zones[-i - 1])
            intersection = np.array(possible_zones)
            x_min = np.max(intersection[:, 0])
            y_min = np.max(intersection[:, 1])
            x_max = np.min(intersection[:, 2])
            y_max = np.min(intersection[:, 3])
            if creature.last_turn_visible:
                last_seen_turns = nb_turns - creature.last_turn_visible
                current_x_projection = creature.x + last_seen_turns * creature.vx
                current_y_projection = creature.y + last_seen_turns * creature.vy
                if x_min <= current_x_projection <= x_max and y_min <= current_y_projection <= y_max:
                    creature.x = current_x_projection
                    creature.y = current_y_projection
                    creature.next_x = current_x_projection + creature.vx
                    creature.next_y = current_y_projection + creature.vy
                else:
                    creature.x = creature.next_x = round((x_min + x_max) / 2)
                    creature.y = creature.next_y = round((y_min + y_max) / 2)
            else:
                creature.x = creature.next_x = round((x_min + x_max) / 2)
                creature.y = creature.next_y = round((y_min + y_max) / 2)
        else:
            creature.next_x = creature.x + creature.vx
            creature.next_y = creature.y + creature.vy

def evaluate_monsters_to_avoid(my_drones: Dict[int, MyDrone], monsters: List[Creature], nb_turns: int, hash_map_norm2=HASH_MAP_NORM2, safe_radius_from_monsters=SAFE_RADIUS_FROM_MONSTERS2):
    for drone in my_drones.values():
        drone.has_to_avoid = []
        for monster in monsters:
            if monster.last_turn_visible:
                if nb_turns - monster.last_turn_visible <= 3:
                    if hash_map_norm2[monster.position - drone.position] <= safe_radius_from_monsters:
                        drone.has_to_avoid.append(monster)

def is_collision(drone: Drone, monster: Creature, collision_range=EMERGENCY_RADIUS2, hash_map_norm2=HASH_MAP_NORM2):
    xm, ym, xd, yd = (monster.x, monster.y, drone.x, drone.y)
    x, y = (xm - xd, ym - yd)
    vx, vy = (monster.vx - drone.vx, monster.vy - drone.vy)
    a = hash_map_norm2[Vector(vx, vy)]
    if a <= 0:
        return False
    b = 2 * (x * vx + y * vy)
    c = hash_map_norm2[Vector(x, y)] - collision_range
    delta = b ** 2 - 4 * a * c
    if delta < 0:
        return False
    t = (-b - math.sqrt(delta)) / (2 * a)
    if t <= 0:
        return False
    if t > 1:
        return False
    return True

def get_drone_next_position_with_target(drone: MyDrone, target_position: Point, drone_max_speed=DRONE_MAX_SPEED, hash_map_norm=HASH_MAP_NORM):
    drone_to_target = target_position - drone.position
    distance_to_target = hash_map_norm[drone_to_target]
    if distance_to_target <= drone_max_speed:
        return round(target_position)
    else:
        return round(drone_max_speed / distance_to_target * drone_to_target) + drone.position

def is_next_position_safe(drone: MyDrone, next_position: Point, x_min=X_MIN, y_min=Y_MIN, x_max=X_MAX, y_max=Y_MAX):
    next_x, next_y = (next_position.x, next_position.y)
    drone.vx = next_x - drone.x
    drone.vy = next_y - drone.y
    if next_x < x_min or next_x > x_max or next_y < y_min or (next_y > y_max):
        return False
    is_safe = True
    for monster in drone.has_to_avoid:
        if is_collision(drone, monster):
            is_safe = False
    return is_safe

def connect_units(units_to_connect: List[Unit], total_units_count: int, min_dist=800 / D_MAX, hash_map_norm=HASH_MAP_NORM, d_max=D_MAX, max_score=96) -> Union[None, AdjacencyMatrix]:
    nb_units_to_connect = len(units_to_connect)
    if nb_units_to_connect == 0:
        return None
    edges = []
    for i, unit in enumerate(units_to_connect):
        unit_value = unit.value if unit.value else 0
        nb_connected_neighbors = 0
        neighbors = units_to_connect.copy()
        neighbors.pop(i)
        if len(neighbors) > 0:
            ordered_neighbors = sorted(neighbors, key=lambda u: hash_map_norm[u.position - unit.position])
            while nb_connected_neighbors < len(ordered_neighbors):
                neighbor = ordered_neighbors[nb_connected_neighbors]
                nb_connected_neighbors += 1
                neighbor_value = neighbor.value
                if neighbor_value:
                    if neighbor_value > 0:
                        dist = max(hash_map_norm[neighbor.position - unit.position] / d_max, min_dist)
                        weight = dist / ((unit_value + neighbor_value) / max_score)
                        edges.append(Edge(from_node=unit.idt, to_node=neighbor.idt, directed=True, weight=weight))
    return create_adjacency_matrix_from_edges(edges=edges, nodes_number=total_units_count)

def optimized_next_target(drone: MyDrone, drone_target: Creature, creatures_connected_to_drone: List[Creature], total_units_count: int):
    adjacency_matrix = connect_units(units_to_connect=[drone, *creatures_connected_to_drone], total_units_count=total_units_count)
    predecessors = dijkstra(adjacency_matrix.sparce_matrix, return_predecessors=True)[1]
    predecessor_idt = drone_target.idt
    while predecessor_idt != drone.idt:
        next_target_idt = predecessor_idt
        predecessor_idt = predecessors[drone.idt, next_target_idt]
    return next_target_idt

def optimize_path_with_targets(drone: MyDrone, first_target: Creature, final_target: Creature, hash_map_norm=HASH_MAP_NORM) -> Point:
    vector_to_final_target = final_target.next_position - drone.position
    vector_to_first_target = first_target.next_position - drone.position
    cos = vector_to_final_target.dot(vector_to_first_target)
    if cos > 0:
        dist_to_final_target = hash_map_norm[vector_to_final_target]
        dist_to_first_target = hash_map_norm[vector_to_final_target]
        cos = min(cos / (dist_to_final_target * dist_to_first_target), 1)
        sin = math.sqrt(1 - cos ** 2)
        d_min = min(dist_to_first_target, dist_to_final_target)
        max_deviation = int(round(sin * d_min))
        if max_deviation > 1500:
            return first_target.next_position
        elif max_deviation > 750:
            return drone.position + 1 / 2 * (vector_to_final_target + vector_to_first_target)
        else:
            return final_target.next_position
    return first_target.next_position

def use_light_to_find_a_target(drone: Drone, target: Creature, hash_map_norm2=HASH_MAP_NORM2, augmented_light_radius=AUGMENTED_LIGHT_RADIUS2):
    battery = drone.battery
    if battery >= 10 and drone.y > 4000:
        return True
    if drone.battery >= 5:
        distance_to_target = hash_map_norm2[target.position - drone.position]
        if distance_to_target <= augmented_light_radius and (not target.visible):
            return True
    return False

def save_points(my_drones: Dict[int, MyDrone], owners_scores_computed: Dict[int, Score], owners_max_possible_score: Dict[int, Score], owners_extra_score_with_all_unsaved_creatures: Dict[int, Score], owners_bonus_score_left: Dict[int, Dict[str, int]], my_owner=MY_OWNER, foe_owner=FOE_OWNER):
    actions = {}
    my_total_max_score = owners_max_possible_score[my_owner].total
    my_max_possible_unshared = owners_max_possible_score[my_owner].base + owners_scores_computed[my_owner].bonus + owners_bonus_score_left[my_owner]['unshared']
    foe_max_possible_unshared = owners_max_possible_score[foe_owner].base + owners_scores_computed[foe_owner].bonus + owners_bonus_score_left[foe_owner]['unshared']
    bonus_shared_left = owners_bonus_score_left[my_owner]['shared']
    X = (bonus_shared_left + foe_max_possible_unshared - my_max_possible_unshared) / 2
    Y = bonus_shared_left - X
    my_extra_score_to_win = foe_max_possible_unshared + Y - owners_scores_computed[my_owner].total + 1
    extra_score_if_all_my_drones_save = owners_extra_score_with_all_unsaved_creatures[my_owner].total
    if extra_score_if_all_my_drones_save >= my_extra_score_to_win:
        for drone in my_drones.values():
            if len(drone.unsaved_creatures_idt) > 0:
                actions[drone.idt] = Action(target=Point(drone.x, 499), comment=f'SAVE {drone.extra_score_with_unsaved_creatures:.0f}/{extra_score_if_all_my_drones_save:.0f}/{my_extra_score_to_win:.0f}/{my_total_max_score:.0f}')
    else:
        ordered_my_drones_with_most_extra_score = order_assets(my_drones.values(), on_attr='extra_score_with_unsaved_creatures', ascending=False)
        for drone in ordered_my_drones_with_most_extra_score:
            drone_extra_score = drone.extra_score_with_unsaved_creatures
            if drone_extra_score >= 20 or drone_extra_score >= my_extra_score_to_win:
                actions[drone.idt] = Action(target=Point(drone.x, 499), comment=f'SAVE {drone.extra_score_with_unsaved_creatures:.0f}/{extra_score_if_all_my_drones_save:.0f}/{my_extra_score_to_win:.0f}/{my_total_max_score:.0f}')
    return actions

def find_valuable_target(my_drones: Dict[int, MyDrone], creatures: Dict[int, Creature], total_units_count: int, hash_map_norm2=HASH_MAP_NORM2):
    actions = {}
    ordered_creatures_with_most_extra_score = order_assets(creatures.values(), on_attr='my_extra_score', ascending=False)
    creatures_with_extra_score = [creature for creature in ordered_creatures_with_most_extra_score if creature.my_extra_score > 0]
    nb_creatures_with_extra_score = len(creatures_with_extra_score)
    if nb_creatures_with_extra_score == 1:
        drone_target = ordered_creatures_with_most_extra_score[0]
        closest_drone = sorted(my_drones.values(), key=lambda drone: hash_map_norm2[drone_target.next_position - drone.position])[0]
        light = use_light_to_find_a_target(closest_drone, drone_target)
        actions[closest_drone.idt] = Action(target=drone_target.next_position, light=light, comment=f'FIND {drone_target.log()}')
    elif nb_creatures_with_extra_score > 1:
        creatures_x = [creature.x for creature in creatures_with_extra_score]
        x_min = np.min(creatures_x)
        x_median = np.median(creatures_x)
        x_max = np.max(creatures_x)
        if x_median == x_min or x_median == x_max:
            x_median = (x_max + x_min) / 2
        creatures_with_extra_score_left = [creature for creature in creatures_with_extra_score if creature.x < x_median]
        creatures_with_extra_score_right = [creature for creature in creatures_with_extra_score if creature.x > x_median]
        creatures_with_extra_score_median = [creature for creature in creatures_with_extra_score if creature.x == x_median]
        for creature in creatures_with_extra_score_median:
            nb_creatures_on_the_left = len(creatures_with_extra_score_left)
            nb_creatures_on_the_right = len(creatures_with_extra_score_right)
            if nb_creatures_on_the_left <= nb_creatures_on_the_right:
                creatures_with_extra_score_left.append(creature)
            else:
                creatures_with_extra_score_right.append(creature)
        left_target = creatures_with_extra_score_left[0]
        right_target = creatures_with_extra_score_right[0]
        my_drones_from_left_to_right = order_assets(my_drones.values(), 'x')
        drone_left = my_drones_from_left_to_right[0]
        drone_right = my_drones_from_left_to_right[-1]
        next_left_target = creatures[optimized_next_target(drone=drone_left, drone_target=left_target, creatures_connected_to_drone=creatures_with_extra_score_left, total_units_count=total_units_count)]
        next_right_target = creatures[optimized_next_target(drone=drone_right, drone_target=right_target, creatures_connected_to_drone=creatures_with_extra_score_right, total_units_count=total_units_count)]
        optimized_left_target = optimize_path_with_targets(drone=drone_left, first_target=next_left_target, final_target=left_target)
        light = use_light_to_find_a_target(drone_left, next_left_target)
        actions[drone_left.idt] = Action(target=optimized_left_target, light=light, comment=f'FIND {left_target.log()} ({next_left_target.log()})')
        optimized_right_target = optimize_path_with_targets(drone=drone_right, first_target=next_right_target, final_target=right_target)
        light = use_light_to_find_a_target(drone_right, next_right_target)
        actions[drone_right.idt] = Action(target=optimized_right_target, light=light, comment=f'FIND {right_target.log()} ({next_right_target.log()})')
    return actions

def deny_valuable_fish_for_foe(my_drones: Dict[int, MyDrone], creatures: Dict[int, Creature], nb_turns: int, hash_map_norm2=HASH_MAP_NORM2, monster_kind=Kind.MONSTER.value, x_max=X_MAX, x_center=X_MAX / 2, limit_distance_from_edge=LIMIT_DISTANCE_FROM_EDGE_TO_DENY, scare_from=SCARE_FROM_DISTANCE, limit_distance_to_deny=LIMIT_DISTANCE_TO_DENY2):
    actions = {}
    fishes_close_to_edge = [creature for creature in creatures.values() if (nb_turns - creature.last_turn_visible <= 3 if creature.last_turn_visible else False) and creature.kind != monster_kind and (creature.foe_extra_score > 0) and (creature.next_x < limit_distance_from_edge or x_max - creature.next_x < limit_distance_from_edge)]
    if len(fishes_close_to_edge) > 0:
        fishes_with_most_extra_for_foe: List[Creature] = order_assets(fishes_close_to_edge, on_attr='foe_extra_score', ascending=False)
        for fish in fishes_with_most_extra_for_foe:
            closest_drone = sorted(my_drones.values(), key=lambda drone: hash_map_norm2[fish.next_position - drone.position])[0]
            if hash_map_norm2[fish.next_position - closest_drone.position] < limit_distance_to_deny:
                edge_direction = 1 if fish.next_x > x_center else -1
                if not actions.get(closest_drone.idt):
                    target = fish.next_position - edge_direction * Vector(scare_from, 0)
                    actions[closest_drone.idt] = Action(target=target, comment=f'DENY {fish.log()}')
    return actions

def just_do_something(my_drones: Dict[int, MyDrone], creatures: Dict[int, Creature], x_center=X_MAX / 2, scare_from=SCARE_FROM_DISTANCE):
    actions = {}
    nb_find_actions = 0
    for drone_idt, drone in my_drones.items():
        if drone.extra_score_with_unsaved_creatures > 0:
            actions[drone.idt] = Action(target=Point(drone.x, 499), comment=f'SAVE {drone.extra_score_with_unsaved_creatures:.0f}')
        else:
            drone_target = order_assets(creatures.values(), on_attr='foe_extra_score', ascending=False)[nb_find_actions]
            nb_find_actions += 1
            edge_direction = 1 if drone_target.next_x > x_center else -1
            target = drone_target.next_position - edge_direction * Vector(scare_from, 0)
            actions[drone_idt] = Action(target=target, light=True, comment=f'DENY {drone_target.log()}')
    return actions

def avoid_monsters(drone: MyDrone, aimed_action: Action, default_action: Action, hash_map_norm2=HASH_MAP_NORM2, rotate_matrix=ROTATE_2D_MATRIX, theta_increment=math.pi / 16, drone_max_speed=DRONE_MAX_SPEED):
    safe_action = aimed_action
    drone_has_to_avoid = drone.has_to_avoid
    if len(drone.has_to_avoid) == 0:
        return safe_action
    target_position = aimed_action.target_position
    drone_next_position = get_drone_next_position_with_target(drone, target_position)
    if is_next_position_safe(drone, drone_next_position):
        return safe_action
    if len(drone_has_to_avoid) > 0:
        speed_wanted = Vector(drone.vx, drone.vy)
        speeds_to_try = [speed_wanted, drone_max_speed / speed_wanted.norm * speed_wanted, 1 / 2 * speed_wanted]
        for speed in speeds_to_try:
            thetas = [theta for theta in np.arange(theta_increment, math.pi + theta_increment, theta_increment)]
            for theta in thetas:
                next_positions_to_try = [drone.position + round(rotate_matrix.rotate_vector(speed, theta)), drone.position + round(rotate_matrix.rotate_vector(speed, -theta))]
                next_positions_to_try = sorted(next_positions_to_try, key=lambda p: hash_map_norm2[target_position - p])
                for next_position in next_positions_to_try:
                    if is_next_position_safe(drone, next_position):
                        safe_action.target = next_position
                        return safe_action
    return default_action

def order_assets(assets: List[Union[Asset, Creature, Drone, MyDrone]], on_attr: str, ascending: bool=True) -> List[Union[Asset, Creature, Drone, MyDrone]]:
    return sorted(assets, key=lambda asset: getattr(asset, on_attr), reverse=not ascending)

class AssetType(Enum):
    CREATURE = Creature
    MY_DRONE = MyDrone
    FOE_DRONE = FoeDrone
    RADAR_BLIP = RadarBlip
    SCANS = Scans
    TROPHIES = Trophies

class GameAssets:

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

def update_trophies_for_all(my_saved_creatures: np.ndarray, foe_saved_creatures: np.ndarray, my_newly_saved_creatures: np.ndarray, foe_newly_saved_creatures: np.ndarray, trophies: Trophies, activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS, score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):
    creatures_win_by = trophies.creatures_win_by
    creatures_trophies_available = creatures_win_by == 0
    my_newly_completed_creatures = my_newly_saved_creatures == MY_OWNER
    foe_newly_completed_creatures = foe_newly_saved_creatures == FOE_OWNER
    creatures_win_by[creatures_trophies_available & my_newly_completed_creatures] += MY_OWNER
    creatures_win_by[creatures_trophies_available & foe_newly_completed_creatures] += FOE_OWNER
    colors_win_by = trophies.colors_win_by
    colors_trophies_available = colors_win_by == 0
    my_completed_colors = my_saved_creatures.dot(activate_colors) == score_for_full_color
    foe_completed_colors = foe_saved_creatures.dot(activate_colors) == score_for_full_color
    my_already_completed_colors = (my_saved_creatures - my_newly_saved_creatures).dot(activate_colors) == score_for_full_color
    foe_already_completed_colors = (foe_saved_creatures - foe_newly_saved_creatures).dot(activate_colors) == score_for_full_color
    my_newly_completed_colors = my_completed_colors & ~my_already_completed_colors
    foe_newly_completed_colors = foe_completed_colors & ~foe_already_completed_colors
    colors_win_by[colors_trophies_available & my_newly_completed_colors] += MY_OWNER
    colors_win_by[colors_trophies_available & foe_newly_completed_colors] += FOE_OWNER
    kinds_win_by = trophies.kinds_win_by
    kinds_trophies_available = kinds_win_by == 0
    my_completed_kinds = activate_kinds.dot(my_saved_creatures) == score_for_full_kind
    foe_completed_kinds = activate_kinds.dot(foe_saved_creatures) == score_for_full_kind
    my_already_completed_kinds = activate_kinds.dot(my_saved_creatures - my_newly_saved_creatures) == score_for_full_kind
    foe_already_completed_kinds = activate_kinds.dot(foe_saved_creatures - foe_newly_saved_creatures) == score_for_full_kind
    my_newly_completed_kinds = my_completed_kinds & ~my_already_completed_kinds
    foe_newly_completed_kinds = foe_completed_kinds & ~foe_already_completed_kinds
    kinds_win_by[kinds_trophies_available & my_newly_completed_kinds] += MY_OWNER
    kinds_win_by[kinds_trophies_available & foe_newly_completed_kinds] += FOE_OWNER

def compute_score(owner: int, saved_creatures: np.ndarray, creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray, score_by_kind=SCORE_BY_KIND, activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS, score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):
    score = Score()
    bonus_saved_creatures = np.zeros_like(saved_creatures)
    bonus_saved_creatures[creatures_win_by == owner] = 1
    colors_activated = saved_creatures.dot(activate_colors)
    kinds_activated = activate_kinds.dot(saved_creatures)
    score.base_creatures = saved_creatures.dot(score_by_kind).sum()
    score.bonus_creatures = bonus_saved_creatures.dot(score_by_kind).sum()
    score.base_colors = colors_activated[colors_activated == score_for_full_color].sum()
    score.bonus_colors = score_for_full_color * colors_win_by[colors_win_by == owner].size
    score.base_kinds = kinds_activated[kinds_activated == score_for_full_kind].sum()
    score.bonus_kinds = score_for_full_kind * kinds_win_by[kinds_win_by == owner].size
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

def evaluate_extra_scores_for_multiple_scenarios(creatures: Dict[int, Creature], my_drones: Dict[int, MyDrone], foe_drones: Dict[int, FoeDrone], scans: Dict[int, Scans], trophies: Trophies, current_owners_scores: Dict[int, Score], my_owner=MY_OWNER, foe_owner=FOE_OWNER, owners=OWNERS, monster_kind=Kind.MONSTER.value, score_by_kind=SCORE_BY_KIND, score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):
    all_drones = [*my_drones.values(), *foe_drones.values()]
    my_drones_from_top_to_bottom = order_assets(my_drones.values(), 'y')
    foe_drones_from_top_to_bottom = order_assets(foe_drones.values(), 'y')
    ordered_drones_from_top_to_bottom = order_assets(all_drones, 'y')
    for creature in creatures.values():
        creature.extra_scores = {owner: 0 for owner in owners}
    owners_extra_score_with_all_unsaved_creatures = {owner: Score() for owner in owners}
    owners_max_possible_score = {owner: Score() for owner in owners}
    owners_bonus_score_left = {owner: {'shared': 0, 'unshared': 0} for owner in owners}
    unsaved_creatures_idt = {}
    for owner, ordered_drones in [(my_owner, my_drones_from_top_to_bottom), (foe_owner, foe_drones_from_top_to_bottom)]:
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
            drone_extra_score = score_simulation.compute_new_score()[owner].total - current_owners_scores[owner].total
        drone.extra_score_with_unsaved_creatures = drone_extra_score
    for owner in owners:
        creatures_to_save = [creatures[creature_idt] for creature_idt in unsaved_creatures_idt[owner]]
        if len(creatures_to_save) > 0:
            score_simulation = ScoreSimulation(simulation_scenario=[(owner, creatures_to_save)], owners_saved_creatures={owner: scans[owner].saved_creatures}, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
            owner_extra_score = score_simulation.compute_new_score()[owner] - current_owners_scores[owner]
            owners_extra_score_with_all_unsaved_creatures[owner] = owner_extra_score
    simulation_scenario = [(drone.owner, [creatures[creature_idt] for creature_idt in drone.eval_unsaved_creatures_idt]) for drone in ordered_drones_from_top_to_bottom]
    owners_saved_creatures = {owner: scans[owner].saved_creatures for owner in owners}
    score_simulation = ScoreSimulation(simulation_scenario=simulation_scenario, owners_saved_creatures=owners_saved_creatures, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
    new_owners_scores = {owner: score_simulation.compute_new_score()[owner].total for owner in owners}
    state_after_saving_current_scans = score_simulation.scans_and_trophies_after_simulation()
    creatures_left_to_saved = {owner: [] for owner in owners}
    for creature in creatures.values():
        for owner in owners:
            creature_scanned_but_not_saved_by_owner = creature.idt in unsaved_creatures_idt[owner]
            if creature.kind == monster_kind:
                pass
            elif creature.escaped and (not creature_scanned_but_not_saved_by_owner):
                pass
            else:
                creatures_left_to_saved[owner].append(creature)
                if not creature_scanned_but_not_saved_by_owner:
                    score_simulation = ScoreSimulation(simulation_scenario=[(owner, [creature])], **state_after_saving_current_scans)
                    new_owner_score = score_simulation.compute_new_score()[owner].total
                    creature_extra_score = new_owner_score - new_owners_scores[owner]
                    creature.extra_scores[owner] = creature_extra_score
    state_after_winning_max_possible = {}
    creatures_left_to_win = {}
    colors_left_to_win = {}
    kinds_left_to_win = {}
    for owner in owners:
        score_simulation = ScoreSimulation(simulation_scenario=[(owner, creatures_left_to_saved[owner])], owners_saved_creatures={owner: scans[owner].saved_creatures}, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
        owners_max_possible_score[owner] = score_simulation.compute_new_score()[owner]
        state_after_winning_max_possible[owner] = score_simulation.scans_and_trophies_after_simulation()
        creatures_left_to_win[owner] = (state_after_winning_max_possible[owner]['creatures_win_by'] == owner) & (trophies.creatures_win_by != owner)
        colors_left_to_win[owner] = (state_after_winning_max_possible[owner]['colors_win_by'] == owner) & (trophies.colors_win_by != owner)
        kinds_left_to_win[owner] = (state_after_winning_max_possible[owner]['kinds_win_by'] == owner) & (trophies.kinds_win_by != owner)
    shared_creatures_left = (creatures_left_to_win[MY_OWNER] & creatures_left_to_win[FOE_OWNER]).astype(int)
    shared_colors_left = colors_left_to_win[MY_OWNER] & colors_left_to_win[FOE_OWNER]
    shared_kinds_left = kinds_left_to_win[MY_OWNER] & kinds_left_to_win[FOE_OWNER]
    bonus_shared_left = shared_creatures_left.dot(score_by_kind).sum() + score_for_full_color * shared_colors_left.size + score_for_full_kind * shared_kinds_left.size
    for owner in owners:
        owners_bonus_score_left[owner]['shared'] = bonus_shared_left
        owners_bonus_score_left[owner]['unshared'] = owners_max_possible_score[owner].bonus - bonus_shared_left - current_owners_scores[owner].bonus
    return (owners_extra_score_with_all_unsaved_creatures, owners_max_possible_score, owners_bonus_score_left)

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'game_assets', 'empty_array_saved_creatures', 'max_number_of_radar_blips_used', 'max_speed_per_kind', 'corners', 'my_owner', 'foe_owner', 'owners', 'owners_scores', 'owners_scores_computed', 'owners_extra_score_with_all_unsaved_creatures', 'owners_max_possible_score', 'owners_bonus_score_left', 'my_drones_idt_play_order', 'monsters', 'total_units_count')
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.empty_array_saved_creatures = EMPTY_ARRAY_CREATURES
        self.max_number_of_radar_blips_used = MAX_NUMBER_OF_RADAR_BLIPS_USED
        self.max_speed_per_kind = MAX_SPEED_PER_KIND
        self.corners = CORNERS
        self.my_owner = MY_OWNER
        self.foe_owner = FOE_OWNER
        self.owners = OWNERS
        self.game_assets = GameAssets()
        self.owners_scores: Dict[int, int] = {}
        self.owners_scores_computed: Dict[int, Score] = {}
        self.owners_extra_score_with_all_unsaved_creatures: Dict[int, Score] = {}
        self.owners_max_possible_score: Dict[int, Score] = {}
        self.owners_bonus_score_left: Dict[int, Dict[str, int]] = {}
        self.my_drones_idt_play_order: List[int] = []
        self.monsters: List[Creature] = []
        creature_count = int(self.get_init_input())
        for i in range(creature_count):
            creature_idt, color, kind = [int(j) for j in self.get_init_input().split()]
            creature = self.game_assets.new_asset(asset_type=AssetType.CREATURE, idt=creature_idt)
            creature.color = color
            creature.kind = kind
            creature.habitat = CREATURE_HABITATS_PER_KIND[kind]
            if creature.kind == Kind.MONSTER.value:
                self.monsters.append(creature)
            for owner in self.owners:
                scans = self.game_assets.new_asset(asset_type=AssetType.SCANS, idt=owner)
                scans.owner = owner
                scans.saved_creatures = np.zeros_like(self.empty_array_saved_creatures)
        trophies = self.game_assets.new_asset(asset_type=AssetType.TROPHIES, idt=42)
        trophies.creatures_win_by = np.zeros_like(self.empty_array_saved_creatures)
        trophies.colors_win_by = np.zeros_like(COLORS)
        trophies.kinds_win_by = np.zeros_like(KINDS)
        self.total_units_count = creature_count + 4
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
        for creature in self.game_assets.get_all(asset_type=AssetType.CREATURE).values():
            creature.visible = False
            creature.escaped = True
        self.nb_turns += 1
        self.owners_scores[self.my_owner] = int(self.get_turn_input())
        self.owners_scores[self.foe_owner] = int(self.get_turn_input())
        my_scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=self.my_owner)
        my_saved_creatures = my_scans.saved_creatures
        my_newly_saved_creatures = np.zeros_like(self.empty_array_saved_creatures)
        my_scan_count = int(self.get_turn_input())
        for i in range(my_scan_count):
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=int(self.get_turn_input()))
            creature_color, creature_kind = (creature.color, creature.kind)
            if update_saved_scans(my_saved_creatures, creature_color, creature_kind):
                my_newly_saved_creatures[creature_color, creature_kind] = self.my_owner
        foe_scans = self.game_assets.get(asset_type=AssetType.SCANS, idt=self.foe_owner)
        foe_saved_creatures = foe_scans.saved_creatures
        foe_newly_saved_creatures = np.zeros_like(self.empty_array_saved_creatures)
        foe_scan_count = int(self.get_turn_input())
        for i in range(foe_scan_count):
            creature = self.game_assets.get(asset_type=AssetType.CREATURE, idt=int(self.get_turn_input()))
            creature_color, creature_kind = (creature.color, creature.kind)
            if update_saved_scans(foe_saved_creatures, creature_color, creature_kind):
                foe_newly_saved_creatures[creature_color, creature_kind] = self.foe_owner
        update_trophies_for_all(my_saved_creatures=my_saved_creatures, foe_saved_creatures=foe_saved_creatures, my_newly_saved_creatures=my_newly_saved_creatures, foe_newly_saved_creatures=foe_newly_saved_creatures, trophies=self.game_assets.get(AssetType.TROPHIES, 42))
        my_drone_count = int(self.get_turn_input())
        self.my_drones_idt_play_order = []
        for i in range(my_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            drone = self.game_assets.get(asset_type=AssetType.MY_DRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.new_asset(asset_type=AssetType.MY_DRONE, idt=drone_idt)
            drone.x = drone_x
            drone.y = drone_y
            drone.emergency = emergency
            drone.battery = battery
            drone.unsaved_creatures_idt = set()
            self.my_drones_idt_play_order.append(drone_idt)
        foe_drone_count = int(self.get_turn_input())
        for i in range(foe_drone_count):
            drone_idt, drone_x, drone_y, emergency, battery = [int(j) for j in self.get_turn_input().split()]
            drone = self.game_assets.get(asset_type=AssetType.FOE_DRONE, idt=drone_idt)
            if drone is None:
                drone = self.game_assets.new_asset(asset_type=AssetType.FOE_DRONE, idt=drone_idt)
            drone.x = drone_x
            drone.y = drone_y
            drone.emergency = emergency
            drone.battery = battery
            drone.unsaved_creatures_idt = set()
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
            radar_blips = self.game_assets.get_all(AssetType.RADAR_BLIP)
            scans = self.game_assets.get_all(AssetType.SCANS)
            trophies = self.game_assets.get(AssetType.TROPHIES, 42)
            for owner in self.owners:
                self.owners_scores_computed[owner] = compute_score(owner=owner, saved_creatures=scans[owner].saved_creatures, creatures_win_by=trophies.creatures_win_by, colors_win_by=trophies.colors_win_by, kinds_win_by=trophies.kinds_win_by)
            self.owners_extra_score_with_all_unsaved_creatures, self.owners_max_possible_score, self.owners_bonus_score_left = evaluate_extra_scores_for_multiple_scenarios(creatures=creatures, my_drones=my_drones, foe_drones=foe_drones, scans=scans, trophies=trophies, current_owners_scores=self.owners_scores_computed)
            evaluate_positions_of_creatures(creatures=creatures, radar_blips=radar_blips, my_drones=my_drones, nb_turns=self.nb_turns)
            evaluate_monsters_to_avoid(my_drones=my_drones, monsters=self.monsters, nb_turns=self.nb_turns)
            default_action = Action(move=False, light=False)
            save_actions = save_points(my_drones=my_drones, owners_scores_computed=self.owners_scores_computed, owners_max_possible_score=self.owners_max_possible_score, owners_extra_score_with_all_unsaved_creatures=self.owners_extra_score_with_all_unsaved_creatures, owners_bonus_score_left=self.owners_bonus_score_left)
            deny_actions = deny_valuable_fish_for_foe(my_drones=my_drones, creatures=creatures, nb_turns=self.nb_turns)
            find_actions = find_valuable_target(my_drones=my_drones, creatures=creatures, total_units_count=self.total_units_count)
            just_do_something_actions = {}
            if len(deny_actions) < 2 and len(save_actions) < 2 and (len(find_actions) < 2):
                just_do_something_actions = just_do_something(my_drones=my_drones, creatures=creatures)
            actions_priorities = [deny_actions, save_actions, find_actions, just_do_something_actions]
            my_drones_action = choose_action_for_drones(my_drones=my_drones, actions_priorities=actions_priorities, default_action=default_action)
            for drone_idt in self.my_drones_idt_play_order:
                my_drone = my_drones[drone_idt]
                safe_action = avoid_monsters(my_drone, my_drones_action[drone_idt], default_action)
                my_drone.light_on = safe_action.light
                print(safe_action)
GameLoop().start()