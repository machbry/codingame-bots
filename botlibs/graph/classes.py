# https://en.wikipedia.org/wiki/Graph_theory

# https://en.wikipedia.org/wiki/Adjacency_list
# https://en.wikipedia.org/wiki/Adjacency_matrix
# https://en.wikipedia.org/wiki/Laplacian_matrix

# https://en.wikipedia.org/wiki/Shortest_path_problem


from typing import Dict, Set, Union
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix


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
        i, j = edge.from_node, edge.to_node
        for node, neighbor in ((i, j), (j, i)):
            if not self[node]:
                self[node] = set()
            self[node].add(neighbor)

    def remove_edge(self, edge: Edge):
        i, j = edge.from_node, edge.to_node
        for node, neighbor in ((i, j), (j, i)):
            if self[node]:
                try:
                    self[node].remove(neighbor)
                except KeyError:
                    pass
