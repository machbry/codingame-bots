from typing import Dict, Any
from enum import Enum

from bots.fall_challenge_2023.challengelibs.units import Creature, MyDrone, FoeDrone


class DataType(Enum):
    CREATURE = Creature
    MYDRONE = MyDrone
    FOEDRONE = FoeDrone


class Singleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance


class GameData(Singleton):

    def __init__(self):
        self.data_sources: Dict[str, Dict[int, Any]] = {data_type.name: {} for data_type in DataType.__iter__()}

    def create(self, data_type: DataType, idt: int, attr_kwargs: Dict[str, Any]):
        attr_kwargs["idt"] = idt
        instance = data_type.value(**attr_kwargs)
        self.data_sources[data_type.name][idt] = instance

    def update(self, data_type: DataType, idt: int, attr_kwargs: Dict[str, Any]):
        instance = self.data_sources[data_type.name].get(idt)
        if instance is None:
            self.create(data_type, idt, attr_kwargs)
        else:
            for name, value in attr_kwargs.items():
                setattr(instance, name, value)

    def get(self, data_type: DataType, idt: int):
        return self.data_sources[data_type.name].get(idt)

    def delete(self, data_type: DataType, idt: int):
        del self.data_sources[data_type.name][idt]
