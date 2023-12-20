from dataclasses import dataclass, field
from typing import Set

from botlibs.trigonometry import Point, Vector
from bots.fall_challenge_2023.constants import MY_OWNER, FOE_OWNER


@dataclass
class Asset:
    idt: int


@dataclass
class Scan(Asset):
    owner: int = None
    creature_idt: int = None
    saved: bool = False


@dataclass
class Unit(Asset):
    x: int = None
    y: int = None
    vx: int = None
    vy: int = None

    def position(self):
        return Point(self.x, self.y)

    def speed(self):
        return Vector(self.vx, self.vy)


@dataclass
class Creature(Unit):
    color: int = None
    kind: int = None
    visible: bool = False  # TODO : update to False if not visible for a turn
    scans_idt: Set[int] = field(default_factory=set)


@dataclass
class Drone(Unit):
    emergency: int = None
    battery: int = None


@dataclass
class MyDrone(Drone):
    owner: int = MY_OWNER


@dataclass
class FoeDrone(Drone):
    owner: int = FOE_OWNER
