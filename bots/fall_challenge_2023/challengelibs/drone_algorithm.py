from bots.fall_challenge_2023.challengelibs.asset import Drone, Creature
from bots.fall_challenge_2023.singletons import HASH_MAP_NORMS, AUGMENTED_LIGHT_RADIUS


def use_light_to_find_a_target(drone: Drone, target: Creature):
    battery = drone.battery
    if battery >= 10 and drone.y > 4000:
        return True
    if drone.battery >= 5:
        distance_to_target = HASH_MAP_NORMS[target.position - drone.position]
        if distance_to_target <= AUGMENTED_LIGHT_RADIUS and not target.visible:
            return True
    return False
