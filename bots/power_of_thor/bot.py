import sys
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __add__(self, other):
        type_self = type(self)
        type_other = type(other)
        if type_self == type_other:
            return Vector(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        type_self = type(self)
        type_other = type(other)
        if type_self == type_other:
            return Vector(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, nombre):
        return Point(nombre * self.x, nombre * self.y)

    def __rmul__(self, nombre):
        return self * nombre

    def __truediv__(self, nombre):
        return self * (1/nombre)

    def __rtruediv__(self, nombre):
        return self / nombre

    def __repr__(self):
        return str(self.x) + ", " + str(self.y)

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

class Thor:
    def __init__(self):
        light_x, light_y, initial_tx, initial_ty = [int(i) for i in input().split()]
        self.position = Point(initial_tx, initial_ty)
        self.light_position = Point(light_x, light_y)

        self.directions = {"E" : Vector(1, 0),
                           "SE": Vector(1, 1),
                           "S": Vector(0, 1),
                           "SW": Vector(-1, 1),
                           "W": Vector(-1, 0),
                           "NW": Vector(-1, -1),
                           "N": Vector(0, -1),
                           "NE": Vector(1, -1)}

    @property
    def direction_to_light(self):
        vl = self.light_position - self.position
        return vl / (vl.norm)

    def play(self):
        vl = self.direction_to_light
        dotmax = -1
        optimal_direction = ""
        for direction, v in self.directions.items():
            dot = (v/v.norm).dot(vl)
            if dot > dotmax:
                optimal_direction = direction
                dotmax = dot

        self.position = self.position + self.directions[optimal_direction]
        print(optimal_direction)


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
# ---
# Hint: You can use the debug stream to print initialTX and initialTY, if Thor seems not follow your orders.

# light_x: the X position of the light of power
# light_y: the Y position of the light of power
# initial_tx: Thor's starting X position
# initial_ty: Thor's starting Y position
thor = Thor()

# game loop
while True:
    remaining_turns = int(input())  # The remaining amount of turns Thor can move. Do not remove this line.
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # A single line providing the move to be made: N NE E SE S SW W or NW
    thor.play()
