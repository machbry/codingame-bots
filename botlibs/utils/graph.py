from typing import Iterable

import numpy as np

from botlibs.graph import Edge, AdjacencyMatrix


def create_adjacency_matrix_from_edges(edges: Iterable[Edge], nodes_number: int) -> AdjacencyMatrix:
    nodes_edges = np.zeros((nodes_number, nodes_number), dtype=int)
    for edge in edges:
        nodes_edges[edge.from_node, edge.to_node] = 1
        if not edge.directed:
            nodes_edges[edge.to_node, edge.from_node] = 1
    return AdjacencyMatrix(nodes_edges)
