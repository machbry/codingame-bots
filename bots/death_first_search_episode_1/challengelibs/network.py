from typing import Set, List
from dataclasses import dataclass


@dataclass(frozen=True)
class Link:
    n1: int
    n2: int

    def has_node(self, node: int) -> bool:
        return node in (self.n1, self.n2)

    def cut_link(self):
        print(f"{self.n1} {self.n2}")


@dataclass
class Network:
    nb_nodes: int
    links: Set[Link]
    gateways: List[int]

    def get_links_from_node(self, node: int) -> Set[Link]:
        links_from_node = set()
        for link in self.links:
            if link.has_node(node):
                links_from_node.add(link)
        return links_from_node

