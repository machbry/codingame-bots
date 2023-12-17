from typing import List, Dict

from botlibs.trigonometry import Point

from bots.code_vs_zombies.challengelibs.entities import Human, Zombie, Player
from bots.code_vs_zombies.challengelibs.constants import HASH_MAP_NORMS, D_MAX


class TurnScore:
    def __init__(self, player: Player, humans: Dict[int, Human], zombies: Dict[int, Zombie]):
        self.player = player
        self.humans = humans
        self.zombies = zombies
        self.humans_alive = len(humans)
        self.score_multipliers: List[int] = [1, 1]
        self.total_score: int = 0

        self.closest_human_to_zombies: Dict[int, Human] = {}
        for zombie in self.zombies.values():
            d_min = D_MAX
            closest_human = None
            for human in self.humans.values():
                d = HASH_MAP_NORMS[(human.position - zombie.position)]
                if d <= d_min:
                    d_min = d
                    closest_human = human
            self.closest_human_to_zombies[zombie.id] = closest_human

        self.zombies_killed: List[Zombie] = []

    def _kill(self, zombie: Zombie):
        self.total_score += 10 * (self.humans_alive ** 2) * self.score_multipliers[-1]
        self.score_multipliers.append(self.score_multipliers[-1] + self.score_multipliers[-2])
        self.zombies_killed.append(zombie)

    def estimate_score_for_target(self, target: Point):
        # player go to its target
        self.player.move_to(target)

        # zombies go to the closest human
        for zombie in self.zombies.values():
            zombie.move_to(self.closest_human_to_zombies[zombie.id].position)
            distance_with_player = HASH_MAP_NORMS[(zombie.position - self.player.position)]
            if distance_with_player <= 2000:
                self._kill(zombie)

        return self.total_score
