from dataclasses import dataclass
from typing import Union, List, Dict

from botlibs.trigonometry import Point
from bots.fall_challenge_2023.singletons import MAP_CENTER
from bots.fall_challenge_2023.challengelibs.asset import Unit, MyDrone


@dataclass
class Action:
    move: bool = True
    target: Union[Point, Unit] = MAP_CENTER
    light: bool = False
    comment: Union[int, str] = None

    def __repr__(self):
        instruction = f"MOVE {int(self.target.x)} {int(self.target.y)}" if self.move else "WAIT"
        instruction = f"{instruction} {1 if self.light else 0}"
        if self.comment:
            instruction = f"{instruction} {self.comment}"
        return instruction


def choose_action_for_drones(my_drones: Dict[int, MyDrone], actions_priorities: List[Dict[int, Action]],
                             default_action: Action):
    my_drones_action = {}

    for drone_idt, drone in my_drones.items():
        if drone.emergency == 0:
            action_chosen = None
            i, N = 0, len(actions_priorities)
            while not action_chosen and i < N:
                action_chosen = actions_priorities[i].get(drone_idt)
                i += 1
            if not action_chosen:
                action_chosen = default_action
        else:
            action_chosen = default_action

        my_drones_action[drone_idt] = action_chosen

    return my_drones_action
