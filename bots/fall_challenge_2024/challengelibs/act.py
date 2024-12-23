from dataclasses import dataclass

import numpy as np

from bots.fall_challenge_2024.challengelibs.assets import ProteinStock


@dataclass
class Action:
    grow: bool = False
    spore: bool = False
    id: int = 0
    x: int = 0
    y: int = 0
    t: str = "BASIC"
    direction: str = None
    message: str = "OK"

    def __repr__(self):
        if not self.grow and not self.spore:
            return "WAIT"

        if self.spore:
            return f"SPORE {self.id} {self.x} {self.y}"

        if not self.direction:
            return f"GROW {self.id} {self.x} {self.y} {self.t} {self.message}"

        return f"GROW {self.id} {self.x} {self.y} {self.t} {self.direction} {self.message}"


def choose_closest_organ_and_target(my_organs: set[int], to_nodes: set[int], dist_matrix: np.ndarray):
    my_organ_chosen = None
    target = None
    distance_to_target = np.inf

    for to_node in to_nodes:
        for my_organ in my_organs:
            distance = dist_matrix[my_organ, to_node]

            if distance < distance_to_target:
                my_organ_chosen = my_organ
                target = to_node
                distance_to_target = int(distance)

    return my_organ_chosen, target, distance_to_target


def can_create_new_root(protein_stock: ProteinStock):
    return all(resource > 0 for resource
               in [protein_stock.A, protein_stock.B, protein_stock.C, protein_stock.D])


def can_use_sporer(protein_stock: ProteinStock, distance_to_target: int):
    return (distance_to_target > protein_stock.A > 1 and protein_stock.B > 1 and
            protein_stock.C > 0 and protein_stock.D)


def can_use_harvester(protein_stock: ProteinStock, distance_to_target: int):
    return distance_to_target == 2 and protein_stock.C > 0 and protein_stock.D > 0


def can_use_tentacle(protein_stock: ProteinStock, distance_to_target: int):
    return distance_to_target == 1 and protein_stock.B > 0 and protein_stock.C > 0

