import numpy as np
import sys
from enum import Enum
from scipy.sparse import csr_matrix
from dataclasses import field, dataclass
from scipy.sparse.csgraph import dijkstra
from typing import NamedTuple, Dict, List, Union

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

class Coordinates(NamedTuple):
    x: int
    y: int

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
        for node, node_coord in enumerate(self.nodes_coordinates):
            x, y = node_coord
            if y >= 1:
                node_up = self.get_node(Coordinates(x, y - 1))
                self.connect_nodes(from_node=node, to_node=node_up)
            if x >= 1:
                node_left = self.get_node(Coordinates(x - 1, y))
                self.connect_nodes(from_node=node, to_node=node_left)
            if x < self.width - 1:
                node_right = self.get_node(Coordinates(x + 1, y))
                self.connect_nodes(from_node=node, to_node=node_right)
            if y < self.height - 1:
                node_down = self.get_node(Coordinates(x, y + 1))
                self.connect_nodes(from_node=node, to_node=node_down)

    def get_node(self, coordinates: Coordinates) -> int:
        x, y = coordinates
        return self.nodes_matrix[x, y]

    def get_node_coordinates(self, node: int):
        return self.nodes_coordinates[node]

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
    my_organs: set[int] = field(default_factory=set)
    opp_organs: set[int] = field(default_factory=set)

    def __getitem__(self, node):
        return self.nodes.__getitem__(node)

    def __setitem__(self, node, entity: Entity):
        if entity.t in ['A', 'B', 'C', 'D']:
            self.proteins[entity.t].add(entity.node)
        if entity.owner == 1:
            self.my_organs.add(entity.node)
        if entity.owner == 0:
            self.opp_organs.add(entity.node)
        self.nodes.__setitem__(node, entity)

    def new_turn(self):
        self.proteins = {'A': set(), 'B': set(), 'C': set(), 'D': set()}
        self.my_organs = set()
        self.opp_organs = set()

class DistArrayCols(Enum):
    FROM_NODE = 0
    TO_NODE = 1
    DISTANCE = 2

def compute_distances_array(from_node: int, to_nodes: set[int], predecessors: np.ndarray):
    distances_array = np.zeros(shape=(len(to_nodes), len(DistArrayCols)), dtype=float)
    distances_array[:, DistArrayCols.DISTANCE.value] = np.inf
    for i, to_node in enumerate(to_nodes):
        predecessor = to_node
        distance = 0
        while predecessor != from_node:
            next_node = predecessor
            predecessor = predecessors[from_node, next_node]
            distance += 1
            if predecessor == -9999:
                distance = np.inf
                break
        distances_array[i, DistArrayCols.FROM_NODE.value] = from_node
        distances_array[i, DistArrayCols.TO_NODE.value] = to_node
        distances_array[i, DistArrayCols.DISTANCE.value] = distance
    return distances_array

@dataclass
class Action:
    grow: bool = False
    id: int = 0
    x: int = 0
    y: int = 0
    t: str = 'BASIC'
    direction: str = None
    message: str = 'OK'

    def __repr__(self):
        if not self.grow:
            return 'WAIT'
        if not self.direction:
            return f'GROW {self.id} {self.x} {self.y} {self.t} {self.message}'
        return f'GROW {self.id} {self.x} {self.y} {self.t} {self.direction} {self.message}'

def choose_organ_and_target(my_organs: set[int], to_nodes: set[int], predecessors: np.ndarray):
    my_organ_chosen = None
    target = None
    distance_to_target = np.inf
    if len(to_nodes) > 0:
        distances_array_to_proteins = []
        for my_organ in my_organs:
            distances_array_to_proteins.append(compute_distances_array(from_node=my_organ, to_nodes=to_nodes, predecessors=predecessors))
        distances_array_to_proteins = np.concatenate(distances_array_to_proteins, axis=0)
        array = distances_array_to_proteins[distances_array_to_proteins[:, DistArrayCols.DISTANCE.value].argsort()][0, :]
        distance_to_target = array[DistArrayCols.DISTANCE.value]
        if distance_to_target < np.inf:
            my_organ_chosen = int(array[DistArrayCols.FROM_NODE.value])
            target = int(array[DistArrayCols.TO_NODE.value])
            distance_to_target = int(distance_to_target)
    return (my_organ_chosen, target, distance_to_target)

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'width', 'height', 'nb_entities', 'entities', 'my_protein_stock', 'opp_protein_stock', 'required_actions_count', 'grid')
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.nb_entities: int = 0
        self.my_protein_stock: list = []
        self.opp_protein_stock: list = []
        self.required_actions_count: int = 1
        self.grid = Grid(width=self.width, height=self.height)
        self.entities: Entities = Entities()
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
        print(self.init_inputs, file=sys.stderr, flush=True)

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
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
            node_neighbours = self.grid.get_node_neighbours(node)
            for neighbour in node_neighbours:
                if t == 'WALL':
                    self.grid.disconnect_nodes(from_node=node, to_node=neighbour)
                if t in ['ROOT', 'BASIC', 'HARVESTER']:
                    self.grid.disconnect_nodes(from_node=neighbour, to_node=node, directed=True)
        self.my_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.opp_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.required_actions_count = int(self.get_turn_input())
        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()
            proteins = set()
            for nodes in self.entities.proteins.values():
                proteins = proteins.union(nodes)
            my_organs = self.entities.my_organs
            opp_organs_free_neighbours = set()
            for node in self.entities.opp_organs:
                opp_organs_free_neighbours = opp_organs_free_neighbours.union(self.grid.get_node_neighbours(node))
            predecessors = dijkstra(self.grid.adjacency_matrix.sparce_matrix, return_predecessors=True)[1]
            for i in range(self.required_actions_count):
                t = 'BASIC'
                direction = None
                test = 'OK'
                my_organ_chosen, target, distance_to_protein = choose_organ_and_target(my_organs=my_organs, to_nodes=proteins, predecessors=predecessors)
                if target and distance_to_protein == 2 and (self.my_protein_stock[2] > 0) and (self.my_protein_stock[3] > 0):
                    t = 'HARVESTER'
                if not target:
                    my_organ_chosen, target, _ = choose_organ_and_target(my_organs=my_organs, to_nodes=opp_organs_free_neighbours, predecessors=predecessors)
                if not target:
                    test = 'NOK'
                    for my_organ in self.entities.my_organs:
                        node_neighbours = self.grid.get_node_neighbours(my_organ)
                        if len(node_neighbours) > 0:
                            my_organ_chosen, target = (my_organ, node_neighbours[0])
                            break
                if target:
                    my_organ_chosen_entity = self.entities[my_organ_chosen]
                    id = my_organ_chosen_entity.organ_id
                    predecessor = predecessors[my_organ_chosen, target]
                    next_node = target
                    while predecessor != my_organ_chosen and predecessor != -9999:
                        next_node = predecessor
                        predecessor = predecessors[my_organ_chosen, next_node]
                    x, y = self.grid.get_node_coordinates(next_node)
                    if t == 'HARVESTER':
                        x_target, y_target = self.grid.get_node_coordinates(target)
                        if x < x_target and y == y_target:
                            direction = 'E'
                        if x > x_target and y == y_target:
                            direction = 'W'
                        if x == x_target and y > y_target:
                            direction = 'N'
                        if x == x_target and y < y_target:
                            direction = 'S'
                        target_neighbours = self.grid.get_node_neighbours(target)
                        for neighbour in target_neighbours:
                            self.grid.disconnect_nodes(from_node=target, to_node=neighbour)
                    action = Action(grow=True, id=id, x=x, y=y, t=t, direction=direction, message=f'{my_organ_chosen}/{next_node}/{target}/{test}')
                else:
                    action = Action()
                print(action)
GameLoop().start()