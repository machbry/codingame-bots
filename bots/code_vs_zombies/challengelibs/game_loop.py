import sys
from typing import List

from bots.code_vs_zombies.challengelibs.entities import Human, Zombie, Player
from botlibs.trigonometry import Vector, Point


class GameLoop:
    RUNNING = True
    LOG = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.turns_inputs: List[str] = []
        self.nb_turns: int = 0
        if GameLoop.LOG:
            print(self.init_inputs, file=sys.stderr, flush=True)

        self.x_max = 16000
        self.y_max = 9000
        self.d_max = Vector(self.x_max, self.y_max).norm

        self.player = Player(id=0, x=0, y=0)
        self.humans = {}
        self.zombies = {}

    def start(self):
        while GameLoop.RUNNING:
            self.nb_turns += 1
            x, y = [int(i) for i in input().split()]
            self.turns_inputs.append(f"{x} {y}")
            self.player = Player(id=0, x=x, y=y)

            human_count = int(input())
            self.turns_inputs.append(f"{human_count}")

            self.humans = {}
            for i in range(human_count):
                human_id, human_x, human_y = [int(j) for j in input().split()]
                self.turns_inputs.append(f"{human_id} {human_x} {human_y}")
                self.humans[human_id] = Human(id=human_id, x=human_x, y=human_y)

            zombie_count = int(input())
            self.turns_inputs.append(f"{zombie_count}")

            self.zombies = {}
            for i in range(zombie_count):
                zombie_id, zombie_x, zombie_y, zombie_xnext, zombie_ynext = [int(j) for j in input().split()]
                self.turns_inputs.append(f"{zombie_id} {zombie_x} {zombie_y} {zombie_xnext} {zombie_ynext}")
                self.zombies[zombie_id] = Zombie(id=zombie_id, x=zombie_x, y=zombie_y, x_next=zombie_xnext, y_next=zombie_ynext)

            if GameLoop.LOG:
                print(self.turns_inputs, file=sys.stderr, flush=True)
                print(self.nb_turns, file=sys.stderr, flush=True)

            d_min = self.d_max
            target = Point(0, 0)
            for zombie in self.zombies.values():
                d = (zombie.next_position - self.player.position).norm
                if d <= d_min:
                    d_min = d
                    target = zombie.next_position

            # Your destination coordinates
            print(f"{target.x} {target.y}")
