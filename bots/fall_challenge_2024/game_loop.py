import sys
from typing import List

from scipy.sparse.csgraph import dijkstra

from bots.fall_challenge_2024.challengelibs.assets import Grid, Entities, Coordinates, Entity
from bots.fall_challenge_2024.challengelibs.act import Action, choose_organ_and_target


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "width", "height", "nb_entities", "entities",
                 "my_protein_stock", "opp_protein_stock", "required_actions_count", "grid")

    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.nb_entities: int = 0
        self.my_protein_stock: list = []
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
        print(self.init_inputs, file=sys.stderr, flush=True)

    def print_turn_logs(self):
        print(self.nb_turns, file=sys.stderr, flush=True)
        print(self.turns_inputs, file=sys.stderr, flush=True)
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

            node_neighbours = self.grid.get_node_neighbours(node)
            for neighbour in node_neighbours:
                if t == "WALL":
                    self.grid.disconnect_nodes(from_node=node,
                                               to_node=neighbour)

                if t in ["ROOT", "BASIC", "HARVESTER"]:
                    self.grid.disconnect_nodes(from_node=neighbour,
                                               to_node=node,
                                               directed=True)

        self.my_protein_stock = [int(i) for i in self.get_turn_input().split()]
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

            opp_organs_free_neighbours = set()
            for node in self.entities.opp_organs:
                opp_organs_free_neighbours = opp_organs_free_neighbours.union(
                    self.grid.get_node_neighbours(node)
                )

            predecessors = dijkstra(
                self.grid.adjacency_matrix.sparce_matrix,
                return_predecessors=True)[1]

            for i in range(self.required_actions_count):
                t = "BASIC"
                direction = None

                my_organ_chosen, target, distance_to_protein = choose_organ_and_target(
                    my_organs=my_organs,
                    to_nodes=proteins,
                    predecessors=predecessors
                )

                if target and distance_to_protein == 2 and self.my_protein_stock[2] > 0 and self.my_protein_stock[3] > 0:
                    t = "HARVESTER"

                if not target:
                    my_organ_chosen, target, _ = choose_organ_and_target(
                        my_organs=my_organs,
                        to_nodes=opp_organs_free_neighbours,
                        predecessors=predecessors
                    )

                if not target:
                    for my_organ in self.entities.my_organs:
                        node_neighbours = self.grid.get_node_neighbours(my_organ)
                        if len(node_neighbours) > 0:
                            my_organ_chosen, target = my_organ, node_neighbours[0]
                            break

                if target:
                    my_organ_chosen_entity = self.entities[my_organ_chosen]
                    id = my_organ_chosen_entity.organ_id

                    predecessor = predecessors[my_organ_chosen, target]
                    next_node = target
                    while predecessor != my_organ_chosen and predecessor != -9999:
                        next_node = predecessor
                        predecessor = predecessors[my_organ_chosen, next_node]

                    x, y = self.grid.get_node_coordinates(next_node)

                    if t == "HARVESTER":
                        x_target, y_target = self.grid.get_node_coordinates(target)
                        if x < x_target and y == y_target:
                            direction = "E"
                        if x > x_target and y == y_target:
                            direction = "W"
                        if x == x_target and y > y_target:
                            direction = "N"
                        if x == x_target and y < y_target:
                            direction = "S"

                        # TODO : possible bad side effects
                        target_neighbours = self.grid.get_node_neighbours(target)
                        for neighbour in target_neighbours:
                            self.grid.disconnect_nodes(from_node=target,
                                                       to_node=neighbour)

                    action = Action(grow=True, id=id, x=x, y=y, t=t,
                                    direction=direction,
                                    message=f"{my_organ_chosen}/{next_node}/{target}")
                else:
                    action = Action()

                print(action)
