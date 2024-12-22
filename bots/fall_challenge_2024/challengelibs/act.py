from dataclasses import dataclass

import numpy as np

from bots.fall_challenge_2024.challengelibs.geometry import compute_distances_array, DistArrayCols


@dataclass
class Action:
    grow: bool = False
    id: int = 0
    x: int = 0
    y: int = 0
    t: str = "BASIC"
    direction: str = None
    message: str = "OK"

    def __repr__(self):
        if not self.grow:
            return "WAIT"

        if not self.direction:
            return f"GROW {self.id} {self.x} {self.y} {self.t} {self.message}"

        return f"GROW {self.id} {self.x} {self.y} {self.t} {self.direction} {self.message}"


def choose_organ_and_target(my_organs: set[int], to_nodes: set[int], predecessors: np.ndarray):
    my_organ_chosen = None
    target = None
    distance_to_target = np.inf

    if len(to_nodes) > 0:
        distances_array_to_proteins = []
        for my_organ in my_organs:
            distances_array_to_proteins.append(
                compute_distances_array(from_node=my_organ,
                                        to_nodes=to_nodes,
                                        predecessors=predecessors)
            )

        distances_array_to_proteins = np.concatenate(
            distances_array_to_proteins,
            axis=0
        )

        array = distances_array_to_proteins[
                    distances_array_to_proteins[:, DistArrayCols.DISTANCE.value].argsort()
                ][0, :]

        distance_to_target = array[DistArrayCols.DISTANCE.value]
        if distance_to_target < np.inf:
            my_organ_chosen = int(array[DistArrayCols.FROM_NODE.value])
            target = int(array[DistArrayCols.TO_NODE.value])
            distance_to_target = int(distance_to_target)

    return my_organ_chosen, target, distance_to_target
