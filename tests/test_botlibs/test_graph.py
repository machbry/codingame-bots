import numpy as np
import pytest

from botlibs.graph.algorithms import DijkstraAlgorithm
from botlibs.graph.classes import Edge, AdjacencyMatrix, AdjacencyList, NodesPair
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
    (AdjacencyList({0: {1: 1, 2: 1}, 1: {0: 1, 3: 1}, 2: {0: 1, 3: 1}, 3: {1: 1, 2: 1}}), Edge(1, 3),
     AdjacencyList({0: {1: 1, 2: 1}, 1: {0: 1}, 2: {0: 1, 3: 1}, 3: {2: 1}})),
    (AdjacencyList({0: {1: 1, 2: 1}, 1: {0: 1}, 2: {0: 1, 3: 1}, 3: {2: 1}}), Edge(1, 3),
     AdjacencyList({0: {1: 1, 2: 1}, 1: {0: 1}, 2: {0: 1, 3: 1}, 3: {2: 1}})),
    (AdjacencyList({0: {1: 1, 2: 1}, 1: {0: 1}, 2: {0: 1, 3: 1}, 3: {2: 1}}), Edge(1, 4),
     AdjacencyList({0: {1: 1, 2: 1}, 1: {0: 1}, 2: {0: 1, 3: 1}, 3: {2: 1}}))
])
def test_adjacency_list_remove_edge(adjacency_list, edge_to_remove, adjacency_list_expected):
    adjacency_list.remove_edge(edge_to_remove)

    assert adjacency_list.nodes_neighbors == adjacency_list_expected.nodes_neighbors

@pytest.mark.parametrize("adjacency_matrix, from_nodes, to_nodes, closest_pair_expected", [
    ([[0, 1, 0, 0, 0, 0],
      [1, 0, 1, 0, 0, 0],
      [0, 0, 0, 1, 0, 0],
      [0, 0, 1, 0, 1, 0],
      [1, 0, 0, 1, 0, 0],
      [0, 0, 0, 1, 0, 0]],
     [0, 1],
     [4, 5],
     NodesPair(
         from_node=1,
         to_node=4,
         distance=3,
         shortest_path=[2, 3, 4]
     )),

    ([[0, 1, 0, 0, 0, 0],
      [1, 0, 1, 0, 0, 0],
      [0, 0, 0, 1, 0, 0],
      [0, 0, 1, 0, 1, 0],
      [1, 0, 0, 1, 0, 0],
      [0, 0, 0, 1, 0, 0]],
     [0, 1, 2, 3, 4],
     [5],
     NodesPair()),

    ([[0, 1, 0, 0, 0, 0],
      [1, 0, 1, 0, 0, 0],
      [0, 0, 0, 1, 0, 0],
      [0, 0, 1, 0, 1, 0],
      [1, 0, 0, 1, 0, 0],
      [0, 0, 0, 1, 0, 0]],
     [5],
     [0, 1, 2, 3, 4],
     NodesPair(
         from_node=5,
         to_node=3,
         distance=1,
         shortest_path=[3]
     )),
])
def test_dijkstra_algorithm_find_closest_pair(adjacency_matrix, from_nodes, to_nodes, closest_pair_expected):
    # init
    dijkstra_algorithm = DijkstraAlgorithm(adjacency_matrix=AdjacencyMatrix(np.array(adjacency_matrix)))

    # act
    closest_pair = dijkstra_algorithm.find_closest_nodes_pair(
        from_nodes=from_nodes,
        to_nodes=to_nodes
    )

    # assert
    assert closest_pair == closest_pair_expected
