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


class Checkpoint(Circle):
    def __init__(self, x, y, r=None):
        super().__init__(x, y, 600)

class Map:
    def __init__(self):
        self.laps = int(input())
        self.Ncp = int(input())
        self.checkpoints = []
        for i in range(self.Ncp):
            checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
            self.checkpoints.append(Checkpoint(checkpoint_x, checkpoint_y))
        self.friction = 0.85


class Pod:
    def __init__(self, map):
        self.map = map
        self.turn = 0
        self.positions = []
        self.speed = Vector(0, 0)
        self.thurst = 0
        self.boost_available = True

    @property
    def Ncp(self):
        return self.map.Ncp

    @property
    def checkpoints(self):
        return self.map.checkpoints

    @property
    def turns(self):
        return len(self.positions)

    @property
    def friction(self):
        return self.map.friction

    def update(self):
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        self.positions.append(Point(x, y))
        self.speed = Vector(vx, vy)
        self.next_check_point_id = next_check_point_id
        self.next_cp = self.checkpoints[next_check_point_id]


class MyPod(Pod):

    def __init__(self, map):
        super().__init__(map)
        self.use_boost_this_turn = False

    def update(self):
        super().update()
        self.use_boost_this_turn = False

    def plan(self):
        Ncp = self.Ncp
        checkpoints = self.checkpoints
        i = self.next_check_point_id
        speed = self.speed

        straight_line_to_cp = self.next_cp.center - self.positions[self.turns - 1]

        power = (1/self.friction)*straight_line_to_cp - self.speed
        self.to_position = self.positions[self.turns - 1] + power

        p = power.norm
        if (p > 200) and self.boost_available:
            self.use_boost_this_turn = True
            self.thurst = 100
        else:
            self.thurst = min(p, 100)

    def drive(self):
        self.plan()
        if self.use_boost_this_turn:
            print(str(math.floor(self.to_position.x)) + " " + str(math.floor(self.to_position.y)) + " BOOST")
            self.boost_available = False
        else:
            print(str(math.floor(self.to_position.x)) + " " + str(math.floor(self.to_position.y)) + " " + str(math.floor(self.thurst)))


class OpponentPod(Pod):

    def __init__(self, map):
        super().__init__(map)

    def update(self):
        super().update()


map = Map()
mypods = [MyPod(map), MyPod(map)]
opponents = [OpponentPod(map), OpponentPod(map)]

# game loop
while True:
    for pod in mypods:
        pod.update()
    for pod in opponents:
        pod.update()

    for pod in mypods:
        pod.drive()

# To debug: print("Debug messages...", file=sys.stderr, flush=True)
