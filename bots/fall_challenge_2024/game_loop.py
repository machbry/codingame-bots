from typing import List

from scipy.sparse.csgraph import dijkstra

from bots.fall_challenge_2024.challengelibs.assets import Entities, Coordinates, Entity
from bots.fall_challenge_2024.challengelibs.geometry import Grid
from bots.fall_challenge_2024.challengelibs.act import Action, choose_closest_organ_and_target
from bots.fall_challenge_2024.challengelibs.logger import log


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "width", "height", "nb_entities", "entities",
                 "my_A", "my_B", "my_C", "my_D", "opp_protein_stock",
                 "required_actions_count", "grid")

    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.nb_entities: int = 0
        self.my_A, self.my_B, self.my_C, self.my_D = 0, 0, 0, 0
        self.opp_protein_stock: list = []
        self.required_actions_count: int = 1

        self.grid = Grid(width=self.width, height=self.height)
        self.entities: Entities = Entities()

        if GameLoop.LOG:
            self.print_init_logs()

    def get_init_input(self):
        result = input()
        self.init_inputs.append(result)
        return result

    def get_turn_input(self):
        result = input()
        self.turns_inputs.append(result)
        return result

    def print_init_logs(self):
        log(self.init_inputs)

    def print_turn_logs(self):
        log(self.nb_turns)
        log(self.turns_inputs)
        if GameLoop.RESET_TURNS_INPUTS:
            self.turns_inputs = []

    def update_assets(self):
        self.nb_turns += 1
        self.nb_entities = int(self.get_turn_input())
        self.entities.new_turn()

        for i in range(self.nb_entities):
            inputs = self.get_turn_input().split()

            coordinates = Coordinates(x=int(inputs[0]), y=int(inputs[1]))
            t = inputs[2]
            owner = int(inputs[3])
            organ_id = int(inputs[4])
            organ_dir = inputs[5]
            organ_parent_id = int(inputs[6])
            organ_root_id = int(inputs[7])
            node = self.grid.get_node(coordinates)

            entity = Entity(
                node=node,
                coordinates=coordinates,
                t=t,
                owner=owner,
                organ_id=organ_id,
                organ_dir=organ_dir,
                organ_parent_id=organ_parent_id,
                organ_root_id=organ_root_id
            )

            self.entities[node] = entity

            cardinal_nodes = self.grid.get_node_frontier(node).cardinal_nodes
            for cardinal in cardinal_nodes:
                if t == "WALL":
                    self.grid.disconnect_nodes(from_node=node,
                                               to_node=cardinal)

                if t in ["ROOT", "BASIC", "HARVESTER", "TENTACLE"]:
                    self.grid.disconnect_nodes(from_node=cardinal,
                                               to_node=node,
                                               directed=True)

        self.my_A, self.my_B, self.my_C, self.my_D = [int(i) for i in self.get_turn_input().split()]
        self.opp_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.required_actions_count = int(self.get_turn_input())

        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()

            proteins = set()
            for nodes in self.entities.proteins.values():
                proteins = proteins.union(nodes)

            my_organs = self.entities.my_organs

            opp_organs_free_neighbours = {}
            for node in self.entities.opp_organs:
                for neighbour in self.grid.get_node_neighbours(node):
                    opp_organs_free_neighbours[neighbour] = node

            dijkstra_algorithm = dijkstra(
                self.grid.adjacency_matrix.sparce_matrix,
                return_predecessors=True)
            dist_matrix = dijkstra_algorithm[0]
            predecessors = dijkstra_algorithm[1]

            for i in range(self.required_actions_count):
                t = "BASIC"
                direction = None

                my_organ_chosen, target, distance_to_protein = choose_closest_organ_and_target(
                    my_organs=my_organs,
                    to_nodes=proteins,
                    dist_matrix=dist_matrix
                )

                if target and distance_to_protein == 2 and self.my_C > 0 and self.my_D > 0:
                    t = "HARVESTER"

                if not target:
                    my_organ_chosen, target, distance_to_opp_neighbour = choose_closest_organ_and_target(
                        my_organs=my_organs,
                        to_nodes=set(opp_organs_free_neighbours.keys()),
                        dist_matrix=dist_matrix
                    )

                    if target and distance_to_opp_neighbour == 1 and self.my_B > 0 and self.my_C > 0:
                        t = "TENTACLE"

                if not target:
                    for my_organ in self.entities.my_organs:
                        node_neighbours = list(self.grid.get_node_neighbours(my_organ))
                        if len(node_neighbours) > 0:
                            my_organ_chosen, target = my_organ, node_neighbours[0]
                            break
                        # TODO : go to harvested proteins

                if target:
                    my_organ_chosen_entity = self.entities[my_organ_chosen]
                    id = my_organ_chosen_entity.organ_id

                    predecessor = predecessors[my_organ_chosen, target]
                    next_node = target
                    while predecessor != my_organ_chosen and predecessor != -9999:
                        next_node = predecessor
                        predecessor = predecessors[my_organ_chosen, next_node]

                    x, y = self.grid.get_node_coordinates(next_node)

                    if t == "TENTACLE":
                        target = opp_organs_free_neighbours[target]

                    if t in ["TENTACLE", "HARVESTER"]:
                        x_target, y_target = self.grid.get_node_coordinates(target)
                        if x < x_target and y == y_target:
                            direction = "E"
                        if x > x_target and y == y_target:
                            direction = "W"
                        if x == x_target and y > y_target:
                            direction = "N"
                        if x == x_target and y < y_target:
                            direction = "S"

                        if t == "HARVESTER":
                            # TODO : possible bad side effects
                            target_neighbours = self.grid.get_node_neighbours(target)
                            for neighbour in target_neighbours:
                                self.grid.disconnect_nodes(from_node=target,
                                                           to_node=neighbour)

                        if t == "TENTACLE":
                            # TODO : target won't appear in opp_organs_free_neighbours
                            self.grid.connect_nodes(from_node=next_node,
                                                    to_node=target,
                                                    directed=True)

                    action = Action(grow=True, id=id, x=x, y=y, t=t,
                                    direction=direction,
                                    message=f"{my_organ_chosen}/{next_node}/{target}")
                else:
                    action = Action()

                print(action)
