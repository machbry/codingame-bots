import sys
from typing import List

import numpy as np
from scipy.sparse.csgraph import dijkstra

from botlibs.graph.classes import AdjacencyMatrix, Edge
from bots.fall_challenge_2024.challengelibs.act import Action
from bots.fall_challenge_2024.challengelibs.assets import EntityAttrs, EntityType, Direction


class GameLoop:
    __slots__ = ("init_inputs", "nb_turns", "turns_inputs", "width", "height", "entity_count", "entities",
                 "my_protein_stock", "opp_protein_stock", "required_actions_count",
                 "nb_nodes", "adjacency_matrix")

    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []

        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.nb_nodes = self.width * self.height
        self.entity_count: int = 0
        self.entities: np.ndarray = np.zeros(shape=(0, 8))
        self.my_protein_stock: np.ndarray = np.zeros(shape=(1, 4))
        self.opp_protein_stock: np.ndarray = np.zeros(shape=(1, 4))
        self.required_actions_count: int = 1
        self.adjacency_matrix = AdjacencyMatrix(np.zeros((self.nb_nodes, self.nb_nodes), dtype=int))

        for node in range(self.nb_nodes):
            x, y = self.get_coordinates(node)

            if y >= 1:
                node_up = self.get_node(x, y - 1)
                self.connect_nodes(node, node_up)

            if x >= 1:
                node_left = self.get_node(x - 1, y)
                self.connect_nodes(node, node_left)

            if x < self.width - 1:
                node_right = self.get_node(x + 1, y)
                self.connect_nodes(node, node_right)

            if y < self.height - 1:
                node_down = self.get_node(x, y + 1)
                self.connect_nodes(node, node_down)

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
        self.entity_count = int(self.get_turn_input())
        self.entities = np.zeros(shape=(self.entity_count, len(EntityAttrs)), dtype=int)

        for i in range(self.entity_count):
            inputs = self.get_turn_input().split()
            x = int(inputs[0])
            y = int(inputs[1])
            t = EntityType[inputs[2]].value
            owner = int(inputs[3])
            organ_id = int(inputs[4])
            organ_dir = Direction[inputs[5]].value
            organ_parent_id = int(inputs[6])
            organ_root_id = int(inputs[7])
            node = self.get_node(x=x, y=y)

            self.entities[i, EntityAttrs.X.value] = x
            self.entities[i, EntityAttrs.Y.value] = y
            self.entities[i, EntityAttrs.TYPE.value] = t
            self.entities[i, EntityAttrs.OWNER.value] = owner
            self.entities[i, EntityAttrs.ORGAN_ID.value] = organ_id
            self.entities[i, EntityAttrs.ORGAN_DIR.value] = organ_dir
            self.entities[i, EntityAttrs.ORGAN_PARENT_ID.value] = organ_parent_id
            self.entities[i, EntityAttrs.ORGAN_ROOT_ID.value] = organ_root_id
            self.entities[i, EntityAttrs.NODE.value] = node

            if t in [EntityType.WALL.value]:
                if y >= 1:
                    node_up = self.get_node(x, y - 1)
                    self.disconnect_nodes(node, node_up)

                if x >= 1:
                    node_left = self.get_node(x - 1, y)
                    self.disconnect_nodes(node, node_left)

                if x < self.width - 1:
                    node_right = self.get_node(x + 1, y)
                    self.disconnect_nodes(node, node_right)

                if y < self.height - 1:
                    node_down = self.get_node(x, y + 1)
                    self.disconnect_nodes(node, node_down)

        self.my_protein_stock = np.ndarray([int(i) for i in self.get_turn_input().split()])
        self.opp_protein_stock = np.ndarray([int(i) for i in self.get_turn_input().split()])
        self.required_actions_count = int(self.get_turn_input())

        if GameLoop.LOG:
            self.print_turn_logs()

    def get_node(self, x: int, y: int):
        return x + self.width * y

    def get_coordinates(self, node: int):
        y = node // self.width
        x = node % self.width
        return x, y

    def connect_nodes(self, node_1, node_2):
        edge = Edge(from_node=node_1, to_node=node_2)
        self.adjacency_matrix.add_edge(edge)

    def disconnect_nodes(self, node_1, node_2):
        edge = Edge(from_node=node_1, to_node=node_2)
        self.adjacency_matrix.remove_edge(edge)

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()

            proteins = self.entities[
                self.entities[:, EntityAttrs.TYPE.value] == EntityType.A.value
            ]

            my_organs = self.entities[
                self.entities[:, EntityAttrs.OWNER.value] == 1
            ]

            predecessors = dijkstra(self.adjacency_matrix.sparce_matrix, return_predecessors=True)[1]

            my_organs_nodes = my_organs[:, EntityAttrs.NODE.value]
            proteins_nodes = proteins[:, EntityAttrs.NODE.value]

            dist_array = np.zeros_like(self.adjacency_matrix.array)
            dist_array[:, :] = 9999
            distance_max = 9999

            my_organ_node_chosen = None
            for my_organ_node in my_organs_nodes:
                for protein_node in proteins_nodes:
                    predecessor_node = my_organ_node
                    distance = 0
                    while predecessor_node != protein_node:
                        next_node = predecessor_node
                        predecessor_node = predecessors[protein_node, next_node]
                        distance += 1
                    if distance <= distance_max:
                        my_organ_node_chosen = my_organ_node
                        target_node = protein_node
                        distance_max = distance

            for i in range(self.required_actions_count):
                x, y = self.get_coordinates(target_node)
                id = self.entities[
                        self.entities[:, EntityAttrs.NODE.value] == my_organ_node_chosen
                    ][:, EntityAttrs.ORGAN_ID.value][0]
                action = Action(grow=True, id=id, x=x, y=y)
                print(action)
