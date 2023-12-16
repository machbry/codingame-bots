# https://en.wikipedia.org/wiki/Graph_theory

# https://en.wikipedia.org/wiki/Adjacency_list
# https://en.wikipedia.org/wiki/Adjacency_matrix
# https://en.wikipedia.org/wiki/Laplacian_matrix

# https://en.wikipedia.org/wiki/Shortest_path_problem


from typing import Iterable
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
    def sparce_matrix(self) -> csr_matrix :
        return csr_matrix(self.array)

    def __getitem__(self, key):
        return self.array.__getitem__(key)

    def __setitem__(self, key, value):
        self.array.__setitem__(key, value)


def create_adjacency_matrix_from_edges(edges: Iterable[Edge], nodes_number: int) -> AdjacencyMatrix:
    nodes_edges = np.zeros((nodes_number, nodes_number), dtype=int)
    for edge in edges:
        nodes_edges[edge.from_node, edge.to_node] = 1
        if not edge.directed:
            nodes_edges[edge.to_node, edge.from_node] = 1
    return AdjacencyMatrix(nodes_edges)
