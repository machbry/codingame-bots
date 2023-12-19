from botlibs.trigonometry import Point, Vector


class Unit:
    def __init__(self, _id: int, x: int = None, y: int = None, vx: int = None, vy: int = None):
        self._id = _id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def position(self):
        return Point(self.x, self.y)

    def speed(self):
        return Vector(self.vx, self.vy)

    def __hash__(self):
        return hash(self._id)


class Creature(Unit):
    def __init__(self, _id, x=None, y=None, vx=None, vy=None, color=None, kind: int = None, visible: bool = None):
        super().__init__(_id, x, y, vx, vy)
        self.color = color
        self.kind = kind
        self.visible = visible


class Drone(Unit):
    def __init__(self, _id, x=None, y=None, vx=None, vy=None, emergency: int = None, battery: int = None, owner: int = None):
        super().__init__(_id, x, y, vx, vy)
        self.emergency = emergency
        self.battery = battery
        self.owner = owner


class MyDrone(Drone):
    def __init__(self, _id, x=None, y=None, vx=None, vy=None, emergency=None, battery=None):
        super().__init__(_id, x, y, vx, vy, emergency, battery, owner=1)


class FoeDrone(Drone):
    def __init__(self, _id, x=None, y=None, vx=None, vy=None, emergency=None, battery=None):
        super().__init__(_id, x, y, vx, vy, emergency, battery, owner=2)
