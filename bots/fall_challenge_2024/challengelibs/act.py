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
    WAIT = "WAIT"


class Strategy(NamedTuple):
    name: str = "Wait"
    objective: Objective = Objective.WAIT
    targets: set[int] = set()
    priority: float = np.inf

    def __hash__(self):
        return hash((self.objective.value, *self.targets, self.priority))


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
    value: float = - np.inf

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


def wait_action_with_message(message: str):
    action = Action()
    action.message = message
    return action


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
        grid: Grid,
        **kwargs
):
    # init
    from_node = nodes_pair.from_node
    to_node = nodes_pair.to_node
    distance = nodes_pair.distance
    shortest_path = nodes_pair.shortest_path

    # nothing to do
    if distance == np.inf or len(shortest_path) == 0:
        return wait_action_with_message("No targets accessible")

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
        return wait_action_with_message("Not enough proteins to grow or spore")

    # choose grow type
    if objective == Objective.PROTEINS:
        if distance == 2:
            action.t = "HARVESTER"
            action.grow = True
        else:
            action.t = "BASIC"
            action.grow = True

    if objective == Objective.ATTACK:
        if distance == 1:
            action.t = "TENTACLE"
            action.grow = True
        else:
            action.t = "BASIC"
            action.grow = True

    if objective == Objective.DEFAULT:
        grow_types_priority = ["BASIC", "TENTACLE", "HARVESTER", "SPORER"]
        action.t = define_grow_type(
            possible_grow_types=possible_grow_types,
            grow_types_priority=grow_types_priority
        )
        action.grow = True

    if not possible_grow_types[action.t]:
        return wait_action_with_message(
            f"Not enough proteins for {objective.value}: {action.t}"
        )

    # choose direction
    if action.t in ["HARVESTER", "TENTACLE", "SPORER"]:
        if "real_target" in kwargs:
            from_coord = Coordinates(x=action.x, y=action.y)
            to_coord = grid.get_node_coordinates(kwargs["real_target"])
        else:
            from_coord = Coordinates(x=action.x, y=action.y)
            to_coord = grid.get_node_coordinates(to_node)

        action.direction = get_direction(
            from_coordinates=from_coord,
            to_coordinates=to_coord
        )

    action.value = - distance - action.cost.sum()

    return action


def choose_best_actions(actions_by_strategy: dict[Strategy, Action]):
    best_strategy = Strategy()
    best_action = Action()

    for strategy, action in actions_by_strategy.items():
        if strategy.priority <= best_strategy.priority:
            if action.value > best_action.value:
                best_strategy = strategy
                best_action = action

    return best_strategy, best_action
