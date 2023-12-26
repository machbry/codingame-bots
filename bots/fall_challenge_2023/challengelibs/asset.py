from dataclasses import dataclass, field
from typing import Set, List, Dict

import numpy as np

from botlibs.trigonometry import Point, Vector
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER


# TODO : REPLACE SET OF ASSET IDTs BY LIST WITH ACTUAL ASSETS


@dataclass(slots=True)
class Asset:
    idt: int

# surcharge Asset().__setattr__() -> to keep historic values ?
# surcharge Asset().__getattribute__() ?


@dataclass(slots=True)
class Unit(Asset):
    x: int = None
    y: int = None
    vx: int = None
    vy: int = None
    next_x: int = None
    next_y: int = None

    @property
    def position(self):
        return Point(self.x, self.y)

    @property
    def speed(self):
        return Vector(self.vx, self.vy)

    @property
    def next_position(self):
        return Point(self.next_x, self.next_y)


@dataclass(slots=True)
class Creature(Unit):
    color: int = None
    kind: int = None
    habitat: List[int] = None
    visible: bool = False
    escaped: bool = False
    scanned_by_drones: Set[int] = field(default_factory=set)  # reset à chaque tour
    saved_by_owners: List[int] = field(default_factory=list)
    eval_saved_by_owners: List[int] = field(default_factory=list)
    extra_scores: Dict[int, int] = field(default_factory=dict)
    last_turn_visible: int = None

    @property
    def my_extra_score(self):
        return self.extra_scores[MY_OWNER]

    @property
    def foe_extra_score(self):
        return self.extra_scores[FOE_OWNER]


@dataclass(slots=True)
class Drone(Unit):
    emergency: int = None
    battery: int = None
    unsaved_creatures_idt: Set[int] = field(default_factory=set)  # reset if drone.emergency == 1
    extra_score_with_unsaved_creatures: int = 0
    has_to_flee_from: List[Creature] = field(default_factory=list)


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
    zones: List[List[int]] = field(default_factory=list)


@dataclass(slots=True)
class Scans(Asset):
    # idt = owner
    owner: int = None
    saved_creatures: np.ndarray = None
