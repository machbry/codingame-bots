from dataclasses import dataclass, field
from typing import NamedTuple

import numpy as np

from botlibs.graph.classes import AdjacencyMatrix, Edge, AdjacencyList


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

    def connect_nodes(self, from_node: int, to_node: int, directed: bool = False):
        edge = Edge(from_node=from_node,
                    to_node=to_node,
                    directed=directed,
                    weight=1)

        self.adjacency_matrix.add_edge(edge=edge)
        self.adjacency_list.add_edge(edge=edge)

    def disconnect_nodes(self, from_node: int, to_node: int, directed: bool = False):
        edge = Edge(from_node=from_node,
                    to_node=to_node,
                    directed=directed,
                    weight=0)

        self.adjacency_matrix.remove_edge(edge=edge)
        self.adjacency_list.remove_edge(edge=edge)

    def get_node_neighbours(self, node: int):
        return set(self.adjacency_list[node].keys())


@dataclass
class Entity:
    node: int
    coordinates: Coordinates
    t: str = "EMPTY"
    owner: int = -1
    organ_id: int = 0
    organ_dir: str = "X"
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
        if entity.t in ["A", "B", "C", "D"]:
            self.proteins[entity.t].add(entity.node)
        if entity.owner == 1:
            self.my_organs.add(entity.node)
        if entity.owner == 0:
            self.opp_organs.add(entity.node)
        self.nodes.__setitem__(node, entity)

    def new_turn(self):
        self.proteins = {
            "A": set(),
            "B": set(),
            "C": set(),
            "D": set()
        }
        self.my_organs = set()
        self.opp_organs = set()
