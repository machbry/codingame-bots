from dataclasses import dataclass, field
from typing import NamedTuple


class Coordinates(NamedTuple):
    x: int
    y: int


@dataclass
class Entity:
    node: int
    coordinates: Coordinates
    t: str = "EMPTY"
    owner: int = -1
    organ_id: int = 0
    organ_dir: str = "X"
    organ_parent_id: int = 0
    organ_root_id: int = 0


@dataclass
class Entities:
    nodes: dict[int, Entity] = field(default_factory=dict)
    proteins: dict[str, set[int]] = field(default_factory=dict)
    my_organs: set[int] = field(default_factory=set)
    opp_organs: set[int] = field(default_factory=set)

    def __getitem__(self, node):
        return self.nodes.__getitem__(node)

    def __setitem__(self, node, entity: Entity):
        if entity.t in ["A", "B", "C", "D"]:
            self.proteins[entity.t].add(entity.node)
        if entity.owner == 1:
            self.my_organs.add(entity.node)
        if entity.owner == 0:
            self.opp_organs.add(entity.node)
        self.nodes.__setitem__(node, entity)

    def new_turn(self):
        self.proteins = {
            "A": set(),
            "B": set(),
            "C": set(),
            "D": set()
        }
        self.my_organs = set()
        self.opp_organs = set()
