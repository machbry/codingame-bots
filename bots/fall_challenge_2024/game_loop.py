from typing import List

from scipy.sparse.csgraph import dijkstra

from bots.fall_challenge_2024.challengelibs.assets import Entities, Coordinates, Entity, ProteinStock
from bots.fall_challenge_2024.challengelibs.geometry import Grid, is_aligned
from bots.fall_challenge_2024.challengelibs.act import Action, choose_closest_organ_and_target, can_create_new_root, \
    can_use_sporer, can_use_harvester, can_use_tentacle
from bots.fall_challenge_2024.challengelibs.logger import log


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "width", "height", "nb_entities", "entities",
                 "my_protein_stock", "opp_protein_stock",
                 "required_actions_count", "grid", "create_new_root",
                 "actions")

    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.actions: list[str] = []

        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.nb_entities: int = 0
        self.my_protein_stock: ProteinStock = ProteinStock()
        self.opp_protein_stock: ProteinStock = ProteinStock()
        self.required_actions_count: int = 1

        self.grid = Grid(width=self.width, height=self.height)
        self.entities: Entities = Entities()

        self.create_new_root: bool = False

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

                if t in ["ROOT", "BASIC", "HARVESTER", "TENTACLE", "SPORER"]:
                    self.grid.disconnect_nodes(from_node=cardinal,
                                               to_node=node,
                                               directed=True)

        my_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.my_protein_stock.A = my_protein_stock[0]
        self.my_protein_stock.B = my_protein_stock[1]
        self.my_protein_stock.C = my_protein_stock[2]
        self.my_protein_stock.D = my_protein_stock[3]

        opp_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.opp_protein_stock.A = my_protein_stock[0]
        self.opp_protein_stock.B = my_protein_stock[1]
        self.opp_protein_stock.C = my_protein_stock[2]
        self.opp_protein_stock.D = my_protein_stock[3]

        self.required_actions_count = int(self.get_turn_input())

        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()

            proteins = set.union(*self.entities.proteins.values())

            my_organs_by_root = self.entities.my_organs_by_root

            opp_organs_free_neighbours = {
                neighbour: node
                for node in self.entities.opp_organs
                for neighbour in self.grid.get_node_neighbours(node)
            }

            dist_matrix, predecessors = dijkstra(
                self.grid.adjacency_matrix.sparce_matrix,
                return_predecessors=True
            )

            for my_root_id, my_organs in my_organs_by_root.items():
                grow = True
                spore = False
                grow_type = "BASIC"
                direction = None

                my_organ_chosen, target, distance_to_protein = choose_closest_organ_and_target(
                    my_organs=my_organs,
                    to_nodes=proteins,
                    dist_matrix=dist_matrix
                )

                # TODO : use this action more often
                if ((target is not None)
                        and self.create_new_root
                        and can_create_new_root(self.my_protein_stock)):
                    self.create_new_root = False
                    grow = False
                    spore = True
                    grow_type = None

                # TODO : use this action more often
                if ((target is not None)
                        and can_use_sporer(self.my_protein_stock, distance_to_protein)
                        and not spore):
                    grow_type = "SPORER"
                    self.create_new_root = True

                if ((target is not None)
                        and can_use_harvester(self.my_protein_stock, distance_to_protein)
                        and not spore):
                    grow_type = "HARVESTER"

                if target is None:
                    my_organ_chosen, target, distance_to_opp_neighbour = choose_closest_organ_and_target(
                        my_organs=my_organs,
                        to_nodes=set(opp_organs_free_neighbours.keys()),
                        dist_matrix=dist_matrix
                    )

                    if ((target is not None)
                            and can_use_tentacle(self.my_protein_stock, distance_to_opp_neighbour)):
                        grow_type = "TENTACLE"

                if target is None:
                    nb_t_max = 0

                    for t in ["D", "C", "B", "A"]:
                        harvested_nodes = self.entities.harvested_proteins[t]

                        nb_t = len(harvested_nodes)

                        if nb_t <= nb_t_max:
                            continue

                        for h in harvested_nodes:
                            cardinals = self.grid.get_node_frontier(h).cardinal_nodes
                            my_organs_neighbour = [org for org in my_organs
                                                   if org in cardinals]

                            if len(my_organs_neighbour) > 0:
                                my_organ_chosen = my_organs_neighbour[0]
                                target = h
                                nb_t_max = nb_t
                                self.entities.harvested_proteins[t].remove(target)
                                break

                if target is None:
                    for my_organ in my_organs:
                        node_neighbours = list(self.grid.get_node_neighbours(my_organ))
                        if len(node_neighbours) > 0:
                            my_organ_chosen, target = my_organ, node_neighbours[0]
                            break

                if target is not None:
                    my_organ_chosen_entity = self.entities[my_organ_chosen]
                    id = my_organ_chosen_entity.organ_id
                    next_node = target

                    if grow:
                        predecessor = predecessors[my_organ_chosen, target]
                        while predecessor != my_organ_chosen and predecessor != -9999:
                            next_node = predecessor
                            predecessor = predecessors[my_organ_chosen, next_node]

                    if spore:
                        from_organ_coordinates = my_organ_chosen_entity.coordinates
                        from_organ_direction = my_organ_chosen_entity.organ_dir

                        aligned = is_aligned(from_coord=from_organ_coordinates,
                                             from_direction=from_organ_direction,
                                             to_coord=self.grid.get_node_coordinates(next_node))
                        predecessor = predecessors[my_organ_chosen, target]
                        while (not (dist_matrix[next_node, target] > 1 and aligned)
                               and predecessor != my_organ_chosen
                               and predecessor != -9999):
                            next_node = predecessor
                            aligned = is_aligned(from_coord=from_organ_coordinates,
                                                 from_direction=from_organ_direction,
                                                 to_coord=self.grid.get_node_coordinates(next_node))
                            predecessor = predecessors[my_organ_chosen, next_node]

                    x, y = self.grid.get_node_coordinates(next_node)

                    if grow_type == "TENTACLE":
                        target = opp_organs_free_neighbours[target]

                    if grow_type == "SPORER":
                        target = predecessors[my_organ_chosen, target]

                    if grow_type in ["TENTACLE", "HARVESTER", "SPORER"]:
                        x_target, y_target = self.grid.get_node_coordinates(target)
                        diff_x = x_target - x
                        diff_y = y_target - y

                        if abs(diff_y) >= abs(diff_x):
                            direction = "N"
                            if diff_y > 0:
                                direction = "S"
                        else:
                            direction = "W"
                            if diff_x > 0:
                                direction = "E"

                        if grow_type == "HARVESTER":
                            target_entity = self.entities[target]
                            self.entities.harvested_proteins[target_entity.t].add(target)

                            target_cardinals = self.grid.get_node_frontier(target).cardinal_nodes
                            for cardinal in target_cardinals:
                                self.grid.disconnect_nodes(from_node=cardinal,
                                                           to_node=target,
                                                           directed=True)

                        if grow_type == "TENTACLE":
                            # TODO : target won't appear in opp_organs_free_neighbours
                            self.grid.connect_nodes(from_node=next_node,
                                                    to_node=target,
                                                    directed=True)

                    if (grow_type == "BASIC"
                            and self.my_protein_stock.A == 0
                            and self.my_protein_stock.B > 0
                            and self.my_protein_stock.C > 0):
                        grow_type = "TENTACLE"

                    action = Action(grow=grow, spore=spore, id=id, x=x, y=y, t=grow_type,
                                    direction=direction,
                                    message=f"{my_organ_chosen}/{next_node}/{target}")
                else:
                    action = Action()

                if action.grow and action.id == 59:
                    pass

                self.actions.append(str(action))
                print(action)

        return self.actions
