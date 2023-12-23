from dataclasses import dataclass
from typing import Union

from botlibs.trigonometry import Point
from bots.fall_challenge_2023.singletons import MAP_CENTER
from bots.fall_challenge_2023.challengelibs.asset import Unit


@dataclass
class Action:
    move: bool = True
    target: Union[Point, Unit] = MAP_CENTER
    light: bool = False
    comment: str = None

    def __repr__(self):
        instruction = f"MOVE {self.target.x} {self.target.y}" if self.move else "WAIT"
        instruction = f"{instruction} {1 if self.light else 0}"
        if self.comment:
            instruction = f"{instruction} {self.comment}"
        return instruction