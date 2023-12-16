import pytest

from botlibs.graph.classes import Edge, AdjacencyMatrix, AdjacencyList
from botlibs.graph.create import create_adjacency_matrix_from_edges, create_adjacency_list_from_edges


@pytest.mark.parametrize("edges, nodes_number", [
    ([Edge(1, 3, True), Edge(2, 3, True), Edge(0, 1, True), Edge(0, 2, True)], 4),
    ([Edge(1, 3, True), Edge(2, 3, False), Edge(0, 1, True), Edge(0, 2, False)], 4)
])
def test_create_adjacency_matrix_from_edges(edges, nodes_number):
    adjacency_matrix = create_adjacency_matrix_from_edges(edges, nodes_number)

    assert isinstance(adjacency_matrix, AdjacencyMatrix)

    assert adjacency_matrix.array.shape == (nodes_number, nodes_number)

    for edge in edges:
        assert adjacency_matrix[edge.from_node, edge.to_node] == 1
        if edge.directed:
            assert adjacency_matrix[edge.to_node, edge.from_node] == 0


@pytest.mark.parametrize("edges, nodes_number_expected", [
    ([Edge(1, 3), Edge(2, 3), Edge(0, 1), Edge(0, 2)], 4)
])
def test_create_adjacency_list_from_edges(edges, nodes_number_expected):
    adjacency_list = create_adjacency_list_from_edges(edges)

    assert isinstance(adjacency_list, AdjacencyList)

    assert adjacency_list.nodes_number == nodes_number_expected

    for edge in edges:
        i, j = edge.from_node, edge.to_node
        assert j in adjacency_list[i]
        assert i in adjacency_list[j]


@pytest.mark.parametrize("adjacency_list, edge_to_remove, adjacency_list_expected", [
    (AdjacencyList({0: {1, 2}, 1: {0, 3}, 2: {0, 3}, 3: {1, 2}}), Edge(1, 3), AdjacencyList({0: {1, 2}, 1: {0}, 2: {0, 3}, 3: {2}})),
    (AdjacencyList({0: {1, 2}, 1: {0}, 2: {0, 3}, 3: {2}}), Edge(1, 3), AdjacencyList({0: {1, 2}, 1: {0}, 2: {0, 3}, 3: {2}})),
    (AdjacencyList({0: {1, 2}, 1: {0}, 2: {0, 3}, 3: {2}}), Edge(1, 4), AdjacencyList({0: {1, 2}, 1: {0}, 2: {0, 3}, 3: {2}}))
])
def test_adjacency_list_remove_edge(adjacency_list, edge_to_remove, adjacency_list_expected):
    adjacency_list.remove_edge(edge_to_remove)

    assert adjacency_list.nodes_neighbors == adjacency_list_expected.nodes_neighbors
