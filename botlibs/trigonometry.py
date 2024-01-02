import math
from typing import Dict, Callable, Any

import numpy as np


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __add__(self, other):
        if isinstance(other, Point):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, nombre):
        return Point(nombre * self.x, nombre * self.y)

    def __rmul__(self, nombre):
        return self * nombre

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __round__(self, n=None):
        return Point(round(self.x, n), round(self.y, n))

    def dist(self, point):
        return math.dist([self.x, self.y], [point.x, point.y])


class Vector(Point):
    def __init__(self, x, y):
        super().__init__(x, y)

    def __mul__(self, nombre):
        return Vector(nombre * self.x, nombre * self.y)

    def __round__(self, n=None):
        return Vector(round(self.x, n), round(self.y, n))

    def dot(self, vector):
        return self.x * vector.x + self.y * vector.y

    @property
    def norm2(self):
        return self.dot(self)

    @property
    def norm(self):
        return math.sqrt(self.norm2)


class VectorHashMap:
    def __init__(self, func_to_cache: Callable[[Vector], Any]):
        self.hasp_map: Dict[int, Any] = {}
        self.func_to_cache = func_to_cache

    def _apply_func(self, vector: Vector) -> Any:
        key = hash(vector)
        if key not in self.hasp_map:
            self.hasp_map[key] = self.func_to_cache(vector)
        return self.hasp_map[key]

    def __getitem__(self, vector):
        return self._apply_func(vector)


class Rotate2DMatrix:
    def __init__(self):
        self.matrix_hash_map: Dict[int, np.ndarray] = {}

    def get_rotate_matrix(self, theta: float):
        key = hash(theta % 2*math.pi)
        if key not in self.matrix_hash_map:
            cos = math.cos(theta)
            sin = math.sin(theta)
            self.matrix_hash_map[key] = np.array([[cos, -sin], [sin, cos]])
        return self.matrix_hash_map[key]

    def rotate_vector(self, vector: Vector, theta: float):
        rotation_matrix = self.get_rotate_matrix(theta)
        rotation = rotation_matrix.dot(np.array([[vector.x], [vector.y]]))
        return Vector(rotation[0][0], rotation[1][0])
