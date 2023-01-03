import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set


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
    calculated_zone_id: int = None
    calculated_aggr_zone_id: int = None
    calculated_is_frontier: bool = None
    calculated_scrap_interest: int = None

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


@dataclass
class Zone:
    id: int
    boxes: List[Box] = field(default_factory=list)

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id

    def add_box(self, box: Box):
        self.boxes.append(box)

    def add_boxes(self, boxes: List[Box]):
        self.boxes.extend(boxes)


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
        box_x, box_y = box.x, box.y
        self.grid[box_y][box_x] = box

    def get_left_and_upper_neighbors(self, center_box: Box) -> Tuple[Box, Box]:
        box_x, box_y = center_box.x, center_box.y
        return self.get_box(x=box_x - 1, y=box_y), self.get_box(x=box_x, y=box_y - 1)


class ZoneAssembler:
    def __init__(self):
        self.zones: Dict[int, Zone] = {-1: Zone(-1)}
        self.connected_zones: List[Tuple[int, int]] = []

    def assign_to_zone(self, box: Box, zone_id: int):
        try:
            zone = self.zones[zone_id]
        except KeyError:
            zone = Zone(id=zone_id)
            self.zones[zone_id] = zone
        box.calculated_zone_id = zone_id
        zone.add_box(box)

    def zones_id_list(self) -> List[int]:
        return list(self.zones.keys())

    def generate_new_zone_id(self) -> int:
        return len(self.zones_id_list()) - 1

    def connect_zones(self, zone_id_1: int, zone_id_2: int):
        self.connected_zones.append((zone_id_1, zone_id_2))

    def synchronize_zone(self, center_box: Box, left_box: Box, upper_box: Box):
        new_zone_id = self.generate_new_zone_id()
        if center_box.is_grass:
            self.assign_to_zone(center_box, -1)
        elif (left_box is not None) and (upper_box is not None):
            if left_box.is_grass and upper_box.is_grass:
                self.assign_to_zone(center_box, new_zone_id)
            elif left_box.is_grass:
                self.assign_to_zone(center_box, upper_box.calculated_zone_id)
            elif upper_box.is_grass:
                self.assign_to_zone(center_box, left_box.calculated_zone_id)
            else:
                if upper_box.calculated_zone_id == left_box.calculated_zone_id:
                    self.assign_to_zone(center_box, left_box.calculated_zone_id)
                else:
                    self.assign_to_zone(center_box, left_box.calculated_zone_id)
                    self.connect_zones(left_box.calculated_zone_id, upper_box.calculated_zone_id)
        elif (left_box is None) and (upper_box is None):
            self.assign_to_zone(center_box, new_zone_id)
        elif left_box is None:
            if upper_box.is_grass:
                self.assign_to_zone(center_box, new_zone_id)
            else:
                self.assign_to_zone(center_box, upper_box.calculated_zone_id)
        elif upper_box is None:
            if left_box.is_grass:
                self.assign_to_zone(center_box, new_zone_id)
            else:
                self.assign_to_zone(center_box, left_box.calculated_zone_id)

    def get_boxes_from_zone(self, zone_id: int) -> List[Box]:
        try:
            zone = self.zones[zone_id]
            return zone.boxes
        except KeyError:
            return None


class AggregatedZones:
    def __init__(self, zone_assembler: ZoneAssembler):
        self.zone_assembler = zone_assembler

        self.aggr_zones: List[List[int]] = []
        for z_id_0, z_id_1 in self.zone_assembler.connected_zones:
            zones_connected = [z_id_0, z_id_1]
            to_remove = []
            for aggr_zone in self.aggr_zones:
                if (z_id_0 in aggr_zone) or (z_id_1 in aggr_zone):
                    zones_connected.extend(aggr_zone)
                    to_remove.append(aggr_zone)
            for aggr_zone in to_remove:
                self.aggr_zones.remove(aggr_zone)
            self.aggr_zones.append(zones_connected)
        # print([set(az) for az in self.aggr_zones], file=sys.stderr, flush=True)


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
    zone_assembler = ZoneAssembler()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            scrap_amount, owner, units, recycler, build, spawn, in_range_of_recycler = [int(k) for k in input().split()]
            current_box = Box(x=x, y=y, scrap_amount=scrap_amount, owner=owner, units=owner, recycler=owner,
                              build=build, spawn=spawn, in_range_of_recycler=in_range_of_recycler)
            current_grid.update(box=current_box)
            current_left_box, current_upper_box = current_grid.get_left_and_upper_neighbors(center_box=current_box)
            zone_assembler.synchronize_zone(center_box=current_box, left_box=current_left_box,
                                            upper_box=current_upper_box)

            # update calculated attributes for itself and its left/upper neighboors
                # zone
                # scrap_interest
                # is_frontier

            # boxes_classifier.classify_box(current_box)

    aggregated_zones = AggregatedZones(zone_assembler)

    print("WAIT")

    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
