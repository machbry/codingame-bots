import sys
import random
from dataclasses import dataclass, field
from typing import Set, List

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
        print(f'{self.n1.index} {self.n2.index}')

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
(n, l, e) = [int(i) for i in input().split()]
start_inputs = f'{n} {l} {e}'
links = set()
for i in range(l):
    (n1, n2) = [int(j) for j in input().split()]
    start_inputs += f'/{n1} {n2}'
    links.add(Link(n1=Node(index=n1), n2=Node(index=n2)))
gateways = []
for i in range(e):
    ei = int(input())
    start_inputs += f'/{ei}'
    gateways.append(Node(ei))

class GameLoop:
    RUNNING = True

    def __init__(self, network):
        self.network = network

    def start(self):
        while GameLoop.RUNNING:
            si = int(input())
            inputs = start_inputs + f'/{si}'
            print(inputs, file=sys.stderr, flush=True)
            bobnet_node = self.network.get_node(si)
            links_from_bobnet = self.network.get_links_from_node(bobnet_node)
            if len(links_from_bobnet) == 1:
                links_from_bobnet.pop().cut_link()
            else:
                gateway = random.choice(self.network.gateways)
                links_from_gateway = self.network.get_links_from_node(gateway)
                links_from_gateway.pop().cut_link()
GameLoop(Network(nb_nodes=n, links=links, gateways=gateways)).start()