import math


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

    def dist(self, point):
        return math.dist([self.x, self.y], [point.x, point.y])


class Vector(Point):
    def __init__(self, x, y):
        super().__init__(x, y)

    def __mul__(self, nombre):
        return Vector(nombre * self.x, nombre * self.y)

    @property
    def norm(self):
        return (self.x ** 2 + self.y ** 2) ** (1/2)

    def dot(self, vector):
        return self.x * vector.x + self.y * vector.y


class Circle:
    def __init__(self, x, y, r=1):
        self.center = Point(x, y)
        self.r = r

    @property
    def x(self):
        return self.center.x

    @property
    def y(self):
        return self.center.y

    def __eq__(self, circle):
        return (self.center == circle.center) and (self.r == circle.r)