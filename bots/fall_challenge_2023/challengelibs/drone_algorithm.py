from bots.fall_challenge_2023.challengelibs.asset import Drone, Creature
from bots.fall_challenge_2023.singletons import HASH_MAP_NORMS, AUGMENTED_LIGHT_RADIUS


# je vois un monstre trop proche de moi, je vais explorer dans une direction opposée
# je pousse hors du terrain un poisson déjà scanné par moi mais pas par mon adversaire
# j'explore vers une zone où je pense trouver un poisson non scanné et valant le plus de points possible
# je remonte quand mes scans me rapportent suffisement de points
# si une creature non visible est dans une zone forcement contenu dans un cercle de 2000u alors je declanche la light


def use_light_to_find_a_target(drone: Drone, target: Creature):
    battery = drone.battery
    if battery >= 10 and drone.y > 4000:
        return True
    if drone.battery >= 5:
        distance_to_target = HASH_MAP_NORMS[target.position - drone.position]
        if distance_to_target <= AUGMENTED_LIGHT_RADIUS and not target.visible:
            return True
    return False
