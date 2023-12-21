from dataclasses import dataclass, field
from typing import Set

from botlibs.trigonometry import Point, Vector
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER


@dataclass
class Asset:
    idt: int

# surcharge Asset().__setattr__() -> to keep historic values ?
# surcharge Asset().__getattribute__() ?


@dataclass
class Scan(Asset):
    owner: int = None
    creature_idt: int = None
    drone_idt: int = None
    saved: bool = False


@dataclass
class Unit(Asset):
    x: int = None
    y: int = None
    vx: int = None
    vy: int = None

    @property
    def position(self):
        return Point(self.x, self.y)

    @property
    def speed(self):
        return Vector(self.vx, self.vy)


@dataclass
class Creature(Unit):
    color: int = None
    kind: int = None
    visible: bool = False
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


@dataclass
class RadarBlip(Asset):
    drone_idt: int = None
    creature_idt: int = None
    radar: str = None
