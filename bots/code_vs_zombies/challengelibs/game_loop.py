import sys
from typing import List

from bots.code_vs_zombies.challengelibs.constants import HASH_MAP_NORMS, D_MAX
from bots.code_vs_zombies.challengelibs.entities import Human, Zombie, Player

from botlibs.trigonometry import Point
from bots.code_vs_zombies.challengelibs.score import TurnScore


class GameLoop:
    RUNNING = True
    LOG = True
    RESET_TURNS_INPUTS = True

    def __init__(self):
        self.init_inputs: List[str] = []
        self.turns_inputs: List[str] = []
        self.nb_turns: int = 0
        if GameLoop.LOG:
            print(self.init_inputs, file=sys.stderr, flush=True)

        self.player = Player(id=0, x=0, y=0)
        self.humans = {}
        self.zombies = {}

    def closest_human_from_player(self) -> Point:
        d_min = D_MAX
        target = Point(0, 0)
        for human in self.humans.values():
            d = HASH_MAP_NORMS[(human.position - self.player.position)]
            if d <= d_min:
                d_min = d
                target = human.position
        return target

    def closest_zombie_from_player(self) -> Point:
        d_min = D_MAX
        target = Point(0, 0)
        for zombie in self.zombies.values():
            d = HASH_MAP_NORMS[(zombie.next_position - self.player.position)]
            if d <= d_min:
                d_min = d
                target = zombie.next_position
        return target

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

            target = self.closest_human_from_player()

            turn_score = TurnScore(player=self.player, humans=self.humans,
                                   zombies=self.zombies).estimate_score_for_target(target)

            if GameLoop.LOG:
                print(self.turns_inputs, file=sys.stderr, flush=True)
                print(f"nb_turns: {self.nb_turns}", file=sys.stderr, flush=True)
                print(f"turn_score: {turn_score}", file=sys.stderr, flush=True)
            if GameLoop.RESET_TURNS_INPUTS:
                self.turns_inputs = []

            print(f"{target.x} {target.y}")
