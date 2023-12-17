import sys
import math
from typing import Dict, List

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if isinstance(other, Point):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, nombre):
        return Point(nombre * self.x, nombre * self.y)

    def __rmul__(self, nombre):
        return self * nombre

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def dist(self, point):
        return math.dist([self.x, self.y], [point.x, point.y])

class Vector(Point):

    def __init__(self, x, y):
        super().__init__(x, y)

    def __mul__(self, nombre):
        return Vector(nombre * self.x, nombre * self.y)

    @property
    def norm(self):
        return (self.x ** 2 + self.y ** 2) ** (1 / 2)

    def dot(self, vector):
        return self.x * vector.x + self.y * vector.y

class HashMapNorms:

    def __init__(self):
        self.hasp_map: Dict[int, float] = {}

    def _norm_of_vector(self, vector: Vector):
        vector_hash = hash(vector)
        try:
            return self.hasp_map[vector_hash]
        except KeyError:
            norm = vector.norm
            self.hasp_map[vector_hash] = norm
            return norm

    def __getitem__(self, vector: Vector):
        return self._norm_of_vector(vector)
HASH_MAP_NORMS = HashMapNorms()
X_MAX = 16000
Y_MAX = 9000
D_MAX = HASH_MAP_NORMS[Vector(X_MAX, Y_MAX)]

class Entity:

    def __init__(self, id: int, x: int, y: int, speed: int=0):
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed

    @property
    def position(self) -> Point:
        return Point(self.x, self.y)

    def move_to(self, target: Point):
        vector_to_target = target - self.position
        distance_to_target = HASH_MAP_NORMS[vector_to_target]
        if distance_to_target <= self.speed:
            self.x = target.x
            self.y = target.y
        else:
            next_position = self.position + self.speed / distance_to_target * vector_to_target
            self.x = next_position.x
            self.y = next_position.y

class Player(Entity):

    def __init__(self, id: int, x: int, y: int):
        super().__init__(id, x, y, 1000)

class Human(Entity):
    pass

class Zombie(Entity):

    def __init__(self, id: int, x: int, y: int, x_next: int, y_next: int):
        super().__init__(id, x, y, speed=400)
        self.x_next = x_next
        self.y_next = y_next

    @property
    def next_position(self) -> Point:
        return Point(self.x_next, self.y_next)

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
                d = HASH_MAP_NORMS[human.position - zombie.position]
                if d <= d_min:
                    d_min = d
                    closest_human = human
            self.closest_human_to_zombies[zombie.id] = closest_human
        self.zombies_killed: List[Zombie] = []

    def _kill(self, zombie: Zombie):
        self.total_score += 10 * self.humans_alive ** 2 * self.score_multipliers[-1]
        self.score_multipliers.append(self.score_multipliers[-1] + self.score_multipliers[-2])
        self.zombies_killed.append(zombie)

    def estimate_score_for_target(self, target: Point):
        self.player.move_to(target)
        for zombie in self.zombies.values():
            zombie.move_to(self.closest_human_to_zombies[zombie.id].position)
            distance_with_player = HASH_MAP_NORMS[zombie.position - self.player.position]
            if distance_with_player <= 2000:
                self._kill(zombie)
        return self.total_score

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
            d = HASH_MAP_NORMS[human.position - self.player.position]
            if d <= d_min:
                d_min = d
                target = human.position
        return target

    def closest_zombie_from_player(self) -> Point:
        d_min = D_MAX
        target = Point(0, 0)
        for zombie in self.zombies.values():
            d = HASH_MAP_NORMS[zombie.next_position - self.player.position]
            if d <= d_min:
                d_min = d
                target = zombie.next_position
        return target

    def start(self):
        while GameLoop.RUNNING:
            self.nb_turns += 1
            (x, y) = [int(i) for i in input().split()]
            self.turns_inputs.append(f'{x} {y}')
            self.player = Player(id=0, x=x, y=y)
            human_count = int(input())
            self.turns_inputs.append(f'{human_count}')
            self.humans = {}
            for i in range(human_count):
                (human_id, human_x, human_y) = [int(j) for j in input().split()]
                self.turns_inputs.append(f'{human_id} {human_x} {human_y}')
                self.humans[human_id] = Human(id=human_id, x=human_x, y=human_y)
            zombie_count = int(input())
            self.turns_inputs.append(f'{zombie_count}')
            self.zombies = {}
            for i in range(zombie_count):
                (zombie_id, zombie_x, zombie_y, zombie_xnext, zombie_ynext) = [int(j) for j in input().split()]
                self.turns_inputs.append(f'{zombie_id} {zombie_x} {zombie_y} {zombie_xnext} {zombie_ynext}')
                self.zombies[zombie_id] = Zombie(id=zombie_id, x=zombie_x, y=zombie_y, x_next=zombie_xnext, y_next=zombie_ynext)
            target = self.closest_human_from_player()
            turn_score = TurnScore(player=self.player, humans=self.humans, zombies=self.zombies).estimate_score_for_target(target)
            if GameLoop.LOG:
                print(self.turns_inputs, file=sys.stderr, flush=True)
                print(f'nb_turns: {self.nb_turns}', file=sys.stderr, flush=True)
                print(f'turn_score: {turn_score}', file=sys.stderr, flush=True)
            if GameLoop.RESET_TURNS_INPUTS:
                self.turns_inputs = []
            print(f'{target.x} {target.y}')
GameLoop().start()