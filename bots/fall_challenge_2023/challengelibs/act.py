from dataclasses import dataclass
from typing import Union, List

from botlibs.trigonometry import Point
from bots.fall_challenge_2023.singletons import MAP_CENTER
from bots.fall_challenge_2023.challengelibs.asset import Unit, Asset


@dataclass
class Action:
    move: bool = True
    target: Union[Point, Unit] = MAP_CENTER
    light: bool = False
    comment: Union[int, str] = None
    is_flee_action: bool = False

    def __repr__(self):
        instruction = f"MOVE {int(self.target.x)} {int(self.target.y)}" if self.move else "WAIT"
        instruction = f"{instruction} {1 if self.light else 0}"
        if self.comment:
            instruction = f"{instruction} {self.comment}"
        return instruction


def order_assets(assets: List[Asset], on_attr: str, ascending: bool = True):
    return sorted(assets, key=lambda asset: getattr(asset, on_attr), reverse=not ascending)
