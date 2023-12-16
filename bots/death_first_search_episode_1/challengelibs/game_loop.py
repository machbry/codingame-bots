import random
import sys
from typing import List

from .network import Link, Network


class GameLoop:
    RUNNING = True

    def __init__(self):
        # n: the total number of nodes in the level, including the gateways
        # l: the number of links
        # e: the number of exit gateways
        n, l, e = [int(i) for i in input().split()]
        self.init_inputs: List[str] = [f"{n} {l} {e}"]

        links = set()
        for i in range(l):
            # n1: N1 and N2 defines a link between these nodes
            n1, n2 = [int(j) for j in input().split()]
            self.init_inputs.append(f"{n1} {n2}")
            links.add(Link(n1, n2))

        gateways = []
        for i in range(e):
            ei = int(input())  # the index of a gateway node
            self.init_inputs.append(f"{ei}")
            gateways.append(ei)

        self.network = Network(nb_nodes=n, links=links, gateways=gateways)

        self.turns_inputs: List[str] = []
        print(self.init_inputs, file=sys.stderr, flush=True)

    def start(self):
        # game loop
        while GameLoop.RUNNING:
            si = int(input())  # The index of the node on which the Bobnet agent is positioned this turn
            self.turns_inputs.append(f"{si}")
            print(self.turns_inputs, file=sys.stderr, flush=True)

            played = False
            bobnet_neighbours = self.network.get_node_neighbours(si)
            if len(bobnet_neighbours) == 1:
                self.network.cut(Link(si, bobnet_neighbours[0]))
                played = True
            else:
                for gateway in self.network.gateways:
                    if gateway in bobnet_neighbours:
                        self.network.cut(Link(si, gateway))
                        played = True
                        break
            if not played:
                self.network.cut(random.choice(list(self.network.links)))
