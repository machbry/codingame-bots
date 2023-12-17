import sys
from typing import List


class GameLoop:
    RUNNING = True
    LOG = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.turns_inputs: List[str] = []
        self.nb_turns: int = 0
        print(self.init_inputs, file=sys.stderr, flush=True)

    def start(self):
        while GameLoop.RUNNING:
            self.nb_turns += 1
            x, y = [int(i) for i in input().split()]
            self.turns_inputs.append(f"{x} {y}")

            human_count = int(input())
            self.turns_inputs.append(f"{human_count}")

            for i in range(human_count):
                human_id, human_x, human_y = [int(j) for j in input().split()]
                self.turns_inputs.append(f"{human_id} {human_x} {human_y}")

            zombie_count = int(input())
            self.turns_inputs.append(f"{zombie_count}")
            for i in range(zombie_count):
                zombie_id, zombie_x, zombie_y, zombie_xnext, zombie_ynext = [int(j) for j in input().split()]
                self.turns_inputs.append(f"{zombie_id} {zombie_x} {zombie_y} {zombie_xnext} {zombie_ynext}")

            if GameLoop.LOG:
                print(self.turns_inputs, file=sys.stderr, flush=True)
                print(self.nb_turns, file=sys.stderr, flush=True)

            # Your destination coordinates
            print("0 0")
