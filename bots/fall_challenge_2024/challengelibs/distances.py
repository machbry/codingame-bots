from enum import Enum

import numpy as np


class DistArrayCols(Enum):
    FROM_NODE = 0
    TO_NODE = 1
    DISTANCE = 2


def compute_distances_array(from_node: int, to_nodes: set[int], predecessors: np.ndarray):

    distances_array = np.zeros(shape=(len(to_nodes), len(DistArrayCols)), dtype=float)
    distances_array[:, DistArrayCols.DISTANCE.value] = np.inf

    for i, to_node in enumerate(to_nodes):
        predecessor = to_node
        distance = 0

        while predecessor != from_node:
            next_node = predecessor
            predecessor = predecessors[from_node, next_node]
            distance += 1
            if predecessor == -9999:
                distance = np.inf
                break

        distances_array[i, DistArrayCols.FROM_NODE.value] = from_node
        distances_array[i, DistArrayCols.TO_NODE.value] = to_node
        distances_array[i, DistArrayCols.DISTANCE.value] = distance

    return distances_array
