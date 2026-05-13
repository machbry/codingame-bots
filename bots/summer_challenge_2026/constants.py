from enum import Enum

class BoxType(Enum):
    GRASS = '.'
    MY_SHACK = '0'
    ENNEMY_SHACK = '1'


class ActionType(Enum):
    MOVE = 'MOVE'
    HARVEST = 'HARVEST'
    DROP = 'DROP'
    WAIT = 'WAIT'
    MSG = 'MSG'
