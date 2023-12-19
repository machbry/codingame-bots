from typing import Dict, Union, Any

from bots.fall_challenge_2023.challengelibs.units import Creature, MyDrone, FoeDrone


class Singleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance


class GameData(Singleton):
    DATA_TYPES = [Creature, MyDrone, FoeDrone]

    def __init__(self):
        self._data_sources: Dict[str, Dict[int, Any]] = {data_type.__name__: {} for data_type in self.DATA_TYPES}

    def add(self, data: Union[Creature, MyDrone, FoeDrone]):
        source = type(data).__name__
        self._data_sources[source][data._id] = data

    def update(self, data: Union[Creature, MyDrone, FoeDrone]):
        source = type(data).__name__

    def get(self):
        pass

    def delete(self):
        pass
