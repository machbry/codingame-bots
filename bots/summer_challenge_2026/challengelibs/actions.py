from bots.summer_challenge_2026.challengelibs.grid import Coordinates
from bots.summer_challenge_2026.constants import ActionType


class Action:
    __slots__ = ("action_type", "coordinates", "_id", "text")

    def __init__(
        self,
        action_type: ActionType = ActionType.WAIT,
        coordinates: Coordinates = None,
        _id: int = None,
        text: str = None,
    ):
        self.action_type = action_type
        self.coordinates = coordinates
        self._id = _id
        self.text = text

    def __repr__(self):
        attrs = [
            self.action_type.value,
            self._id,
            self.coordinates.x if self.coordinates else None,
            self.coordinates.y if self.coordinates else None,
            self.text,
        ]
        not_null_attrs = [str(attr) for attr in attrs if attr is not None]
        return " ".join(not_null_attrs)


def move_action(_id: int, coordinates: Coordinates) -> Action:
    return Action(
        action_type=ActionType.MOVE,
        _id=_id,
        coordinates=coordinates,
    )


def wait_action() -> Action:
    return Action(action_type=ActionType.WAIT)


def harvest_action(_id: int) -> Action:
    return Action(
        action_type=ActionType.HARVEST, 
        _id=_id,
    )

def drop_action(_id: int) -> Action:
    return Action(
        action_type=ActionType.DROP, 
        _id=_id
    )
