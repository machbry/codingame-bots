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
        "carry_plum",
        "carry_lemon",
        "carry_apple",
        "carry_banana",
        "carry_iron",
        "carry_wood",
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
        carry_plum: int,
        carry_lemon: int,
        carry_apple: int,
        carry_banana: int,
        carry_iron: int,
        carry_wood: int,
    ):
        self._id = _id
        self.player = player
        self.coordinates = coordinates
        self.movement_speed = movement_speed
        self.carry_capacity = carry_capacity
        self.harvest_power = harvest_power
        self.chop_power = chop_power
        self.carry_plum = carry_plum
        self.carry_lemon = carry_lemon
        self.carry_apple = carry_apple
        self.carry_banana = carry_banana
        self.carry_iron = carry_iron
        self.carry_wood = carry_wood

    @property
    def is_my_troll(self) -> bool:
        return self.player == 0

    @property
    def carry_total(self) -> int:
        return (
            self.carry_plum
            + self.carry_lemon
            + self.carry_apple
            + self.carry_banana
            + self.carry_iron
            + self.carry_wood
        )

    @property
    def is_inventory_full(self) -> bool:
        return self.carry_total >= self.carry_capacity

    def can_drop(self, troll_shack_coordinates: Coordinates) -> bool:
        return (self.carry_total > 0) and (
            self.coordinates.is_adjacent_to(troll_shack_coordinates)
        )

    def can_harvest(self, tree: Tree) -> bool:
        return (
            (tree.can_be_harvested)
            and (self.coordinates == tree.coordinates)
            and (not self.is_inventory_full)
        )
