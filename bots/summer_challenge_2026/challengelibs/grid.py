from bots.summer_challenge_2026.constants import BoxType


class Coordinates:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other: "Coordinates"):
        return self.x == other.x and self.y == other.y

    def is_adjacent_to(self, other: "Coordinates"):
        if self.x == other.x:
            return (self.y == other.y + 1) or (self.y == other.y - 1)

        if self.y == other.y:
            return (self.x == other.x + 1) or (self.x == other.x - 1)

        return False

    def distance_to(self, other: "Coordinates"):
        # TODO: can be wrong if there are obstacles
        return abs(self.x - other.x) + abs(self.y - other.y)


class Grid:
    __slots__ = "lines"

    def __init__(self, lines: list[str]):
        self.lines = lines

    def player_shack_coordinates(self, player: int) -> Coordinates:
        looking_for_box_type = (
            BoxType.MY_SHACK if player == 0 else BoxType.ENNEMY_SHACK
        )

        for y, line in enumerate(self.lines):
            for x, car in enumerate(line):
                if car == looking_for_box_type.value:
                    return Coordinates(x, y)
