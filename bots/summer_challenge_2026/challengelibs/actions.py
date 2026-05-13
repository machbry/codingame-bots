from bots.summer_challenge_2026.challengelibs.grid import Coordinates
from bots.summer_challenge_2026.constants import ActionType


class Action:
    __slots__ = ('action_type', 'coordinates', '_id', 'text')

    def __init__(self, action_type: ActionType, coordinates: Coordinates = None, _id: int = None, text: str = None):
        self.action_type = action_type
        self.coordinates = coordinates
        self._id = _id
        self.text = text

    def __repr__(self):
        attrs = [self.action_type, self._id, self.coordinates.x, self.coordinates.y, self.text] 
        not_null_attrs = [attr for attr in attrs if attr is not None]
        return " ".join(not_null_attrs)