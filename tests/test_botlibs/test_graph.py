import pytest

from botlibs.graph import Edge, create_adjacency_matrix_from_edges, AdjacencyMatrix


@pytest.mark.parametrize("edges_tuples, nodes_number", [
    ([(1, 3, True), (2, 3, True), (0, 1, True), (0, 2, True)], 4),
    ([(1, 3, True), (2, 3, False), (0, 1, True), (0, 2, False)], 4)
])
def test_create_adjacency_matrix_from_edges(edges_tuples, nodes_number):
    edges = [Edge(from_node=i, to_node=j, directed=d) for i, j, d in edges_tuples]
    adjacency_matrix = create_adjacency_matrix_from_edges(edges, nodes_number)

    assert isinstance(adjacency_matrix, AdjacencyMatrix)

    assert adjacency_matrix.array.shape == (nodes_number, nodes_number)

    for edge in edges:
        assert adjacency_matrix[edge.from_node, edge.to_node] == 1
        if edge.directed:
            assert adjacency_matrix[edge.to_node, edge.from_node] == 0
