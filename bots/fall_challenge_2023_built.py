import sys
from typing import List

class GameLoop:
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = False

    def __init__(self):
        self.init_inputs: List[str] = []
        self.turns_inputs: List[str] = []
        if GameLoop.LOG:
            print(self.init_inputs, file=sys.stderr, flush=True)

    def start(self):
        while GameLoop.RUNNING:
            self.turns_inputs.append(input())
            if GameLoop.LOG:
                print(self.turns_inputs, file=sys.stderr, flush=True)
            if GameLoop.RESET_TURNS_INPUTS:
                self.turns_inputs = []
GameLoop().start()