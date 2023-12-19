from typing import Dict

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


class UnitsData:
    def __init__(self):
        self._hash_table: Dict[int, Unit] = {}

    def __setitem__(self, key: int, unit: Unit):
        self._hash_table[key] = unit

    def __getitem__(self, unit_id: int):
        return self._hash_table.get(unit_id)

    def get(self, unit_id: int):
        # get item
        return self[unit_id]

    def post(self, unit: Unit):
        # create new item
        self[hash(unit)] = unit

    def put(self):
        # update existing item
        pass

    def delete(self):
        # delete existing item
        pass

    def patch(self):
        # partial update on an item
        pass

