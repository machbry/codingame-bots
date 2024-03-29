from typing import List, Dict, Tuple

import numpy as np

from bots.fall_challenge_2023.challengelibs.algorithms import order_assets
from bots.fall_challenge_2023.challengelibs.asset import Score, Creature, MyDrone, FoeDrone, Scans, Trophies
from bots.fall_challenge_2023.singletons import SCORE_BY_KIND, ACTIVATE_COLORS, \
    SCORE_FOR_FULL_COLOR, SCORE_FOR_FULL_KIND, ACTIVATE_KINDS, EMPTY_ARRAY_CREATURES, MY_OWNER, FOE_OWNER, OWNERS, Kind


def update_saved_scans(saved_creatures: np.ndarray, creature_color: int, creature_kind: int):
    creature_saved = saved_creatures[creature_color, creature_kind]
    if creature_saved == 1:
        return False
    saved_creatures[creature_color, creature_kind] = 1
    return True


def update_trophies(owner: int, saved_creatures: np.ndarray, newly_saved_creatures: np.ndarray,
                    creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray,
                    activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS,
                    score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):

    newly_completed_creatures = newly_saved_creatures == owner
    creatures_trophies_available = creatures_win_by == 0
    creatures_win_by[newly_completed_creatures & creatures_trophies_available] = owner

    completed_colors = saved_creatures.dot(activate_colors) == score_for_full_color
    colors_trophies_available = colors_win_by == 0
    colors_win_by[completed_colors & colors_trophies_available] = owner

    completed_kinds = activate_kinds.dot(saved_creatures) == score_for_full_kind
    kinds_trophies_available = kinds_win_by == 0
    kinds_win_by[completed_kinds & kinds_trophies_available] = owner


def update_trophies_for_all(my_saved_creatures: np.ndarray, foe_saved_creatures: np.ndarray,
                            my_newly_saved_creatures: np.ndarray, foe_newly_saved_creatures: np.ndarray,
                            trophies: Trophies, activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS,
                            score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):

    # TROPHIES FOR CREATURES
    creatures_win_by = trophies.creatures_win_by
    creatures_trophies_available = creatures_win_by == 0

    my_newly_completed_creatures = my_newly_saved_creatures == MY_OWNER
    foe_newly_completed_creatures = foe_newly_saved_creatures == FOE_OWNER

    creatures_win_by[creatures_trophies_available & my_newly_completed_creatures] += MY_OWNER
    creatures_win_by[creatures_trophies_available & foe_newly_completed_creatures] += FOE_OWNER

    # TROPHIES FOR COLORS
    colors_win_by = trophies.colors_win_by
    colors_trophies_available = colors_win_by == 0

    my_completed_colors = my_saved_creatures.dot(activate_colors) == score_for_full_color
    foe_completed_colors = foe_saved_creatures.dot(activate_colors) == score_for_full_color

    my_already_completed_colors = (my_saved_creatures - my_newly_saved_creatures).dot(activate_colors) == score_for_full_color
    foe_already_completed_colors = (foe_saved_creatures - foe_newly_saved_creatures).dot(activate_colors) == score_for_full_color

    my_newly_completed_colors = my_completed_colors & ~my_already_completed_colors
    foe_newly_completed_colors = foe_completed_colors & ~foe_already_completed_colors

    colors_win_by[colors_trophies_available & my_newly_completed_colors] += MY_OWNER
    colors_win_by[colors_trophies_available & foe_newly_completed_colors] += FOE_OWNER

    # TROPHIES FOR KINDS
    kinds_win_by = trophies.kinds_win_by
    kinds_trophies_available = kinds_win_by == 0

    my_completed_kinds = activate_kinds.dot(my_saved_creatures) == score_for_full_kind
    foe_completed_kinds = activate_kinds.dot(foe_saved_creatures) == score_for_full_kind

    my_already_completed_kinds = activate_kinds.dot(my_saved_creatures - my_newly_saved_creatures) == score_for_full_kind
    foe_already_completed_kinds = activate_kinds.dot(foe_saved_creatures - foe_newly_saved_creatures) == score_for_full_kind

    my_newly_completed_kinds = my_completed_kinds & ~my_already_completed_kinds
    foe_newly_completed_kinds = foe_completed_kinds & ~foe_already_completed_kinds

    kinds_win_by[kinds_trophies_available & my_newly_completed_kinds] += MY_OWNER
    kinds_win_by[kinds_trophies_available & foe_newly_completed_kinds] += FOE_OWNER


def compute_score(owner: int, saved_creatures: np.ndarray, creatures_win_by: np.ndarray,
                  colors_win_by: np.ndarray, kinds_win_by: np.ndarray, score_by_kind=SCORE_BY_KIND,
                  activate_colors=ACTIVATE_COLORS, activate_kinds=ACTIVATE_KINDS,
                  score_for_full_color=SCORE_FOR_FULL_COLOR, score_for_full_kind=SCORE_FOR_FULL_KIND):

    score = Score()

    bonus_saved_creatures = np.zeros_like(saved_creatures)
    bonus_saved_creatures[creatures_win_by == owner] = 1
    colors_activated = saved_creatures.dot(activate_colors)
    kinds_activated = activate_kinds.dot(saved_creatures)

    score.base_creatures = saved_creatures.dot(score_by_kind).sum()
    score.bonus_creatures = bonus_saved_creatures.dot(score_by_kind).sum()

    score.base_colors = colors_activated[colors_activated == score_for_full_color].sum()
    score.bonus_colors = score_for_full_color * colors_win_by[colors_win_by == owner].size

    score.base_kinds = kinds_activated[kinds_activated == score_for_full_kind].sum()
    score.bonus_kinds = score_for_full_kind * kinds_win_by[kinds_win_by == owner].size

    return score


class ScoreSimulation:
    __slots__ = ("simulation_scenario", "owners_saved_creatures", "creatures_win_by", "colors_win_by", "kinds_win_by",
                 "empty_array_creatures", "newly_saved_creatures", "owners_in_scenario", "simulation_done")

    def __init__(self, simulation_scenario: List[Tuple[int, List[Creature]]],
                 owners_saved_creatures: Dict[int, np.ndarray],
                 creatures_win_by: np.ndarray, colors_win_by: np.ndarray, kinds_win_by: np.ndarray):
        self.simulation_scenario = simulation_scenario
        self.owners_saved_creatures = {owner: saved_creatures.copy() for owner, saved_creatures
                                       in owners_saved_creatures.items()}
        self.creatures_win_by = creatures_win_by.copy()
        self.colors_win_by = colors_win_by.copy()
        self.kinds_win_by = kinds_win_by.copy()

        self.empty_array_creatures = EMPTY_ARRAY_CREATURES
        self.newly_saved_creatures = None
        self.owners_in_scenario = set()
        self.simulation_done = False

    def do_simulation(self):
        for owner, creatures_to_save in self.simulation_scenario:
            self.owners_in_scenario.add(owner)
            self.newly_saved_creatures = np.zeros_like(EMPTY_ARRAY_CREATURES)

            for creature in creatures_to_save:
                if update_saved_scans(self.owners_saved_creatures[owner], creature.color, creature.kind):
                    self.newly_saved_creatures[creature.color, creature.kind] = owner

            update_trophies(owner=owner, saved_creatures=self.owners_saved_creatures[owner],
                            newly_saved_creatures=self.newly_saved_creatures,
                            creatures_win_by=self.creatures_win_by, colors_win_by=self.colors_win_by,
                            kinds_win_by=self.kinds_win_by)

        self.simulation_done = True

    def compute_new_score(self):
        if not self.simulation_done:
            self.do_simulation()

        new_score_per_owner = {owner: compute_score(owner=owner,
                                                    saved_creatures=self.owners_saved_creatures[owner],
                                                    creatures_win_by=self.creatures_win_by,
                                                    colors_win_by=self.colors_win_by,
                                                    kinds_win_by=self.kinds_win_by)
                               for owner in self.owners_in_scenario}

        return new_score_per_owner

    def scans_and_trophies_after_simulation(self):
        if not self.simulation_done:
            self.do_simulation()

        return {'owners_saved_creatures': self.owners_saved_creatures,
                'creatures_win_by': self.creatures_win_by,
                'colors_win_by': self.colors_win_by,
                'kinds_win_by': self.kinds_win_by}


def evaluate_extra_scores_for_multiple_scenarios(creatures: Dict[int, Creature], my_drones: Dict[int, MyDrone],
                                                 foe_drones: Dict[int, FoeDrone], scans: Dict[int, Scans],
                                                 trophies: Trophies, current_owners_scores: Dict[int, Score],
                                                 my_owner=MY_OWNER, foe_owner=FOE_OWNER, owners=OWNERS,
                                                 monster_kind=Kind.MONSTER.value, score_by_kind=SCORE_BY_KIND,
                                                 score_for_full_color=SCORE_FOR_FULL_COLOR,
                                                 score_for_full_kind=SCORE_FOR_FULL_KIND):

    all_drones = [*my_drones.values(), *foe_drones.values()]
    my_drones_from_top_to_bottom = order_assets(my_drones.values(), 'y')
    foe_drones_from_top_to_bottom = order_assets(foe_drones.values(), 'y')
    ordered_drones_from_top_to_bottom = order_assets(all_drones, 'y')

    # INIT
    for creature in creatures.values():
        creature.extra_scores = {owner: 0 for owner in owners}

    owners_extra_score_with_all_unsaved_creatures = {owner: Score() for owner in owners}
    owners_max_possible_score = {owner: Score() for owner in owners}
    owners_bonus_score_left = {owner: {"shared": 0,
                                       "unshared": 0} for owner in owners}

    # REMOVE DUPLICATES IN UNSAVED CREATURES FOR EACH OWNER (THE TOP DRONE KEEPS IT)
    unsaved_creatures_idt = {}
    for owner, ordered_drones in [(my_owner, my_drones_from_top_to_bottom),
                                  (foe_owner, foe_drones_from_top_to_bottom)]:
        unsaved_creatures_idt[owner] = set()
        for drone in ordered_drones:
            drone.eval_unsaved_creatures_idt = set()
            for creature_idt in drone.unsaved_creatures_idt:
                if creature_idt not in unsaved_creatures_idt[owner]:
                    drone.eval_unsaved_creatures_idt.add(creature_idt)
                    unsaved_creatures_idt[owner].add(creature_idt)

    # SIMULATE THAT EACH DRONE SAVES ITS SCANS INDEPENDENTLY FROM EACH OTHER
    for drone in ordered_drones_from_top_to_bottom:
        owner = drone.owner
        creatures_to_save = [creatures[creature_idt] for creature_idt in drone.eval_unsaved_creatures_idt]
        drone_extra_score = 0
        drone_extra_bonus = 0

        if len(creatures_to_save) > 0:
            score_simulation = ScoreSimulation(simulation_scenario=[(owner, creatures_to_save)],
                                               owners_saved_creatures={owner: scans[owner].saved_creatures},
                                               creatures_win_by=trophies.creatures_win_by,
                                               colors_win_by=trophies.colors_win_by,
                                               kinds_win_by=trophies.kinds_win_by)

            owner_new_score = score_simulation.compute_new_score()[owner]
            drone_extra_score = owner_new_score.total - current_owners_scores[owner].total
            drone_extra_bonus = owner_new_score.bonus - current_owners_scores[owner].bonus

        drone.extra_score_with_unsaved_creatures = drone_extra_score
        drone.extra_bonus_with_unsaved_creatures = drone_extra_bonus

    # SIMULATE THAT ALL DRONES OF THE SAME OWNER GO SAVING
    for owner in owners:
        creatures_to_save = [creatures[creature_idt] for creature_idt in unsaved_creatures_idt[owner]]

        if len(creatures_to_save) > 0:
            score_simulation = ScoreSimulation(simulation_scenario=[(owner, creatures_to_save)],
                                               owners_saved_creatures={owner: scans[owner].saved_creatures},
                                               creatures_win_by=trophies.creatures_win_by,
                                               colors_win_by=trophies.colors_win_by,
                                               kinds_win_by=trophies.kinds_win_by)
            owner_extra_score = score_simulation.compute_new_score()[owner] - current_owners_scores[owner]
            owners_extra_score_with_all_unsaved_creatures[owner] = owner_extra_score

    # EVALUATE EXTRA SCORES IF CURRENT SCANS ARE SAVED (FROM TOP TO BOTTOM DRONES)
    simulation_scenario = [(drone.owner, [creatures[creature_idt]
                                          for creature_idt in drone.eval_unsaved_creatures_idt])
                           for drone in ordered_drones_from_top_to_bottom]
    owners_saved_creatures = {owner: scans[owner].saved_creatures for owner in owners}

    score_simulation = ScoreSimulation(simulation_scenario=simulation_scenario,
                                       owners_saved_creatures=owners_saved_creatures,
                                       creatures_win_by=trophies.creatures_win_by,
                                       colors_win_by=trophies.colors_win_by,
                                       kinds_win_by=trophies.kinds_win_by)

    new_owners_scores = {owner: score_simulation.compute_new_score()[owner].total for owner in owners}

    state_after_saving_current_scans = score_simulation.scans_and_trophies_after_simulation()

    # TODO : FOR FOE EVALUATE SCORE LOST IF SAVING ALL creatures_left_to_saved BUT ONE
    creatures_left_to_saved = {owner: [] for owner in owners}
    for creature in creatures.values():
        for owner in owners:
            creature_scanned_but_not_saved_by_owner = creature.idt in unsaved_creatures_idt[owner]
            if creature.kind == monster_kind:
                pass
            elif creature.escaped and not creature_scanned_but_not_saved_by_owner:
                pass
            else:
                creatures_left_to_saved[owner].append(creature)
                if not creature_scanned_but_not_saved_by_owner:
                    score_simulation = ScoreSimulation(simulation_scenario=[(owner, [creature])],
                                                       **state_after_saving_current_scans)

                    new_owner_score = score_simulation.compute_new_score()[owner].total

                    creature_extra_score = new_owner_score - new_owners_scores[owner]

                    creature.extra_scores[owner] = creature_extra_score

    # EVALUATE MAX POSSIBLE SCORES FOR EACH OWNER AND SHARED / UNSHARED BONUS LEFT TO WIN
    state_after_winning_max_possible = {}
    creatures_left_to_win = {}
    colors_left_to_win = {}
    kinds_left_to_win = {}
    for owner in owners:
        score_simulation = ScoreSimulation(simulation_scenario=[(owner, creatures_left_to_saved[owner])],
                                           owners_saved_creatures={owner: scans[owner].saved_creatures},
                                           creatures_win_by=trophies.creatures_win_by,
                                           colors_win_by=trophies.colors_win_by,
                                           kinds_win_by=trophies.kinds_win_by)

        owners_max_possible_score[owner] = score_simulation.compute_new_score()[owner]

        state_after_winning_max_possible[owner] = score_simulation.scans_and_trophies_after_simulation()

        creatures_left_to_win[owner] = (state_after_winning_max_possible[owner]['creatures_win_by'] == owner) & \
                                       (trophies.creatures_win_by != owner)
        colors_left_to_win[owner] = (state_after_winning_max_possible[owner]['colors_win_by'] == owner) & \
                                    (trophies.colors_win_by != owner)
        kinds_left_to_win[owner] = (state_after_winning_max_possible[owner]['kinds_win_by'] == owner) & \
                                   (trophies.kinds_win_by != owner)

    shared_creatures_left = (creatures_left_to_win[MY_OWNER] & creatures_left_to_win[FOE_OWNER]).astype(int)
    shared_colors_left = (colors_left_to_win[MY_OWNER] & colors_left_to_win[FOE_OWNER])
    shared_kinds_left = (kinds_left_to_win[MY_OWNER] & kinds_left_to_win[FOE_OWNER])

    bonus_shared_left = (shared_creatures_left.dot(score_by_kind).sum() + score_for_full_color * shared_colors_left.sum()
                         + score_for_full_kind * shared_kinds_left.sum())

    for owner in owners:
        owners_bonus_score_left[owner]["shared"] = bonus_shared_left
        owners_bonus_score_left[owner]["unshared"] = (owners_max_possible_score[owner].bonus - bonus_shared_left
                                                      - current_owners_scores[owner].bonus)

    return owners_extra_score_with_all_unsaved_creatures, owners_max_possible_score, owners_bonus_score_left
