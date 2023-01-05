import sys
from dataclasses import dataclass
from typing import List, Tuple, Dict
from random import randrange
from math import floor


WIDTH, HEIGHT = [int(i) for i in input().split()]
DISTANCE_MAX = WIDTH**2 + HEIGHT**2


@dataclass
class Box:
    x: int
    y: int
    scrap_amount: int = 0
    owner: int = -1
    units: int = 0
    recycler: int = 0
    can_build: int = 0
    can_spawn: int = 0
    in_range_of_recycler: int = 0


def distance_between(pos1: Box, pos2: Box):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


def closest(from_box, to_boxes: List[Box]) -> Tuple[int, Box]:
    if len(to_boxes) == 0:
        return None
    dmin = DISTANCE_MAX
    closest_box_index = 0
    for i, box in enumerate(to_boxes):
        d = distance_between(from_box, box)
        if d < dmin:
            dmin = d
            closest_box_index = i
            if d <= 1:
                break
    return closest_box_index, to_boxes[closest_box_index]


def barycentre(boxes: List[Box]) -> Box:
    N = len(boxes)
    if N == 0:
        return Box(x=int(round(WIDTH/2)), y=int(round(HEIGHT/2)))
    else:
        xsum, ysum = 0, 0
        for box in boxes:
            xsum += box.x
            ysum += box.y
        return Box(x=int(round(xsum/N)), y=int(round(ysum/N)))


def scrap_potential(center: Box, grid: Dict[int, Dict[int, Box]]) -> int:
    xc = center.x
    yc = center.y
    sc = center.scrap_amount
    scrap_coords = [(xc, yc), (xc, yc-1), (xc+1, yc), (xc, yc+1), (xc-1, yc)]
    total_scrap = 0
    for x, y in scrap_coords:
        try:
            neighbor = grid[y][x]
            if neighbor.owner == 0:
                total_scrap += min(sc, floor(neighbor.scrap_amount / (1 + neighbor.in_range_of_recycler)))
        except KeyError:
            continue
    return total_scrap


def next_to_uncontrolled(box: Box, grid: Dict[int, Dict[int, Box]]) -> bool:
    xb = box.x
    yb = box.y
    neighbors_coords = [(xb, yb-1), (xb+1, yb), (xb, yb+1), (xb-1, yb)]
    for x, y in neighbors_coords:
        try:
            neighbor = grid[y][x]
            if ((neighbor.owner != 1) and (neighbor.scrap_amount > 0)):
                return True
        except KeyError:
            continue
    return False


def next_to_mine(box: Box, grid: Dict[int, Dict[int, Box]]) -> bool:
    xb = box.x
    yb = box.y
    neighbors_coords = [(xb, yb-1), (xb+1, yb), (xb, yb+1), (xb-1, yb)]
    for x, y in neighbors_coords:
        try:
            neighbor = grid[y][x]
            if ((neighbor.owner == 1) and (neighbor.scrap_amount > 0)):
                return True
        except KeyError:
            continue
    return False


while True:
    my_matter, opp_matter = [int(i) for i in input().split()]
    current_grid: Dict[int, Dict[int, Box]] = {}
    uncontrolled_boxes = []
    my_boxes = []
    ennemy_boxes = []
    my_robots = []
    spawn_boxes = []
    build_boxes = []
    for i in range(HEIGHT):
        current_grid_row: Dict[int, Box] = {}
        for j in range(WIDTH):
            scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in input().split()]
            current_box = Box(x=j, y=i, scrap_amount=scrap_amount, owner=owner, units=owner, recycler=owner,
                              can_build=can_build, can_spawn=can_spawn, in_range_of_recycler=in_range_of_recycler)
            current_grid_row[j] = current_box

            if ((scrap_amount > 0) and (owner != 1) and (recycler == 0) and (in_range_of_recycler == 0)):
                uncontrolled_boxes.append(current_box)

            if ((owner == 1) and (recycler == 0)):
                my_boxes.append(current_box)

            if ((owner == 0) and (recycler == 0)):
                ennemy_boxes.append(current_box)

            if ((owner == 1) and (units > 0)):
                for u in range(units):
                    my_robots.append(current_box)

            if can_spawn == 1:
                spawn_boxes.append(current_box)

            if can_build == 1:
                build_boxes.append(current_box)

        current_grid[i] = current_grid_row

    actions = ""
    for my_robot in my_robots:
        if len(uncontrolled_boxes) == 0:
            break
        closest_box_index, closest_box = closest(from_box=my_robot, to_boxes=uncontrolled_boxes)
        uncontrolled_boxes.pop(closest_box_index)
        action = f"MOVE 1 {str(my_robot.x)} {str(my_robot.y)} {str(closest_box.x)} {str(closest_box.y)};"
        actions += action

    if ((len(build_boxes) > 0) and (my_matter >= 10)):
        scrap_pot_max = 10
        build_recycler = False
        best_potential_box = None
        for build_box in build_boxes:
            scrap_pot = scrap_potential(center=build_box, grid=current_grid)
            if scrap_pot > scrap_pot_max:
                scrap_pot_max = scrap_pot
                build_recycler = True
                best_potential_box = build_box
        if build_recycler:
            action = f"BUILD {best_potential_box.x} {best_potential_box.y};"
            actions += action
            my_matter += -10

    frontier_spawn_boxes = []
    for spawn_box in spawn_boxes:
        is_next_to_uncontrolled = next_to_uncontrolled(box=spawn_box, grid=current_grid)
        if is_next_to_uncontrolled:
            frontier_spawn_boxes.append(spawn_box)

    ennemy_barycentre = barycentre(ennemy_boxes)
    while ((my_matter >= 10) and len(frontier_spawn_boxes) > 0):
        spawn_box_chosen = frontier_spawn_boxes.pop(randrange(len(frontier_spawn_boxes)))
        action = f"SPAWN 1 {spawn_box_chosen.x} {spawn_box_chosen.y};"
        actions += action
        my_matter += -10

    print(actions)

    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
