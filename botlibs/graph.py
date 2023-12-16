# https://en.wikipedia.org/wiki/Graph_theory

# https://en.wikipedia.org/wiki/Adjacency_list
# https://en.wikipedia.org/wiki/Adjacency_matrix
# https://en.wikipedia.org/wiki/Laplacian_matrix

# https://en.wikipedia.org/wiki/Shortest_path_problem


from typing import Iterable, Dict, Set
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

