from dataclasses import dataclass, field
from typing import NamedTuple


class Coordinates(NamedTuple):
    x: int
    y: int


@dataclass
class ProteinStock:
    A: int = 0
    B: int = 0
    C: int = 0
    D: int = 0

    def __add__(self, other):
        return ProteinStock(
            A=self.A + other.A,
            B=self.B + other.B,
            C=self.C + other.C,
            D=self.D + other.D
        )

    def sum(self):
        return self.A + self.B + self.C + self.D


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

    def __hash__(self):
        return int(self.node)


@dataclass
class Entities:
    nodes: dict[int, Entity] = field(default_factory=dict)
    proteins: dict[str, set[int]] = field(default_factory=dict)
    my_organs_by_root: dict[int, set[int]] = field(default_factory=dict)
    opp_organs: set[int] = field(default_factory=set)
    harvested_proteins: dict[int, dict[str, set[int]]] = field(default_factory=dict)

    def __getitem__(self, node):
        if node not in self.nodes:
            return None
        return self.nodes.__getitem__(node)

    def __setitem__(self, node, entity: Entity):
        if entity.t in ["A", "B", "C", "D"]:
            self.proteins[entity.t].add(entity.node)
        if entity.owner == 1:
            if entity.organ_root_id not in self.my_organs_by_root:
                self.my_organs_by_root[entity.organ_root_id] = set()
            self.my_organs_by_root[entity.organ_root_id].add(entity.node)
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
        self.my_organs_by_root = {}
        self.opp_organs = set()
        self.harvested_proteins = {
            1: {
                "A": set(),
                "B": set(),
                "C": set(),
                "D": set()
            },
            0: {
                "A": set(),
                "B": set(),
                "C": set(),
                "D": set()
            },
        }

    def update_harvested_proteins(self, aimed_nodes_by_harvester: dict[Entity, int]):
        for harvester_entity, harvested_node in aimed_nodes_by_harvester.items():
            harvested_entity = self[harvested_node]
            if harvested_entity is not None:
                harvested_entity_type = harvested_entity.t
                if harvested_entity_type in ["A", "B", "C", "D"]:
                    self.harvested_proteins[harvester_entity.owner][harvested_entity_type].add(harvested_node)

    def get_wanted_proteins_for_owner(
            self,
            protein_stock: ProteinStock,
            max_turns_left,
            nb_roots: int,
            harvested_proteins_per_type: dict[str, set[int]]
    ):
        wanted_types = ["A", "B", "C", "D"]
        wanted_proteins = set()

        for t in wanted_types:
            proteins_t = self.proteins[t]
            stock_is_not_enough = getattr(protein_stock, t) < max_turns_left * nb_roots / 2
            protein_type_still_exists = len(proteins_t) > 0

            if stock_is_not_enough and protein_type_still_exists:
                wanted_proteins = wanted_proteins.union(proteins_t)

            harvested_proteins = harvested_proteins_per_type[t]
            for harvested_protein in harvested_proteins:
                if harvested_protein in wanted_proteins:
                    wanted_proteins.remove(harvested_protein)

        return wanted_proteins
