from dataclasses import dataclass, field

import numpy as np

from botlibs.graph.classes import AdjacencyMatrix, AdjacencyList, Edge
from bots.fall_challenge_2024.challengelibs.assets import Coordinates


@dataclass
class NodeFrontier:
    node: int
    north: int = None
    south: int = None
    east: int = None
    west: int = None

    @property
    def cardinal_nodes(self):
        all_nodes = [
            self.north,
            self.south,
            self.east,
            self.west
        ]

        existing_nodes = set()
        for node in all_nodes:
            if node is not None:
                existing_nodes.add(node)

        return existing_nodes

    @property
    def nodes_by_direction(self):
        return {
            "N": self.north,
            "S": self.south,
            "E": self.east,
            "W": self.west
        }


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

    def connect_nodes(self, from_node: int, to_node: int, directed: bool = False, weight: float = 1):
        edge = Edge(from_node=from_node,
                    to_node=to_node,
                    directed=directed,
                    weight=weight)

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

    def update_weight_toward_node(self, node: int, weight: float):
        cardinal_nodes = self.get_node_frontier(node).cardinal_nodes
        for cardinal in cardinal_nodes:
            if node in self.get_node_neighbours(cardinal):
                self.connect_nodes(
                    from_node=cardinal,
                    to_node=node,
                    directed=True,
                    weight=weight
                )


def get_direction(from_coordinates: Coordinates, to_coordinates: Coordinates):
    diff_x = to_coordinates.x - from_coordinates.x
    diff_y = to_coordinates.y - from_coordinates.y
    if abs(diff_y) >= abs(diff_x):
        if diff_y > 0:
            return "S"
        return "N"
    if diff_x > 0:
        return "E"
    return "W"


def is_aligned(from_coord: Coordinates, from_direction: str, to_coord: Coordinates):
    if from_direction == "N":
        return from_coord.x == to_coord.x and from_coord.y > to_coord.y
    if from_direction == "S":
        return from_coord.x == to_coord.x and from_coord.y < to_coord.y
    if from_direction == "E":
        return from_coord.y == to_coord.y and from_coord.x < to_coord.x
    if from_direction == "W":
        return from_coord.y == to_coord.y and from_coord.x > to_coord.x

    return False
