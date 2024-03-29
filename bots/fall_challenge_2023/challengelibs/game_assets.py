from typing import Dict, Any, Union
from enum import Enum

from bots.fall_challenge_2023.challengelibs.asset import Creature, MyDrone, FoeDrone, RadarBlip, Scans, Trophies


class AssetType(Enum):
    CREATURE = Creature
    MY_DRONE = MyDrone
    FOE_DRONE = FoeDrone
    RADAR_BLIP = RadarBlip
    SCANS = Scans
    TROPHIES = Trophies


class GameAssets:

    def __init__(self):
        self.assets: Dict[str, Dict[int, Any]] = {asset_type.name: {} for asset_type in AssetType.__iter__()}

    def new_asset(self, asset_type: AssetType, idt: int):
        asset = asset_type.value(idt=idt)
        self.assets[asset_type.name][idt] = asset
        return asset

    def get(self, asset_type: AssetType, idt: int) -> Union[Creature, MyDrone, FoeDrone, RadarBlip, Scans, Trophies]:
        return self.assets[asset_type.name].get(idt)

    def delete(self, asset_type: AssetType, idt: int):
        del self.assets[asset_type.name][idt]

    def get_all(self, asset_type: AssetType):
        return self.assets[asset_type.name]
