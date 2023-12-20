from dataclasses import dataclass

from botlibs.trigonometry import Point, Vector


@dataclass
class Unit:
    idt: int
    x: int = None
    y: int = None
    vx: int = None
    vy: int = None

    def position(self):
        return Point(self.x, self.y)

    def speed(self):
        return Vector(self.vx, self.vy)

    def __hash__(self):
        return hash(self.idt)


@dataclass
class Creature(Unit):
    color: int = None,
    kind: int = None,
    visible: bool = None


@dataclass
class Drone(Unit):
    emergency: int = None,
    battery: int = None,


@dataclass
class MyDrone(Drone):
    owner: int = 1


@dataclass
class FoeDrone(Drone):
    owner: int = 2
