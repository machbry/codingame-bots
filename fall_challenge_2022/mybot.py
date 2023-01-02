import sys
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Box:
    x: int
    y: int
    scrap_amount: int = 0
    owner: int = -1
    units: int = 0
    recycler: int = 0
    build: int = 0
    spawn: int = 0
    in_range_of_recycler: int = 0
    zone: int = -1
    scrap_interest: int = 0
    is_frontier: bool = None

    @property
    def is_grass(self) -> bool:
        return self.scrap_amount == 0

    def can_conquer(self) -> bool:
        assertions = [not self.is_grass,
                      self.owner != 1,
                      self.recycler == 0,
                      self.in_range_of_recycler == 0]
        return all(assertions)

    def can_defend(self) -> bool:
        assertions = [self.owner == 1,
                      self.recycler == 0,
                      self.in_range_of_recycler == 0]
        return all(assertions)

    def can_move(self) -> bool:
        assertions = [self.owner == 1,
                      self.units > 0]
        return all(assertions)

    def can_destroy(self) -> bool:
        assertions = [self.owner == 0,
                      self.units > 0]
        return all(assertions)

    def can_build(self) -> bool:
        assertions = [self.build == 1]
        return all(assertions)

    def can_spawn(self) -> bool:
        assertions = [self.spawn == 1]
        return all(assertions)


class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = {y: {x: Box(x=x, y=y) for x in range(width)} for y in range(height)}

    def get_box(self, x: int, y: int) -> Box:
        try:
            box = self.grid[y][x]
        except KeyError:
            box = None
        return box

    def update(self, box: Box):
        x = box.x
        y = box.y
        self.grid[y][x] = box


class BoxesClassifier:
    def __init__(self, boxes_clusters_dict: Dict):
        self.boxes_clusters_dict = boxes_clusters_dict
        self.classifier = {box_cluster_name: [] for box_cluster_name in self.boxes_clusters_dict.keys()}

    def classify_box(self, box: Box) -> None:
        for box_cluster_name, box_cluster_method in self.boxes_clusters_dict.items():
            if box_cluster_method(box):
                self.classifier[box_cluster_name].append(box)

    def get_boxes_from_cluster(self, box_cluster_name: str) -> List[Box]:
        return self.classifier[box_cluster_name]


def distance_between(box1: Box, box2: Box) -> int:
    return abs(box1.x - box2.x) + abs(box1.y - box2.y)


BOXES_CLUSTERS_DICT = {"defend": Box.can_defend,
                       "move": Box.can_move,
                       "conquer": Box.can_conquer,
                       "destroy": Box.can_destroy,
                       "spawn": Box.can_spawn,
                       "build": Box.can_build}
WIDTH, HEIGHT = [int(i) for i in input().split()]
DISTANCE_MAX = WIDTH ** 2 + HEIGHT ** 2
current_grid = Grid(width=WIDTH, height=HEIGHT)
boxes_classifier = BoxesClassifier(boxes_clusters_dict=BOXES_CLUSTERS_DICT)


while True:
    my_matter, opp_matter = [int(i) for i in input().split()]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            scrap_amount, owner, units, recycler, build, spawn, in_range_of_recycler = [int(k) for k in input().split()]
            current_box = Box(x=x, y=y, scrap_amount=scrap_amount, owner=owner, units=owner, recycler=owner,
                              build=build, spawn=spawn, in_range_of_recycler=in_range_of_recycler)
            current_grid.update(current_box)

            # update special attributes pour left and upper neighboors
                # zone
                # scrap_interest
                # is_frontier

            # only classify a box with all its neighbors infos
            # classify the upper box and not the current one
            boxes_classifier.classify_box(current_box)

    print("WAIT")

    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
