from typing import Set, List
from dataclasses import dataclass

from botlibs.graph.classes import Edge
from botlibs.graph.create import create_adjacency_list_from_edges


class Link(Edge):
    def __init__(self, from_node: int, to_node: int):
        super().__init__(from_node, to_node, False, 1)

    def cut(self):
        print(f"{self.from_node} {self.to_node}")


@dataclass
class Network:
    nb_nodes: int
    links: Set[Link]
    gateways: List[int]

    def __post_init__(self):
        self.adjacency_list = create_adjacency_list_from_edges(self.links)

    def cut(self, link: Link):
        self.adjacency_list.remove_edge(link)
        try:
            self.links.remove(link)
        except KeyError:
            self.links.remove(Link(link.to_node, link.from_node))
        link.cut()

    def get_node_neighbours(self, node):
        return list(self.adjacency_list[node])
