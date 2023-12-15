import sys
import random

from challengelibs.network import Node, Link, Network


# n: the total number of nodes in the level, including the gateways
# l: the number of links
# e: the number of exit gateways
n, l, e = [int(i) for i in input().split()]
start_inputs = f"{n} {l} {e}"

links = set()
for i in range(l):
    # n1: N1 and N2 defines a link between these nodes
    n1, n2 = [int(j) for j in input().split()]
    start_inputs += f"/{n1} {n2}"
    links.add(Link(n1=Node(index=n1), n2=Node(index=n2)))

gateways = []
for i in range(e):
    ei = int(input())  # the index of a gateway node
    start_inputs += f"/{ei}"
    gateways.append(Node(ei))


class GameLoop:
    RUNNING = True

    def __init__(self, network):
        self.network = network

    def start(self):
        # game loop
        while GameLoop.RUNNING:
            si = int(input())  # The index of the node on which the Bobnet agent is positioned this turn
            inputs = start_inputs + f"/{si}"
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
