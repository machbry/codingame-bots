from bots.summer_challenge_2026.challengelibs.actions import Action, drop_action, harvest_action, move_action, wait_action
from bots.summer_challenge_2026.challengelibs.assets import Tree, Troll
from bots.summer_challenge_2026.challengelibs.grid import Coordinates


def closest_tree_from_troll(
    troll: Troll,
    trees: list[Tree],
) -> Tree:
    min_distance = 999
    closest_tree = None

    for tree in trees:
        d = troll.coordinates.distance_to(tree.coordinates)
        if d < min_distance:
            min_distance = d
            closest_tree = tree

    return closest_tree


def basic_strategy_for_troll(
    troll: Troll,
    trees: list[Tree],
    troll_shack_coordinates: Coordinates,
) -> Action:
    if troll.is_inventory_full:
        if troll.can_drop(troll_shack_coordinates=troll_shack_coordinates):
            return drop_action(_id=troll._id)

        return move_action(
            _id=troll._id,
            coordinates=troll_shack_coordinates,
        )

    if len(trees) == 0:
        return wait_action()
    
    closest_tree = closest_tree_from_troll(
        troll=troll,
        trees=trees,
    )

    if troll.can_harvest(tree=closest_tree):
        return harvest_action(_id=troll._id)
    
    return move_action(
        _id=troll._id,
        coordinates=closest_tree.coordinates,
    )
