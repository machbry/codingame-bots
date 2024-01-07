from enum import Enum
import math

import numpy as np

from botlibs.trigonometry import VectorHashMap, Vector, Point, Rotate2DMatrix

HASH_MAP_NORM2 = VectorHashMap(func_to_cache=lambda v: v.norm2)
HASH_MAP_NORM = VectorHashMap(func_to_cache=lambda v: math.sqrt(HASH_MAP_NORM2[v]))
ROTATE_2D_MATRIX = Rotate2DMatrix()

MY_OWNER = 1
FOE_OWNER = 2
OWNERS = [MY_OWNER, FOE_OWNER]

X_MIN = 0
Y_MIN = 0
X_MAX = 10000
Y_MAX = 10000
MAP_CENTER = Point(X_MAX / 2, Y_MAX / 2)
D_MAX = HASH_MAP_NORM[Vector(X_MAX, Y_MAX)]
CORNERS = {"TL": Point(X_MIN, Y_MIN),
           "TR": Point(X_MAX, Y_MIN),
           "BR": Point(X_MAX, Y_MAX),
           "BL": Point(X_MIN, Y_MAX)}
MAP_GRID_STEP = 400
MAX_X_STEP = int(round(X_MAX / MAP_GRID_STEP))
MAX_Y_STEP = int(round(Y_MAX / MAP_GRID_STEP))
MAP_INDICES = np.indices((MAX_Y_STEP, MAX_X_STEP))[1][0]
X_ONES = np.ones(shape=(1, MAP_GRID_STEP))
Y_ONES = np.ones(shape=(MAP_GRID_STEP, 1))


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


KINDS = np.array([[Kind.ZERO.value, Kind.ONE.value, Kind.TWO.value]])
COLORS = np.array([[Color.ROSE.value], [Color.YELLOW.value], [Color.GREEN.value], [Color.BLUE.value]])
EMPTY_ARRAY_CREATURES = np.zeros(shape=(len(Color), len(Kind) - 1))

SCORE_BY_KIND = np.array([[1], [2], [3]])
SCORE_FOR_FULL_COLOR = 3
SCORE_FOR_FULL_KIND = 4

ACTIVATE_COLORS = np.array([[1], [1], [1]])
ACTIVATE_KINDS = np.array([[1, 1, 1, 1]])


CREATURE_HABITATS_PER_KIND = {Kind.MONSTER.value: [X_MIN, 2500, X_MAX, 10000],
                              Kind.ZERO.value: [X_MIN, 2500, X_MAX, 5000],
                              Kind.ONE.value: [X_MIN, 5000, X_MAX, 7500],
                              Kind.TWO.value: [X_MIN, 7500, X_MAX, 10000]}

MAX_SPEED_PER_KIND = {Kind.MONSTER.value: 540,
                      Kind.ZERO.value: 400,
                      Kind.ONE.value: 400,
                      Kind.TWO.value: 400}

LIGHT_RADIUS2 = HASH_MAP_NORM2[Vector(0, 800)]
AUGMENTED_LIGHT_RADIUS2 = HASH_MAP_NORM2[Vector(0, 2000)]
EMERGENCY_RADIUS2 = HASH_MAP_NORM2[Vector(0, 500)]
DRONE_MAX_SPEED = HASH_MAP_NORM[Vector(0, 600)]
SAFE_RADIUS_FROM_MONSTERS2 = HASH_MAP_NORM2[Vector(0, 500 + 540 + 600)]
FRIGHTEN_RADIUS_FROM_DRONE = HASH_MAP_NORM[Vector(0, 1400)]

MAX_NUMBER_OF_RADAR_BLIPS_USED = 5

LIMIT_DISTANCE_FROM_EDGE_TO_DENY = HASH_MAP_NORM[Vector(1600, 0)]
SCARE_FROM_DISTANCE = HASH_MAP_NORM[Vector(400, 0)]
LIMIT_DISTANCE_TO_DENY2 = HASH_MAP_NORM2[Vector(2000, 0)]
