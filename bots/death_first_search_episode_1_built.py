import sys
import random
import numpy as np
from scipy.sparse import csr_matrix
from dataclasses import dataclass
from typing import Dict, Union, List, Iterable, Set

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

    def __setitem__(self, key, value: int):
        self.array.__setitem__(key, value)

    def update_edge(self, edge: Edge, value: int):
        self[edge.from_node, edge.to_node] = value
        if not edge.directed:
            self[edge.to_node, edge.from_node] = value

    def add_edge(self, edge: Edge):
        self.update_edge(edge, 1)

    def remove_edge(self, edge: Edge):
        self.update_edge(edge, 0)

class AdjacencyList:

    def __init__(self, nodes_neighbors: Dict[int, Set[int]]):
        self.nodes_neighbors = nodes_neighbors

    @property
    def nodes_number(self) -> int:
        return len(self.nodes_neighbors.keys())

    def __getitem__(self, node: int) -> Union[None, Set[int]]:
        return self.nodes_neighbors.get(node)

    def __setitem__(self, node: int, value: Set[int]):
        self.nodes_neighbors[node] = value

    def add_edge(self, edge: Edge):
        (i, j) = (edge.from_node, edge.to_node)
        for (node, neighbor) in ((i, j), (j, i)):
            if not self[node]:
                self[node] = set()
            self[node].add(neighbor)

    def remove_edge(self, edge: Edge):
        (i, j) = (edge.from_node, edge.to_node)
        for (node, neighbor) in ((i, j), (j, i)):
            if self[node]:
                try:
                    self[node].remove(neighbor)
                except KeyError:
                    pass

def create_adjacency_matrix_from_edges(edges: Iterable[Edge], nodes_number: int) -> AdjacencyMatrix:
    adjacency_matrix = AdjacencyMatrix(np.zeros((nodes_number, nodes_number), dtype=int))
    for edge in edges:
        adjacency_matrix.add_edge(edge)
    return adjacency_matrix

def create_adjacency_list_from_edges(edges: Iterable[Edge]) -> AdjacencyList:
    adjacency_list = AdjacencyList({})
    for edge in edges:
        adjacency_list.add_edge(edge)
    return adjacency_list

class Link(Edge):

    def __init__(self, from_node: int, to_node: int):
        super().__init__(from_node, to_node, False, 1)

    def cut(self):
        print(f'{self.from_node} {self.to_node}')

@dataclass
class Network:
    nb_nodes: int
    links: Set[Link]
    gateways: List[int]

    def __post_init__(self):
        self.adjacency_list = create_adjacency_list_from_edges(self.links)

    def cut(self, link: Link):
        self.adjacency_list.remove_edge(link)
        link.cut()

    def get_node_neighbours(self, node):
        return self.adjacency_list[node]

class GameLoop:
    RUNNING = True

    def __init__(self):
        (n, l, e) = [int(i) for i in input().split()]
        self.init_inputs: List[str] = [f'{n} {l} {e}']
        links = set()
        for i in range(l):
            (n1, n2) = [int(j) for j in input().split()]
            self.init_inputs.append(f'{n1} {n2}')
            links.add(Link(n1, n2))
        gateways = []
        for i in range(e):
            ei = int(input())
            self.init_inputs.append(f'{ei}')
            gateways.append(ei)
        self.network = Network(nb_nodes=n, links=links, gateways=gateways)
        self.turns_inputs: List[str] = []
        print(self.init_inputs, file=sys.stderr, flush=True)

    def start(self):
        while GameLoop.RUNNING:
            si = int(input())
            self.turns_inputs.append(f'{si}')
            print(self.turns_inputs, file=sys.stderr, flush=True)
            bobnet_neighbours = self.network.get_node_neighbours(si)
            if len(bobnet_neighbours) == 1:
                self.network.cut(Link(si, bobnet_neighbours.pop()))
            else:
                gateway = random.choice(self.network.gateways)
                gateway_neighbours = self.network.get_node_neighbours(gateway)
                self.network.cut(Link(gateway, gateway_neighbours.pop()))
GameLoop().start()