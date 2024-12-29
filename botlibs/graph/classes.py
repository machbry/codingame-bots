# https://en.wikipedia.org/wiki/Graph_theory

# https://en.wikipedia.org/wiki/Adjacency_list
# https://en.wikipedia.org/wiki/Adjacency_matrix
# https://en.wikipedia.org/wiki/Laplacian_matrix

# https://en.wikipedia.org/wiki/Shortest_path_problem


from typing import Dict, Union, List, Optional
from dataclasses import dataclass, field

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
        i, j, w = edge.from_node, edge.to_node, edge.weight

        edges_to_add = [(i, j, w)]
        if not edge.directed:
            edges_to_add.append((j, i, w))

        for node, neighbor, weight in edges_to_add:
            if not self[node]:
                self[node] = {}
            self[node][neighbor] = weight

    def remove_edge(self, edge: Edge):
        i, j = edge.from_node, edge.to_node

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
class NodesPair:
    from_node: int = None
    to_node: int = None
    distance: float = np.inf
    shortest_path: Optional[list[int]] = None
