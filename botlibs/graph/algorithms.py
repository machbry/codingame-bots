from typing import Optional

import numpy as np
from scipy.sparse.csgraph import dijkstra

from botlibs.graph.classes import AdjacencyMatrix, NodesPair


class DijkstraAlgorithm:
    def __init__(self, adjacency_matrix: AdjacencyMatrix):
        self.adjacency_matrix = adjacency_matrix
        self.dist_matrix, self.predecessors = dijkstra(
            self.adjacency_matrix.sparce_matrix,
            return_predecessors=True
        )

    def get_shortest_path(self, nodes_pair: NodesPair) -> Optional[list[int]]:
        distance = nodes_pair.distance
        if distance == 0 or distance == np.inf:
            return None

        from_node = nodes_pair.from_node
        to_node = nodes_pair.to_node

        shortest_path = [to_node]
        predecessor = self.predecessors[from_node, to_node]
        while predecessor != from_node and predecessor != -9999:
            next_node = predecessor
            shortest_path.insert(0, next_node)
            predecessor = self.predecessors[from_node, next_node]

        return shortest_path

    def find_closest_nodes_pair(self, from_nodes: list[int], to_nodes: list[int]) -> NodesPair:
        closest_pair = NodesPair()

        for to_node in to_nodes:
            for from_node in from_nodes:
                distance = self.dist_matrix[from_node, to_node]

                if distance < closest_pair.distance:
                    closest_pair.from_node = from_node
                    closest_pair.to_node = to_node
                    closest_pair.distance = int(distance)

        closest_pair.shortest_path = self.get_shortest_path(closest_pair)

        return closest_pair

