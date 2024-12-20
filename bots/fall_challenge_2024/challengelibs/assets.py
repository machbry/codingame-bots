from enum import Enum


class EntityAttrs(Enum):
    X = 0
    Y = 1
    TYPE = 2
    OWNER = 3
    ORGAN_ID = 4
    ORGAN_DIR = 5
    ORGAN_PARENT_ID = 6
    ORGAN_ROOT_ID = 7
    NODE = 8


class EntityType(Enum):
    WALL = 0
    ROOT = 1
    BASIC = 2
    TENTACLE = 3
    HARVESTER = 4
    SPORER = 5
    A = 6
    B = 7
    C = 8
    D = 9


class Direction(Enum):
    N = 0
    E = 1
    S = 2
    W = 3
    X = 4
