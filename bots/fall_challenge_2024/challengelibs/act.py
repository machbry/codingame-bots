from dataclasses import dataclass

from bots.fall_challenge_2024.challengelibs.assets import EntityType


@dataclass
class Action:
    grow: bool = False
    id: int = 0
    x: int = 0
    y: int = 0
    t: EntityType = EntityType.BASIC

    def __repr__(self):
        if not self.grow:
            return "WAIT"

        return f"GROW {self.id} {self.x} {self.y} {self.t.name}"
