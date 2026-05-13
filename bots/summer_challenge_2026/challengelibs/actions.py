from bots.summer_challenge_2026.challengelibs.grid import Coordinates
from bots.summer_challenge_2026.constants import ActionType


class Action:
    __slots__ = ('action_type', 'coordinates', '_id', 'text')

    def __init__(self, action_type: ActionType = ActionType.WAIT, coordinates: Coordinates = None, _id: int = None, text: str = None):
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
            self.text
        ] 
        not_null_attrs = [attr for attr in attrs if attr is not None]
        return " ".join(not_null_attrs)