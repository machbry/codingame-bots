import sys
import random
from dataclasses import dataclass
from typing import List, Set

@dataclass(frozen=True)
class Link:
    n1: int
    n2: int

    def has_node(self, node: int) -> bool:
        return node in (self.n1, self.n2)

    def cut_link(self):
        print(f'{self.n1} {self.n2}')

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

class GameLoop:
    RUNNING = True

    def __init__(self):
        (n, l, e) = [int(i) for i in input().split()]
        self.init_inputs: List[str] = [f'{n} {l} {e}']
        links = set()
        for i in range(l):
            (n1, n2) = [int(j) for j in input().split()]
            self.init_inputs.append(f'{n1} {n2}')
            links.add(Link(n1=n1, n2=n2))
        gateways = []
        for i in range(e):
            ei = int(input())
            self.init_inputs.append(f'{ei}')
            gateways.append(ei)
        self.network = Network(nb_nodes=n, links=links, gateways=gateways)
        self.turns_inputs: List[str] = []
        print(self.init_inputs, file=sys.stderr, flush=True)

    def start(self):
        while GameLoop.RUNNING:
            si = int(input())
            self.turns_inputs.append(f'{si}')
            print(self.turns_inputs, file=sys.stderr, flush=True)
            links_from_bobnet = self.network.get_links_from_node(si)
            if len(links_from_bobnet) == 1:
                links_from_bobnet.pop().cut_link()
            else:
                gateway = random.choice(self.network.gateways)
                links_from_gateway = self.network.get_links_from_node(gateway)
                links_from_gateway.pop().cut_link()
GameLoop().start()