from enum import Enum

from botlibs.trigonometry import HashMapNorms, Vector, Point

HASH_MAP_NORMS = HashMapNorms(norm_name="norm2")

MY_OWNER = 1
FOE_OWNER = 2
OWNERS = [MY_OWNER, FOE_OWNER]

X_MIN = 0
Y_MIN = 0
X_MAX = 10000
Y_MAX = 10000
D_MAX = HASH_MAP_NORMS[Vector(X_MAX, Y_MAX)]
MAP_CENTER = Point(X_MAX / 2, Y_MAX / 2)
CORNERS = {"TL": Point(X_MIN, Y_MIN),
           "TR": Point(X_MAX, Y_MIN),
           "BR": Point(X_MAX, Y_MAX),
           "BL": Point(X_MIN, Y_MAX)}


class Kind(Enum):
    MONSTER = -1
    ZERO = 0
    ONE = 1
    TWO = 2


class Color(Enum):
    ROSE = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3


SCORE_BY_KIND = {Kind.MONSTER.value: 0,
                 Kind.ZERO.value: 1,
                 Kind.ONE.value: 2,
                 Kind.TWO.value: 3}
SCORE_FOR_FULL_COLOR = 3
SCORE_FOR_FULL_KIND = 4
SCORE_MULTIPLIER_FIRST = 2

CREATURE_HABITATS_PER_KIND = {Kind.MONSTER.value: [X_MIN, 2500, X_MAX, 10000],
                              Kind.ZERO.value: [X_MIN, 2500, X_MAX, 5000],
                              Kind.ONE.value: [X_MIN, 5000, X_MAX, 7500],
                              Kind.TWO.value: [X_MIN, 2500, X_MAX, 5000]}

LIGHT_RADIUS = HASH_MAP_NORMS[Vector(0, 800)]
AUGMENTED_LIGHT_RADIUS = HASH_MAP_NORMS[Vector(0, 2000)]
EMERGENCY_RADIUS = HASH_MAP_NORMS[Vector(0, 500)]
DRONE_SPEED = HASH_MAP_NORMS[Vector(0, 600)]
AGGRESSIVE_MONSTER_SPEED = HASH_MAP_NORMS[Vector(0, 540)]
NON_AGGRESSIVE_MONSTER_SPEED = HASH_MAP_NORMS[Vector(0, 270)]

SAFE_RADIUS_FROM_MONSTERS = HASH_MAP_NORMS[Vector(0, 500 + 540)]
FLEE_RADIUS_FROM_MONSTERS = HASH_MAP_NORMS[Vector(0, 500 + 540 + 600)]
