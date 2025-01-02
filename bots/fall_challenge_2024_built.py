import copy
import numpy as np
import sys
from enum import Enum
from scipy.sparse import csr_matrix
from dataclasses import field, dataclass
from scipy.sparse.csgraph import dijkstra
from typing import List, Iterable, Dict, Union, Optional, NamedTuple

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

    def copy(self):
        copy_array = self.array.copy()
        return AdjacencyMatrix(nodes_edges=copy_array)

class AdjacencyList:

    def __init__(self, nodes_neighbors: Dict[int, Dict[int, float]]):
        self.nodes_neighbors = nodes_neighbors

    @property
    def nodes(self) -> List[int]:
        return list(self.nodes_neighbors.keys())

    @property
    def nodes_number(self) -> int:
        return len(self.nodes)

    def __getitem__(self, node: int) -> Union[None, Dict[int, float]]:
        return self.nodes_neighbors.get(node)

    def __setitem__(self, node: int, value: Dict[int, float]):
        self.nodes_neighbors[node] = value

    def add_edge(self, edge: Edge):
        i, j, w = (edge.from_node, edge.to_node, edge.weight)
        edges_to_add = [(i, j, w)]
        if not edge.directed:
            edges_to_add.append((j, i, w))
        for node, neighbor, weight in edges_to_add:
            if not self[node]:
                self[node] = {}
            self[node][neighbor] = weight

    def remove_edge(self, edge: Edge):
        i, j = (edge.from_node, edge.to_node)
        edges_to_remove = [(i, j)]
        if not edge.directed:
            edges_to_remove.append((j, i))
        for node, neighbor in edges_to_remove:
            if self[node]:
                try:
                    del self[node][neighbor]
                except KeyError:
                    pass

    def copy(self):
        copy_nodes_neighbors = copy.deepcopy(self.nodes_neighbors)
        return AdjacencyList(nodes_neighbors=copy_nodes_neighbors)

@dataclass
class NodesPair:
    from_node: int = None
    to_node: int = None
    distance: float = np.inf
    shortest_path: Optional[list[int]] = None

class DijkstraAlgorithm:

    def __init__(self, adjacency_matrix: AdjacencyMatrix):
        self.adjacency_matrix = adjacency_matrix
        self.dist_matrix, self.predecessors = dijkstra(self.adjacency_matrix.sparce_matrix, return_predecessors=True)

    def get_shortest_path(self, nodes_pair: NodesPair) -> Optional[list[int]]:
        distance = nodes_pair.distance
        if distance == 0 or distance == np.inf:
            return None
        from_node = nodes_pair.from_node
        to_node = nodes_pair.to_node
        shortest_path = [to_node]
        predecessor = self.predecessors[from_node, to_node]
        while predecessor != from_node and predecessor != -9999:
            next_node = predecessor
            shortest_path.insert(0, next_node)
            predecessor = self.predecessors[from_node, next_node]
        return shortest_path

    def find_closest_nodes_pair(self, from_nodes: Iterable[int], to_nodes: Iterable[int]) -> NodesPair:
        closest_pair = NodesPair()
        for to_node in to_nodes:
            for from_node in from_nodes:
                distance = self.dist_matrix[from_node, to_node]
                if distance < closest_pair.distance:
                    closest_pair.from_node = from_node
                    closest_pair.to_node = to_node
                    closest_pair.distance = int(distance)
        closest_pair.shortest_path = self.get_shortest_path(closest_pair)
        return closest_pair

class Coordinates(NamedTuple):
    x: int
    y: int

@dataclass
class ProteinStock:
    A: int = 0
    B: int = 0
    C: int = 0
    D: int = 0

    def __add__(self, other):
        return ProteinStock(A=self.A + other.A, B=self.B + other.B, C=self.C + other.C, D=self.D + other.D)

    def sum(self):
        return self.A + self.B + self.C + self.D

@dataclass
class Entity:
    node: int
    coordinates: Coordinates
    t: str = 'EMPTY'
    owner: int = -1
    organ_id: int = 0
    organ_dir: str = 'X'
    organ_parent_id: int = 0
    organ_root_id: int = 0

    def __hash__(self):
        return int(self.node)

@dataclass
class Entities:
    nodes: dict[int, Entity] = field(default_factory=dict)
    proteins: dict[str, set[int]] = field(default_factory=dict)
    my_organs_by_root: dict[int, set[int]] = field(default_factory=dict)
    opp_organs: set[int] = field(default_factory=set)
    harvested_proteins: dict[int, dict[str, set[int]]] = field(default_factory=dict)

    def __getitem__(self, node):
        if node not in self.nodes:
            return None
        return self.nodes.__getitem__(node)

    def __setitem__(self, node, entity: Entity):
        if entity.t in ['A', 'B', 'C', 'D']:
            self.proteins[entity.t].add(entity.node)
        if entity.owner == 1:
            if entity.organ_root_id not in self.my_organs_by_root:
                self.my_organs_by_root[entity.organ_root_id] = set()
            self.my_organs_by_root[entity.organ_root_id].add(entity.node)
        if entity.owner == 0:
            self.opp_organs.add(entity.node)
        self.nodes.__setitem__(node, entity)

    def new_turn(self):
        self.proteins = {'A': set(), 'B': set(), 'C': set(), 'D': set()}
        self.my_organs_by_root = {}
        self.opp_organs = set()
        self.harvested_proteins = {1: {'A': set(), 'B': set(), 'C': set(), 'D': set()}, 0: {'A': set(), 'B': set(), 'C': set(), 'D': set()}}

    def update_harvested_proteins(self, aimed_nodes_by_harvester: dict[Entity, int]):
        for harvester_entity, harvested_node in aimed_nodes_by_harvester.items():
            harvested_entity = self[harvested_node]
            if harvested_entity is not None:
                harvested_entity_type = harvested_entity.t
                if harvested_entity_type in ['A', 'B', 'C', 'D']:
                    self.harvested_proteins[harvester_entity.owner][harvested_entity_type].add(harvested_node)

    def get_wanted_proteins_for_owner(self, protein_stock: ProteinStock, max_turns_left, nb_roots: int, harvested_proteins_per_type: dict[str, set[int]]):
        wanted_types = ['A', 'B', 'C', 'D']
        wanted_proteins = set()
        for t in wanted_types:
            proteins_t = self.proteins[t]
            stock_is_not_enough = getattr(protein_stock, t) < max_turns_left * nb_roots / 2
            protein_type_still_exists = len(proteins_t) > 0
            if stock_is_not_enough and protein_type_still_exists:
                wanted_proteins = wanted_proteins.union(proteins_t)
            harvested_proteins = harvested_proteins_per_type[t]
            for harvested_protein in harvested_proteins:
                if harvested_protein in wanted_proteins:
                    wanted_proteins.remove(harvested_protein)
        return wanted_proteins

@dataclass
class NodeFrontier:
    node: int
    north: int = None
    south: int = None
    east: int = None
    west: int = None

    @property
    def cardinal_nodes(self):
        all_nodes = [self.north, self.south, self.east, self.west]
        existing_nodes = set()
        for node in all_nodes:
            if node is not None:
                existing_nodes.add(node)
        return existing_nodes

    @property
    def nodes_by_direction(self):
        return {'N': self.north, 'S': self.south, 'E': self.east, 'W': self.west}

@dataclass
class Grid:
    width: int
    height: int
    nb_nodes: int = field(init=False)
    nodes_coordinates: list[Coordinates] = field(init=False)
    nodes_matrix: np.ndarray = field(init=False)
    adjacency_matrix: AdjacencyMatrix = field(init=False)
    adjacency_list: AdjacencyList = field(init=False)
    initial_adjacency_matrix: AdjacencyMatrix = field(init=False)
    initial_adjacency_list: AdjacencyList = field(init=False)

    def __post_init__(self):
        self.nb_nodes = self.width * self.height
        self.nodes_coordinates = []
        self.nodes_matrix = np.zeros(shape=(self.width, self.height), dtype=int)
        for node in range(self.nb_nodes):
            x = node % self.width
            y = node // self.width
            self.nodes_coordinates.append(Coordinates(x=x, y=y))
            self.nodes_matrix[x, y] = node
        self.adjacency_matrix = AdjacencyMatrix(np.zeros((self.nb_nodes, self.nb_nodes), dtype=int))
        self.adjacency_list = AdjacencyList({})
        for node in range(self.nb_nodes):
            cardinal_nodes = self.get_node_frontier(node).cardinal_nodes
            for cardinal_node in cardinal_nodes:
                self.connect_nodes(from_node=node, to_node=cardinal_node)
        self.initial_adjacency_matrix = self.adjacency_matrix.copy()
        self.initial_adjacency_list = self.adjacency_list.copy()

    def new_turn(self):
        self.adjacency_matrix = self.initial_adjacency_matrix.copy()
        self.adjacency_list = self.initial_adjacency_list.copy()

    def get_node(self, coordinates: Coordinates) -> int:
        x, y = coordinates
        return self.nodes_matrix[x, y]

    def get_node_coordinates(self, node: int):
        return self.nodes_coordinates[node]

    def get_node_frontier(self, node: int):
        node_frontier = NodeFrontier(node)
        x, y = self.get_node_coordinates(node)
        if y >= 1:
            node_north = self.get_node(Coordinates(x, y - 1))
            node_frontier.north = node_north
        if x >= 1:
            node_west = self.get_node(Coordinates(x - 1, y))
            node_frontier.west = node_west
        if x < self.width - 1:
            node_east = self.get_node(Coordinates(x + 1, y))
            node_frontier.east = node_east
        if y < self.height - 1:
            node_south = self.get_node(Coordinates(x, y + 1))
            node_frontier.south = node_south
        return node_frontier

    def connect_nodes(self, from_node: int, to_node: int, directed: bool=False, weight: float=1):
        edge = Edge(from_node=from_node, to_node=to_node, directed=directed, weight=weight)
        self.adjacency_matrix.add_edge(edge=edge)
        self.adjacency_list.add_edge(edge=edge)

    def disconnect_nodes(self, from_node: int, to_node: int, directed: bool=False):
        edge = Edge(from_node=from_node, to_node=to_node, directed=directed, weight=0)
        self.adjacency_matrix.remove_edge(edge=edge)
        self.adjacency_list.remove_edge(edge=edge)

    def get_node_neighbours(self, node: int):
        return set(self.adjacency_list[node].keys())

    def update_weight_toward_node(self, node: int, weight: float):
        cardinal_nodes = self.get_node_frontier(node).cardinal_nodes
        for cardinal in cardinal_nodes:
            if node in self.get_node_neighbours(cardinal):
                self.connect_nodes(from_node=cardinal, to_node=node, directed=True, weight=weight)

def get_direction(from_coordinates: Coordinates, to_coordinates: Coordinates):
    diff_x = to_coordinates.x - from_coordinates.x
    diff_y = to_coordinates.y - from_coordinates.y
    if abs(diff_y) >= abs(diff_x):
        if diff_y > 0:
            return 'S'
        return 'N'
    if diff_x > 0:
        return 'E'
    return 'W'

class Objective(Enum):
    PROTEINS = 'PROTEINS'
    REPRODUCTION = 'REPRODUCTION'
    ATTACK = 'ATTACK'
    DEFAULT = 'DEFAULT'
    WAIT = 'WAIT'

class Strategy(NamedTuple):
    name: str = 'Wait'
    objective: Objective = Objective.WAIT
    targets: set[int] = set()
    priority: float = np.inf

    def __hash__(self):
        return hash((self.objective.value, *self.targets, self.priority))

@dataclass
class Action:
    grow: bool = False
    spore: bool = False
    id: int = 0
    x: int = 0
    y: int = 0
    t: str = 'BASIC'
    direction: str = None
    message: str = ''
    value: float = -np.inf

    def __repr__(self):
        if not self.grow and (not self.spore):
            return 'WAIT'
        if self.spore:
            return f'SPORE {self.id} {self.x} {self.y}'
        if not self.direction:
            return f'GROW {self.id} {self.x} {self.y} {self.t} {self.message}'
        return f'GROW {self.id} {self.x} {self.y} {self.t} {self.direction} {self.message}'

    @property
    def cost(self):
        if self.grow:
            if self.t == 'BASIC':
                return ProteinStock(A=-1)
            if self.t == 'HARVESTER':
                return ProteinStock(C=-1, D=-1)
            if self.t == 'TENTACLE':
                return ProteinStock(B=-1, C=-1)
            if self.t == 'SPORER':
                return ProteinStock(B=-1, D=-1)
        if self.spore:
            return ProteinStock(A=-1, B=-1, C=-1, D=-1)
        return ProteinStock()

def wait_action_with_message(message: str):
    action = Action()
    action.message = message
    return action

def can_grow_basic(protein_stock: ProteinStock):
    return protein_stock.A > 0

def can_grow_sporer(protein_stock: ProteinStock):
    return protein_stock.B > 0 and protein_stock.D > 0

def can_grow_harvester(protein_stock: ProteinStock):
    return protein_stock.C > 0 and protein_stock.D > 0

def can_grow_tentacle(protein_stock: ProteinStock):
    return protein_stock.B > 0 and protein_stock.C > 0

def define_grow_type(possible_grow_types: dict[str, bool], grow_types_priority: list[str]):
    for t in grow_types_priority:
        if possible_grow_types[t]:
            return t

def next_action_to_reach_target(nodes_pair: NodesPair, objective: Objective, protein_stock: ProteinStock, entities: Entities, grid: Grid, **kwargs):
    from_node = nodes_pair.from_node
    to_node = nodes_pair.to_node
    distance = nodes_pair.distance
    shortest_path = nodes_pair.shortest_path
    if distance == np.inf or len(shortest_path) == 0:
        return wait_action_with_message('No targets accessible')
    from_organ = entities[from_node]
    next_node = shortest_path[0]
    x, y = grid.get_node_coordinates(next_node)
    action = Action(id=from_organ.organ_id, x=x, y=y, message=f'{from_node}/{next_node}/{to_node}')
    possible_grow_types = {'BASIC': can_grow_basic(protein_stock=protein_stock), 'TENTACLE': can_grow_tentacle(protein_stock=protein_stock), 'SPORER': can_grow_sporer(protein_stock=protein_stock), 'HARVESTER': can_grow_harvester(protein_stock=protein_stock)}
    if True not in possible_grow_types.values():
        return wait_action_with_message('Not enough proteins to grow or spore')
    if objective == Objective.PROTEINS:
        if distance == 2:
            action.t = 'HARVESTER'
            action.grow = True
        else:
            action.t = 'BASIC'
            action.grow = True
    if objective == Objective.ATTACK:
        if distance == 1:
            action.t = 'TENTACLE'
            action.grow = True
        else:
            action.t = 'BASIC'
            action.grow = True
    if objective == Objective.DEFAULT:
        grow_types_priority = ['BASIC', 'TENTACLE', 'HARVESTER', 'SPORER']
        action.t = define_grow_type(possible_grow_types=possible_grow_types, grow_types_priority=grow_types_priority)
        action.grow = True
    if not possible_grow_types[action.t]:
        return wait_action_with_message(f'Not enough proteins for {objective.value}: {action.t}')
    if action.t in ['HARVESTER', 'TENTACLE', 'SPORER']:
        if 'real_target' in kwargs:
            from_coord = Coordinates(x=action.x, y=action.y)
            to_coord = grid.get_node_coordinates(kwargs['real_target'])
        else:
            from_coord = Coordinates(x=action.x, y=action.y)
            to_coord = grid.get_node_coordinates(to_node)
        action.direction = get_direction(from_coordinates=from_coord, to_coordinates=to_coord)
    action.value = -distance - action.cost.sum()
    return action

def choose_best_actions(actions_by_strategy: dict[Strategy, Action]):
    best_strategy = Strategy()
    best_action = Action()
    for strategy, action in actions_by_strategy.items():
        if strategy.priority <= best_strategy.priority:
            if action.value > best_action.value:
                best_strategy = strategy
                best_action = action
    return (best_strategy, best_action)

def log(message):
    print(message, file=sys.stderr, flush=True)

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'width', 'height', 'nb_entities', 'entities', 'my_protein_stock', 'opp_protein_stock', 'required_actions_count', 'grid', 'create_new_root', 'actions')
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.actions: list[str] = []
        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.nb_entities: int = 0
        self.my_protein_stock: ProteinStock = ProteinStock()
        self.opp_protein_stock: ProteinStock = ProteinStock()
        self.required_actions_count: int = 1
        self.grid = Grid(width=self.width, height=self.height)
        self.entities: Entities = Entities()
        self.create_new_root: bool = False
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
        self.nb_entities = int(self.get_turn_input())
        self.entities.new_turn()
        self.grid.new_turn()
        aimed_nodes_by_harvester = {}
        for i in range(self.nb_entities):
            inputs = self.get_turn_input().split()
            coordinates = Coordinates(x=int(inputs[0]), y=int(inputs[1]))
            t = inputs[2]
            owner = int(inputs[3])
            organ_id = int(inputs[4])
            organ_dir = inputs[5]
            organ_parent_id = int(inputs[6])
            organ_root_id = int(inputs[7])
            node = self.grid.get_node(coordinates)
            entity = Entity(node=node, coordinates=coordinates, t=t, owner=owner, organ_id=organ_id, organ_dir=organ_dir, organ_parent_id=organ_parent_id, organ_root_id=organ_root_id)
            self.entities[node] = entity
            frontier_nodes = self.grid.get_node_frontier(node)
            cardinal_nodes = frontier_nodes.cardinal_nodes
            for cardinal in cardinal_nodes:
                if t == 'WALL':
                    self.grid.disconnect_nodes(from_node=node, to_node=cardinal)
                if t in ['ROOT', 'BASIC', 'HARVESTER', 'TENTACLE', 'SPORER']:
                    self.grid.disconnect_nodes(from_node=cardinal, to_node=node, directed=True)
            if t == 'HARVESTER':
                harvested_node = frontier_nodes.nodes_by_direction[organ_dir]
                if harvested_node is not None:
                    aimed_nodes_by_harvester[entity] = harvested_node
            if t == 'TENTACLE' and owner == 0:
                node_attacked = frontier_nodes.nodes_by_direction[organ_dir]
                if node_attacked is not None:
                    cardinals_attacked = self.grid.get_node_frontier(node_attacked).cardinal_nodes
                    for cardinal in cardinals_attacked:
                        self.grid.disconnect_nodes(from_node=cardinal, to_node=node_attacked, directed=True)
        self.entities.update_harvested_proteins(aimed_nodes_by_harvester=aimed_nodes_by_harvester)
        my_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.my_protein_stock.A = my_protein_stock[0]
        self.my_protein_stock.B = my_protein_stock[1]
        self.my_protein_stock.C = my_protein_stock[2]
        self.my_protein_stock.D = my_protein_stock[3]
        opp_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.opp_protein_stock.A = opp_protein_stock[0]
        self.opp_protein_stock.B = opp_protein_stock[1]
        self.opp_protein_stock.C = opp_protein_stock[2]
        self.opp_protein_stock.D = opp_protein_stock[3]
        self.required_actions_count = int(self.get_turn_input())
        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()
            my_organs_by_root = self.entities.my_organs_by_root
            my_harvested_proteins_per_type = self.entities.harvested_proteins[1]
            for protein_type, harvested_nodes in my_harvested_proteins_per_type.items():
                for harvested_node in harvested_nodes:
                    weight = max(self.grid.nb_nodes - getattr(self.my_protein_stock, protein_type), 1)
                    self.grid.update_weight_toward_node(node=harvested_node, weight=weight)
            my_wanted_proteins = self.entities.get_wanted_proteins_for_owner(protein_stock=self.my_protein_stock, max_turns_left=100 - self.nb_turns, nb_roots=len(my_organs_by_root), harvested_proteins_per_type=my_harvested_proteins_per_type)
            neighbours_opp_organs = {}
            for opp_organ in self.entities.opp_organs:
                neighbours = self.grid.get_node_neighbours(opp_organ)
                for neighbour in neighbours:
                    neighbours_opp_organs[neighbour] = opp_organ
            dijkstra_algorithm = DijkstraAlgorithm(adjacency_matrix=self.grid.adjacency_matrix)
            for my_root_id, my_organs in my_organs_by_root.items():
                organs_neighbours = set()
                for organ in my_organs:
                    organs_neighbours = organs_neighbours.union(self.grid.get_node_neighbours(organ))
                strategies = [Strategy(name='target_wanted_proteins', objective=Objective.PROTEINS, targets=my_wanted_proteins, priority=0), Strategy(name='attack_opponent', objective=Objective.ATTACK, targets=set(neighbours_opp_organs.keys()), priority=0), Strategy(name='target_proteins', objective=Objective.PROTEINS, targets=set.union(*self.entities.proteins.values()), priority=1), Strategy(name='default', objective=Objective.DEFAULT, targets=organs_neighbours, priority=2)]
                actions_by_strategy = {}
                for strategy in strategies:
                    closest_organ_target_pair = dijkstra_algorithm.find_closest_nodes_pair(from_nodes=my_organs, to_nodes=strategy.targets)
                    kwargs = {}
                    to_node = closest_organ_target_pair.to_node
                    if to_node is not None and strategy.objective == Objective.ATTACK:
                        opp_organ_neighbour = closest_organ_target_pair.to_node
                        kwargs['real_target'] = neighbours_opp_organs[opp_organ_neighbour]
                    action = next_action_to_reach_target(nodes_pair=closest_organ_target_pair, objective=strategy.objective, protein_stock=self.my_protein_stock, entities=self.entities, grid=self.grid, **kwargs)
                    actions_by_strategy[strategy] = action
                strategy, action = choose_best_actions(actions_by_strategy=actions_by_strategy)
                self.my_protein_stock = self.my_protein_stock + action.cost
                action.message = f'{strategy.name}/{action.message}'
                print(action)
GameLoop().start()