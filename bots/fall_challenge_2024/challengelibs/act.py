from enum import Enum
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np

from botlibs.graph.classes import NodesPair
from bots.fall_challenge_2024.challengelibs.assets import ProteinStock, Entities, Coordinates
from bots.fall_challenge_2024.challengelibs.geometry import Grid, get_direction


class Objective(Enum):
    PROTEINS = "PROTEINS" # HARVEST target
    REPRODUCTION = "REPRODUCTION" # SPORE + ROOT on target
    ATTACK = "ATTACK" # TENTACLE target
    DEFAULT = "DEFAULT"


class Strategy(NamedTuple):
    objective: Objective
    targets: set[int]


@dataclass
class Action:
    grow: bool = False
    spore: bool = False
    id: int = 0
    x: int = 0
    y: int = 0
    t: str = "BASIC"
    direction: str = None
    message: str = ""

    def __repr__(self):
        if not self.grow and not self.spore:
            return "WAIT"

        if self.spore:
            return f"SPORE {self.id} {self.x} {self.y}"

        if not self.direction:
            return f"GROW {self.id} {self.x} {self.y} {self.t} {self.message}"

        return f"GROW {self.id} {self.x} {self.y} {self.t} {self.direction} {self.message}"

    @property
    def cost(self):
        if self.grow:
            if self.t == "BASIC":
                return ProteinStock(A=-1)
            if self.t == "HARVESTER":
                return ProteinStock(C=-1, D=-1)
            if self.t == "TENTACLE":
                return ProteinStock(B=-1, C=-1)
            if self.t == "SPORER":
                return ProteinStock(B=-1, D=-1)
        if self.spore:
            return ProteinStock(A=-1, B=-1, C=-1, D=-1)

        return ProteinStock()


def can_grow_basic(protein_stock: ProteinStock):
    return protein_stock.A > 0


def can_grow_sporer(protein_stock: ProteinStock):
    return protein_stock.B > 0 and protein_stock.D > 0


def can_grow_harvester(protein_stock: ProteinStock):
    return protein_stock.C > 0 and protein_stock.D > 0


def can_grow_tentacle(protein_stock: ProteinStock):
    return protein_stock.B > 0 and protein_stock.C > 0


def can_spore_new_root(protein_stock: ProteinStock):
    return protein_stock.A > 0 and protein_stock.B > 0 and protein_stock.C > 0 and protein_stock.D > 0


def define_grow_type(possible_grow_types: dict[str, bool], grow_types_priority: list[str]):
    for t in grow_types_priority:
        if possible_grow_types[t]:
            return t

def next_action_to_reach_target(
        nodes_pair: NodesPair,
        objective: Objective,
        protein_stock: ProteinStock,
        entities: Entities,
        grid: Grid
):
    # init
    from_node = nodes_pair.from_node
    to_node = nodes_pair.to_node
    distance = nodes_pair.distance
    shortest_path = nodes_pair.shortest_path

    # nothing to do
    if distance == np.inf or len(shortest_path) == 0:
        action = Action()
        action.message = "No targets accessible"
        return action

    # default action
    from_organ = entities[from_node]
    next_node = shortest_path[0]
    x, y = grid.get_node_coordinates(next_node)

    action = Action(
        id=from_organ.organ_id,
        x=x,
        y=y,
        message=f"{from_node}/{next_node}/{to_node}"
    )

    # what can we do
    possible_grow_types = {
        "BASIC": can_grow_basic(protein_stock=protein_stock),
        "TENTACLE": can_grow_tentacle(protein_stock=protein_stock),
        "SPORER": can_grow_sporer(protein_stock=protein_stock),
        "HARVESTER": can_grow_harvester(protein_stock=protein_stock)
    }

    # not enough proteins to grow or spore
    if True not in possible_grow_types.values():
        return action

    # we can grow
    action.grow = True

    # choose grow type
    grow_types_priority = ["BASIC", "TENTACLE", "SPORER", "HARVESTER"]
    if distance == 2 and objective == Objective.PROTEINS:
        grow_types_priority = ["HARVESTER", "BASIC", "TENTACLE", "SPORER"]

    if distance == 2 and objective == Objective.ATTACK:
        grow_types_priority = ["TENTACLE", "BASIC", "SPORER", "HARVESTER"]

    action.t = define_grow_type(
        possible_grow_types=possible_grow_types,
        grow_types_priority=grow_types_priority
    )

    # choose direction
    if action.t in ["HARVESTER", "TENTACLE", "SPORER"]:
        action.direction = get_direction(
            from_coordinates=Coordinates(x=action.x, y=action.y),
            to_coordinates=grid.get_node_coordinates(to_node)
        )

    return action
