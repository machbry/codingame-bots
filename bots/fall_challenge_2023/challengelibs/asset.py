from dataclasses import dataclass, field
from typing import Set

from botlibs.trigonometry import Point, Vector
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER


@dataclass(slots=True)
class Asset:
    idt: int

# surcharge Asset().__setattr__() -> to keep historic values ?
# surcharge Asset().__getattribute__() ?


@dataclass(slots=True)
class Scores:
    me: int = 0
    foe: int = 0


@dataclass(slots=True)
class Scan(Asset):
    # idt = hash((drone.owner, creature_idt))
    owner: int = None
    creature_idt: int = None
    owned_by_drones: Set[int] = field(default_factory=set)  # reset à chaque tour
    saved: bool = False
    first_saved_by: int = None


@dataclass(slots=True)
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


@dataclass(slots=True)
class Creature(Unit):
    color: int = None
    kind: int = None
    visible: bool = False
    escaped: bool = False
    saved_by_owners: Set[int] = field(default_factory=set)
    scanned_by_drones: Set[int] = field(default_factory=set)  # reset à chaque tour
    my_extra_score: int = 0
    foe_extra_score: int = 0


@dataclass(slots=True)
class Drone(Unit):
    emergency: int = None
    battery: int = None
    unsaved_scans_idt: Set[int] = field(default_factory=set)  # reset if drone.emergency == 1
    my_extra_score: int = 0
    foe_extra_score: int = 0


@dataclass(slots=True)
class MyDrone(Drone):
    owner: int = MY_OWNER


@dataclass(slots=True)
class FoeDrone(Drone):
    owner: int = FOE_OWNER


@dataclass(slots=True)
class RadarBlip(Asset):
    # idt = hash((drone_idt, creature_idt))
    drone_idt: int = None
    creature_idt: int = None
    radar: str = None
