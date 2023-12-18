from botlibs.trigonometry import Point, Vector


class Unit:
    def __init__(self, _id: int, x: int, y: int, vx: int, vy: int):
        self._id = _id
        self.position = Point(x, y)
        self.speed = Vector(vx, vy)

    def __hash__(self):
        return hash(self._id)


class Fish(Unit):
    def __init__(self, _id, x, y, vx, vy, color: int, kind: int):
        super().__init__(_id, x, y, vx, vy)
        self.color = color
        self.kind = kind


class Drone(Unit):
    def __init__(self, _id, x, y, vx, vy, emergency: int, battery: int, owner: int):
        super().__init__(_id, x, y, vx, vy)
        self.emergency = emergency
        self.battery = battery
        self.owner = owner


class MyDrone(Drone):
    def __init__(self, _id, x, y, vx, vy, emergency: int, battery: int):
        super().__init__(_id, x, y, vx, vy, emergency, battery, owner=1)


class FoeDrone(Drone):
    def __init__(self, _id, x, y, vx, vy, emergency: int, battery: int):
        super().__init__(_id, x, y, vx, vy, emergency, battery, owner=2)
