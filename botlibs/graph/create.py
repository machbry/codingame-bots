from typing import Iterable

import numpy as np

from botlibs.graph.classes import Edge, AdjacencyMatrix, AdjacencyList


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

