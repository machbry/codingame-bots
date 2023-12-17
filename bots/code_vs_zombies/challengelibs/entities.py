from dataclasses import dataclass

from botlibs.trigonometry import Point


@dataclass
class Entity:
    id: int
    x: int
    y: int

    @property
    def position(self) -> Point:
        return Point(self.x, self.y)


class Player(Entity):
    pass


class Human(Entity):
    pass


@dataclass
class Zombie(Entity):
    x_next: int
    y_next: int

    @property
    def next_position(self) -> Point:
        return Point(self.x_next, self.y_next)
