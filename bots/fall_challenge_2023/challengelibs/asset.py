from dataclasses import dataclass, field
from typing import Set, List, Dict

import numpy as np

from botlibs.trigonometry import Point, Vector
from bots.fall_challenge_2023.singletons import MY_OWNER, FOE_OWNER


@dataclass(slots=True)
class Asset:
    idt: int


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

    def log(self):
        return f"{self.idt}"


@dataclass(slots=True)
class Creature(Unit):
    color: int = None
    kind: int = None
    habitat: List[int] = None
    visible: bool = False
    escaped: bool = False
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
    light_on: bool = False  # TODO : to update
    unsaved_creatures_idt: Set[int] = field(default_factory=set)  # reset each turn
    eval_unsaved_creatures_idt: Set[int] = field(default_factory=set)
    extra_score_with_unsaved_creatures: int = 0
    has_to_avoid: List[Creature] = field(default_factory=list)


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

    def copy(self):
        return Scans(idt=self.idt,
                     owner=self.owner,
                     saved_creatures=self.saved_creatures.copy())


@dataclass(slots=True)
class Trophies(Asset):
    creatures_win_by: np.ndarray = None
    colors_win_by: np.ndarray = None
    kinds_win_by: np.ndarray = None

    def copy(self):
        return Trophies(idt=self.idt,
                        creatures_win_by=self.creatures_win_by.copy(),
                        colors_win_by=self.colors_win_by.copy(),
                        kinds_win_by=self.kinds_win_by.copy())


@dataclass(slots=True)
class Score:
    base_creatures: int = 0
    bonus_creatures: int = 0
    base_colors: int = 0
    bonus_colors: int = 0
    base_kinds: int = 0
    bonus_kinds: int = 0

    @property
    def base(self):
        return self.base_creatures + self.base_colors + self.base_kinds

    @property
    def bonus(self):
        return self.bonus_creatures + self.bonus_colors + self.bonus_kinds

    @property
    def creatures(self):
        return self.base_creatures + self.bonus_creatures

    @property
    def colors(self):
        return self.base_colors + self.bonus_colors

    @property
    def kinds(self):
        return self.base_kinds + self.bonus_kinds

    @property
    def total(self):
        return self.base + self.bonus
