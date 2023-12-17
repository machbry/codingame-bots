from bots.code_vs_zombies.challengelibs.constants import HASH_MAP_NORMS
from botlibs.trigonometry import Point


class Entity:
    def __init__(self, id: int, x: int, y: int, speed: int = 0):
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
            next_position = self.position + (self.speed / distance_to_target) * vector_to_target
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
