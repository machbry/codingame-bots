import numpy as np
import sys
from scipy.sparse import csr_matrix
from dataclasses import dataclass, field
from scipy.sparse.csgraph import dijkstra
from typing import List, Union, NamedTuple, Dict

class Coordinates(NamedTuple):
    x: int
    y: int

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

@dataclass
class Entities:
    nodes: dict[int, Entity] = field(default_factory=dict)
    proteins: dict[str, set[int]] = field(default_factory=dict)
    my_organs_by_root: dict[int, set[int]] = field(default_factory=dict)
    opp_organs: set[int] = field(default_factory=set)
    harvested_proteins: dict[str, set[int]] = field(default_factory=dict)

    def __post_init__(self):
        self.harvested_proteins = {'A': set(), 'B': set(), 'C': set(), 'D': set()}

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

@dataclass
class ProteinStock:
    A: int = 0
    B: int = 0
    C: int = 0
    D: int = 0

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

@dataclass
class Grid:
    width: int
    height: int
    nb_nodes: int = field(init=False)
    nodes_coordinates: list[Coordinates] = field(init=False)
    nodes_matrix: np.ndarray = field(init=False)
    adjacency_matrix: AdjacencyMatrix = field(init=False)

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

    def connect_nodes(self, from_node: int, to_node: int, directed: bool=False):
        edge = Edge(from_node=from_node, to_node=to_node, directed=directed, weight=1)
        self.adjacency_matrix.add_edge(edge=edge)
        self.adjacency_list.add_edge(edge=edge)

    def disconnect_nodes(self, from_node: int, to_node: int, directed: bool=False):
        edge = Edge(from_node=from_node, to_node=to_node, directed=directed, weight=0)
        self.adjacency_matrix.remove_edge(edge=edge)
        self.adjacency_list.remove_edge(edge=edge)

    def get_node_neighbours(self, node: int):
        return set(self.adjacency_list[node].keys())

def is_aligned(from_coord: Coordinates, from_direction: str, to_coord: Coordinates):
    if from_direction == 'N':
        return from_coord.x == to_coord.x and from_coord.y > to_coord.y
    if from_direction == 'S':
        return from_coord.x == to_coord.x and from_coord.y < to_coord.y
    if from_direction == 'E':
        return from_coord.y == to_coord.y and from_coord.x < to_coord.x
    if from_direction == 'W':
        return from_coord.y == to_coord.y and from_coord.x > to_coord.x
    return False

@dataclass
class Action:
    grow: bool = False
    spore: bool = False
    id: int = 0
    x: int = 0
    y: int = 0
    t: str = 'BASIC'
    direction: str = None
    message: str = 'OK'

    def __repr__(self):
        if not self.grow and (not self.spore):
            return 'WAIT'
        if self.spore:
            return f'SPORE {self.id} {self.x} {self.y}'
        if not self.direction:
            return f'GROW {self.id} {self.x} {self.y} {self.t} {self.message}'
        return f'GROW {self.id} {self.x} {self.y} {self.t} {self.direction} {self.message}'

def choose_closest_organ_and_target(my_organs: set[int], to_nodes: set[int], dist_matrix: np.ndarray):
    my_organ_chosen = None
    target = None
    distance_to_target = np.inf
    for to_node in to_nodes:
        for my_organ in my_organs:
            distance = dist_matrix[my_organ, to_node]
            if distance < distance_to_target:
                my_organ_chosen = my_organ
                target = to_node
                distance_to_target = int(distance)
    return (my_organ_chosen, target, distance_to_target)

def can_create_new_root(protein_stock: ProteinStock):
    return all((resource > 0 for resource in [protein_stock.A, protein_stock.B, protein_stock.C, protein_stock.D]))

def can_use_sporer(protein_stock: ProteinStock, distance_to_target: int):
    return distance_to_target > protein_stock.A > 1 and protein_stock.B > 1 and (protein_stock.C > 0) and protein_stock.D

def can_use_harvester(protein_stock: ProteinStock, distance_to_target: int):
    return distance_to_target == 2 and protein_stock.C > 0 and (protein_stock.D > 0)

def can_use_tentacle(protein_stock: ProteinStock, distance_to_target: int):
    return distance_to_target == 1 and protein_stock.B > 0 and (protein_stock.C > 0)

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
            cardinal_nodes = self.grid.get_node_frontier(node).cardinal_nodes
            for cardinal in cardinal_nodes:
                if t == 'WALL':
                    self.grid.disconnect_nodes(from_node=node, to_node=cardinal)
                if t in ['ROOT', 'BASIC', 'HARVESTER', 'TENTACLE', 'SPORER']:
                    self.grid.disconnect_nodes(from_node=cardinal, to_node=node, directed=True)
        my_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.my_protein_stock.A = my_protein_stock[0]
        self.my_protein_stock.B = my_protein_stock[1]
        self.my_protein_stock.C = my_protein_stock[2]
        self.my_protein_stock.D = my_protein_stock[3]
        opp_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.opp_protein_stock.A = my_protein_stock[0]
        self.opp_protein_stock.B = my_protein_stock[1]
        self.opp_protein_stock.C = my_protein_stock[2]
        self.opp_protein_stock.D = my_protein_stock[3]
        self.required_actions_count = int(self.get_turn_input())
        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()
            proteins = set.union(*self.entities.proteins.values())
            my_organs_by_root = self.entities.my_organs_by_root
            opp_organs_free_neighbours = {neighbour: node for node in self.entities.opp_organs for neighbour in self.grid.get_node_neighbours(node)}
            dist_matrix, predecessors = dijkstra(self.grid.adjacency_matrix.sparce_matrix, return_predecessors=True)
            for my_root_id, my_organs in my_organs_by_root.items():
                grow = True
                spore = False
                grow_type = 'BASIC'
                direction = None
                my_organ_chosen, target, distance_to_protein = choose_closest_organ_and_target(my_organs=my_organs, to_nodes=proteins, dist_matrix=dist_matrix)
                if target is not None and self.create_new_root and can_create_new_root(self.my_protein_stock):
                    self.create_new_root = False
                    grow = False
                    spore = True
                    grow_type = None
                if target is not None and can_use_sporer(self.my_protein_stock, distance_to_protein) and (not spore):
                    grow_type = 'SPORER'
                    self.create_new_root = True
                if target is not None and can_use_harvester(self.my_protein_stock, distance_to_protein) and (not spore):
                    grow_type = 'HARVESTER'
                if target is None:
                    my_organ_chosen, target, distance_to_opp_neighbour = choose_closest_organ_and_target(my_organs=my_organs, to_nodes=set(opp_organs_free_neighbours.keys()), dist_matrix=dist_matrix)
                    if target is not None and can_use_tentacle(self.my_protein_stock, distance_to_opp_neighbour):
                        grow_type = 'TENTACLE'
                if target is None:
                    nb_t_max = 0
                    for t in ['D', 'C', 'B', 'A']:
                        harvested_nodes = self.entities.harvested_proteins[t]
                        nb_t = len(harvested_nodes)
                        if nb_t <= nb_t_max:
                            continue
                        for h in harvested_nodes:
                            cardinals = self.grid.get_node_frontier(h).cardinal_nodes
                            my_organs_neighbour = [org for org in my_organs if org in cardinals]
                            if len(my_organs_neighbour) > 0:
                                my_organ_chosen = my_organs_neighbour[0]
                                target = h
                                nb_t_max = nb_t
                                self.entities.harvested_proteins[t].remove(target)
                                break
                if target is None:
                    for my_organ in my_organs:
                        node_neighbours = list(self.grid.get_node_neighbours(my_organ))
                        if len(node_neighbours) > 0:
                            my_organ_chosen, target = (my_organ, node_neighbours[0])
                            break
                if target is not None:
                    my_organ_chosen_entity = self.entities[my_organ_chosen]
                    id = my_organ_chosen_entity.organ_id
                    next_node = target
                    if grow:
                        predecessor = predecessors[my_organ_chosen, target]
                        while predecessor != my_organ_chosen and predecessor != -9999:
                            next_node = predecessor
                            predecessor = predecessors[my_organ_chosen, next_node]
                    if spore:
                        from_organ_coordinates = my_organ_chosen_entity.coordinates
                        from_organ_direction = my_organ_chosen_entity.organ_dir
                        aligned = is_aligned(from_coord=from_organ_coordinates, from_direction=from_organ_direction, to_coord=self.grid.get_node_coordinates(next_node))
                        predecessor = predecessors[my_organ_chosen, target]
                        while not (dist_matrix[next_node, target] > 1 and aligned) and predecessor != my_organ_chosen and (predecessor != -9999):
                            next_node = predecessor
                            aligned = is_aligned(from_coord=from_organ_coordinates, from_direction=from_organ_direction, to_coord=self.grid.get_node_coordinates(next_node))
                            predecessor = predecessors[my_organ_chosen, next_node]
                    x, y = self.grid.get_node_coordinates(next_node)
                    if grow_type == 'TENTACLE':
                        target = opp_organs_free_neighbours[target]
                    if grow_type == 'SPORER':
                        target = predecessors[my_organ_chosen, target]
                    if grow_type in ['TENTACLE', 'HARVESTER', 'SPORER']:
                        x_target, y_target = self.grid.get_node_coordinates(target)
                        diff_x = x_target - x
                        diff_y = y_target - y
                        if abs(diff_y) >= abs(diff_x):
                            direction = 'N'
                            if diff_y > 0:
                                direction = 'S'
                        else:
                            direction = 'W'
                            if diff_x > 0:
                                direction = 'E'
                        if grow_type == 'HARVESTER':
                            target_entity = self.entities[target]
                            self.entities.harvested_proteins[target_entity.t].add(target)
                            target_cardinals = self.grid.get_node_frontier(target).cardinal_nodes
                            for cardinal in target_cardinals:
                                self.grid.disconnect_nodes(from_node=cardinal, to_node=target, directed=True)
                        if grow_type == 'TENTACLE':
                            self.grid.connect_nodes(from_node=next_node, to_node=target, directed=True)
                    if grow_type == 'BASIC' and self.my_protein_stock.A == 0 and (self.my_protein_stock.B > 0) and (self.my_protein_stock.C > 0):
                        grow_type = 'TENTACLE'
                    action = Action(grow=grow, spore=spore, id=id, x=x, y=y, t=grow_type, direction=direction, message=f'{my_organ_chosen}/{next_node}/{target}')
                else:
                    action = Action()
                if action.grow and action.id == 59:
                    pass
                self.actions.append(str(action))
                print(action)
        return self.actions
GameLoop().start()