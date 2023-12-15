from typing import Set, List
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    index: int


@dataclass(frozen=True)
class Link:
    n1: Node
    n2: Node

    def has_node(self, node: Node) -> bool:
        return node in (self.n1, self.n2)

    def cut_link(self):
        print(f"{self.n1.index} {self.n2.index}")


@dataclass
class Network:
    nb_nodes: int
    links: Set[Link]
    gateways: List[Node]
    _nodes: List[Node] = field(init=False, compare=False)

    def __post_init__(self):
        self._nodes = [Node(i) for i in range(self.nb_nodes)]

    def get_node(self, index: int) -> Node:
        return self._nodes[index]

    def get_links_from_node(self, node: Node) -> Set[Link]:
        links_from_node = set()
        for link in self.links:
            if link.has_node(node):
                links_from_node.add(link)
        return links_from_node

