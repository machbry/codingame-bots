from bots.summer_challenge_2026.challengelibs.grid import Coordinates
from bots.summer_challenge_2026.constants import BoxType


class Box:
    __slots__ = ("coordinates", "box_type")

    def __init__(self, coordinates: Coordinates, box_type: BoxType):
        self.coordinates = coordinates
        self.box_type = box_type


class Tree:
    __slots__ = (
        "coordinates",
        "_type",
        "size",
        "health",
        "fruits",
        "cooldown",
    )

    def __init__(
        self,
        coordinates: Coordinates,
        _type: str,
        size: int,
        health: int,
        fruits: int,
        cooldown: int,
    ):
        self.coordinates = coordinates
        self._type = _type
        self.size = size
        self.health = health
        self.fruits = fruits
        self.cooldown = cooldown

    @property
    def can_be_harvested(self) -> bool:
        return self.fruits > 0

    # TODO: Quand le cooldown atteint 0, l'arbre grandit ou, s'il est à la taille maximale (4), produit des fruits. Les arbres peuvent contenir jusqu'à 3 fruits.


class Troll:
    __slots__ = (
        "_id",
        "player",
        "coordinates",
        "movement_speed",
        "carry_capacity",
        "harvest_power",
        "chop_power",
    )

    def __init__(
        self,
        _id: int,
        player: int,
        coordinates: Coordinates,
        movement_speed: int,
        carry_capacity: int,
        harvest_power: int,
        chop_power: int,
    ):
        self._id = _id
        self.player = player
        self.coordinates = coordinates
        self.movement_speed = movement_speed
        self.carry_capacity = carry_capacity
        self.harvest_power = harvest_power
        self.chop_power = chop_power

    def harvest(self, tree: Tree) -> int:
        if not tree.can_be_harvested:
            return 0

        if self.coordinates != tree.coordinates:
            return 0

        return min(self.carry_capacity, self.harvest_power, tree.fruits)

    @property
    def is_my_troll(self) -> bool:
        return self.player == 0

    # TODO: Lorsqu'un troll portant des ressources est adjacent (horizontalement ou verticalement) à son shack, DROP (déposer) transfère tous les objets portés au shack.
