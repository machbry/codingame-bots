from typing import Dict, Any
from enum import Enum

from bots.fall_challenge_2023.challengelibs.asset import Creature, MyDrone, FoeDrone, Scan, RadarBlip


class AssetType(Enum):
    CREATURE = Creature
    MYDRONE = MyDrone
    FOEDRONE = FoeDrone
    SCAN = Scan
    RADARBLIP = RadarBlip


class Singleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance


class GameAssets(Singleton):

    def __init__(self):
        self.assets: Dict[str, Dict[int, Any]] = {asset_type.name: {} for asset_type in AssetType.__iter__()}

    def create(self, asset_type: AssetType, idt: int, attr_kwargs: Dict[str, Any]):
        attr_kwargs["idt"] = idt
        asset = asset_type.value(**attr_kwargs)
        self.assets[asset_type.name][idt] = asset

    def update(self, asset_type: AssetType, idt: int, attr_kwargs: Dict[str, Any]):
        asset = self.assets[asset_type.name].get(idt)
        if asset is None:
            self.create(asset_type, idt, attr_kwargs)
        else:
            for name, value in attr_kwargs.items():
                setattr(asset, name, value)

    def get(self, asset_type: AssetType, idt: int):
        return self.assets[asset_type.name].get(idt)

    def delete(self, asset_type: AssetType, idt: int):
        del self.assets[asset_type.name][idt]

    def get_all(self, asset_type: AssetType):
        return self.assets[asset_type.name]
