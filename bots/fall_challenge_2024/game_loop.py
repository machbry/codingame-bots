from typing import List

from botlibs.graph.algorithms import DijkstraAlgorithm
from bots.fall_challenge_2024.challengelibs.assets import Entities, Coordinates, Entity, ProteinStock
from bots.fall_challenge_2024.challengelibs.geometry import Grid
from bots.fall_challenge_2024.challengelibs.act import Action, next_action_to_reach_target, Objective, Strategy, \
    choose_best_actions
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
        self.grid.new_turn()

        aimed_nodes_by_harvester = {}
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

            frontier_nodes = self.grid.get_node_frontier(node)
            cardinal_nodes = frontier_nodes.cardinal_nodes
            for cardinal in cardinal_nodes:
                if t == "WALL":
                    self.grid.disconnect_nodes(from_node=node,
                                               to_node=cardinal)

                if t in ["ROOT", "BASIC", "HARVESTER", "TENTACLE", "SPORER"]:
                    self.grid.disconnect_nodes(from_node=cardinal,
                                               to_node=node,
                                               directed=True)

            if t == "HARVESTER":
                harvested_node = frontier_nodes.nodes_by_direction[organ_dir]
                if harvested_node is not None:
                    aimed_nodes_by_harvester[entity] = harvested_node

            if t == "TENTACLE" and owner == 0:
                node_attacked = frontier_nodes.nodes_by_direction[organ_dir]
                if node_attacked is not None:
                    cardinals_attacked = self.grid.get_node_frontier(node_attacked).cardinal_nodes
                    for cardinal in cardinals_attacked:
                        self.grid.disconnect_nodes(from_node=cardinal,
                                                   to_node=node_attacked,
                                                   directed=True)

        self.entities.update_harvested_proteins(
            aimed_nodes_by_harvester=aimed_nodes_by_harvester
        )

        my_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.my_protein_stock.A = my_protein_stock[0]
        self.my_protein_stock.B = my_protein_stock[1]
        self.my_protein_stock.C = my_protein_stock[2]
        self.my_protein_stock.D = my_protein_stock[3]

        opp_protein_stock = [int(i) for i in self.get_turn_input().split()]
        self.opp_protein_stock.A = opp_protein_stock[0]
        self.opp_protein_stock.B = opp_protein_stock[1]
        self.opp_protein_stock.C = opp_protein_stock[2]
        self.opp_protein_stock.D = opp_protein_stock[3]

        self.required_actions_count = int(self.get_turn_input())

        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()

            my_organs_by_root = self.entities.my_organs_by_root

            my_harvested_proteins_per_type = self.entities.harvested_proteins[1]
            for protein_type, harvested_nodes in my_harvested_proteins_per_type.items():
                for harvested_node in harvested_nodes:
                    weight = max(self.grid.nb_nodes - getattr(self.my_protein_stock, protein_type), 1)
                    self.grid.update_weight_toward_node(
                        node=harvested_node,
                        weight=weight
                    )

            my_wanted_proteins = self.entities.get_wanted_proteins_for_owner(
                protein_stock=self.my_protein_stock,
                max_turns_left=100-self.nb_turns,
                nb_roots=len(my_organs_by_root),
                harvested_proteins_per_type=my_harvested_proteins_per_type
            )

            neighbours_opp_organs = {}
            for opp_organ in self.entities.opp_organs:
                neighbours = self.grid.get_node_neighbours(opp_organ)
                for neighbour in neighbours:
                    neighbours_opp_organs[neighbour] = opp_organ

            dijkstra_algorithm = DijkstraAlgorithm(
                adjacency_matrix=self.grid.adjacency_matrix
            )

            for my_root_id, my_organs in my_organs_by_root.items():
                organs_neighbours = set()
                for organ in my_organs:
                    organs_neighbours = organs_neighbours.union(self.grid.get_node_neighbours(organ))

                strategies = [
                    Strategy(
                        name="target_wanted_proteins",
                        objective=Objective.PROTEINS,
                        targets=my_wanted_proteins,
                        priority=0
                    ),
                    Strategy(
                        name="attack_opponent",
                        objective=Objective.ATTACK,
                        targets=set(neighbours_opp_organs.keys()),
                        priority=0
                    ),
                    Strategy(
                        name="target_proteins",
                        objective=Objective.PROTEINS,
                        targets=set.union(*self.entities.proteins.values()),
                        priority=1
                    ),
                    Strategy(
                        name="default",
                        objective=Objective.DEFAULT,
                        targets=organs_neighbours,
                        priority=2
                    )
                ]

                actions_by_strategy = {}
                for strategy in strategies:
                    closest_organ_target_pair = dijkstra_algorithm.find_closest_nodes_pair(
                        from_nodes=my_organs,
                        to_nodes=strategy.targets
                    )

                    kwargs = {}
                    to_node = closest_organ_target_pair.to_node
                    if to_node is not None and strategy.objective == Objective.ATTACK:
                        opp_organ_neighbour = closest_organ_target_pair.to_node
                        kwargs["real_target"] = neighbours_opp_organs[opp_organ_neighbour]

                    action = next_action_to_reach_target(
                        nodes_pair=closest_organ_target_pair,
                        objective=strategy.objective,
                        protein_stock=self.my_protein_stock,
                        entities=self.entities,
                        grid=self.grid,
                        **kwargs
                    )

                    actions_by_strategy[strategy] = action

                strategy, action = choose_best_actions(actions_by_strategy=actions_by_strategy)

                self.my_protein_stock = self.my_protein_stock + action.cost
                action.message = f"{strategy.name}/{action.message}"

                print(action)
