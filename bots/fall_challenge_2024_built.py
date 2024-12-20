import numpy as np
import sys
from enum import Enum
from typing import List

class Attrs(Enum):
    X = 0
    Y = 1
    TYPE = 2
    OWNER = 3
    ORGAN_ID = 4
    ORGAN_DIR = 5
    ORGAN_PARENT_ID = 6
    ORGAN_ROOT_ID = 7

class Type(Enum):
    WALL = 0
    ROOT = 1
    BASIC = 2
    TENTACLE = 3
    HARVESTER = 4
    SPORER = 5
    A = 6
    B = 7
    C = 8
    D = 9

class Direction(Enum):
    N = 0
    E = 1
    S = 2
    W = 3
    X = 4

class GameLoop:
    __slots__ = ('init_inputs', 'nb_turns', 'turns_inputs', 'width', 'height', 'entity_count', 'entities', 'my_protein_stock', 'opp_protein_stock', 'required_actions_count')
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.nb_turns: int = 0
        self.turns_inputs: List[str] = []
        self.width, self.height = [int(i) for i in self.get_init_input().split()]
        self.entity_count: int = 0
        self.entities: np.ndarray = np.zeros(shape=(0, 8))
        self.my_protein_stock: np.ndarray = np.zeros(shape=(1, 4))
        self.opp_protein_stock: np.ndarray = np.zeros(shape=(1, 4))
        self.required_actions_count: int = 0
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
        self.entities = np.zeros(shape=(self.entity_count, len(Attrs)))
        for i in range(self.entity_count):
            inputs = self.get_turn_input().split()
            self.entities[i, Attrs.X.value] = int(inputs[0])
            self.entities[i, Attrs.Y.value] = int(inputs[1])
            self.entities[i, Attrs.TYPE.value] = Type[inputs[2]].value
            self.entities[i, Attrs.OWNER.value] = int(inputs[3])
            self.entities[i, Attrs.ORGAN_ID.value] = int(inputs[4])
            self.entities[i, Attrs.ORGAN_DIR.value] = Direction[inputs[5]].value
            self.entities[i, Attrs.ORGAN_PARENT_ID.value] = int(inputs[6])
            self.entities[i, Attrs.ORGAN_ROOT_ID.value] = int(inputs[7])
        self.my_protein_stock = np.ndarray([int(i) for i in self.get_turn_input().split()])
        self.opp_protein_stock = np.ndarray([int(i) for i in self.get_turn_input().split()])
        self.required_actions_count = int(self.get_turn_input())
        if GameLoop.LOG:
            self.print_turn_logs()

    def start(self):
        while GameLoop.RUNNING:
            self.update_assets()
            for i in range(self.required_actions_count):
                print('WAIT')
GameLoop().start()