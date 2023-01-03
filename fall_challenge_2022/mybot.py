import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


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

    def get_all_boxes(self) -> List[Box]:
        all_boxes = []
        for y in range(self.height):
            for x in range(self.width):
                all_boxes.append(self.get_box(x, y))
        return all_boxes


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
        self.all_connected_ids: List[List[int]] = []
        for z_id_0, z_id_1 in self.zone_assembler.connected_zones:
            zones_connected = [z_id_0, z_id_1]
            to_remove = []
            for connected_ids in self.all_connected_ids:
                if (z_id_0 in connected_ids) or (z_id_1 in connected_ids):
                    zones_connected.extend(connected_ids)
                    to_remove.append(connected_ids)
            for ids in to_remove:
                self.all_connected_ids.remove(ids)
            self.all_connected_ids.append(zones_connected)
        self.aggregated_zones: Dict[int, Zone] = {}
        for i, zones_ids in enumerate(self.all_connected_ids):
            aggregated_zone_boxes = []
            for zone_id in zones_ids:
                boxes = self.zone_assembler.get_boxes_from_zone(zone_id)
                for box in boxes:
                    box.calculated_aggr_zone_id = i
                aggregated_zone_boxes += boxes
            self.aggregated_zones[i] = Zone(id=i, boxes=aggregated_zone_boxes)

    def get_aggregated_zone_ids(self) -> List[int]:
        return list(self.aggregated_zones.keys())

    def get_boxes_from_aggr_zone(self, aggr_zone_id: int) -> List[Box]:
        try:
            zone = self.aggregated_zones[aggr_zone_id]
            return zone.boxes
        except KeyError:
            return None


class BoxesClassifier:
    def __init__(self, boxes_clusters_dict: Dict, aggregated_zones: AggregatedZones):
        self.boxes_clusters_dict = boxes_clusters_dict
        self.aggregated_zones = aggregated_zones
        self.aggregated_zones_ids = self.aggregated_zones.get_aggregated_zone_ids()
        self.classifier = {box_cluster_name: {aggregated_zones_id: [] \
                                              for aggregated_zones_id in self.aggregated_zones_ids}
                           for box_cluster_name in self.boxes_clusters_dict.keys()}

    def classify_box(self, box: Box) -> None:
        for box_cluster_name, box_cluster_method in self.boxes_clusters_dict.items():
            if box_cluster_method(box):
                aggregated_zones_id = box.calculated_aggr_zone_id
                self.classifier[box_cluster_name][aggregated_zones_id].append(box)

    def classify_boxes(self, boxes: List[Box]):
        for box in boxes:
            if not box.is_grass:
                self.classify_box(box)

    def get_boxes_from_cluster_and_zone(self, box_cluster_name: str, aggregated_zones_id: int) -> List[Box]:
        return self.classifier[box_cluster_name][aggregated_zones_id]

    def get_boxes_from_cluster(self, box_cluster_name: str) -> List[Box]:
        boxes = []
        for aggregated_zones_id in self.aggregated_zones_ids:
            boxes.extend(self.get_boxes_from_cluster_and_zone(box_cluster_name, aggregated_zones_id))
        return boxes

    def print_boxes_clustering(self):
        for box_cluster_name in self.boxes_clusters_dict.keys():
            print(box_cluster_name, file=sys.stderr, flush=True)
            for aggregated_zones_id in self.aggregated_zones_ids:
                boxes_ids = [(box.x, box.y) for box in self.get_boxes_from_cluster_and_zone(box_cluster_name, aggregated_zones_id)]
                print((aggregated_zones_id, boxes_ids), file=sys.stderr, flush=True)


def distance_between(box1: Box, box2: Box) -> int:
    return abs(box1.x - box2.x) + abs(box1.y - box2.y)


def print_grid_boxes_attribute(grid: Grid, box_attribute_name: str):
    for y in range(grid.height):
        grid_line = ""
        for x in range(grid.width):
            box = grid.get_box(x, y)
            attr_value = str(getattr(box, box_attribute_name))
            grid_line += attr_value + " "
        print(grid_line, file=sys.stderr, flush=True)


BOXES_CLUSTERS_DICT = {"defend": Box.can_defend,
                       "move": Box.can_move,
                       "conquer": Box.can_conquer,
                       "destroy": Box.can_destroy,
                       "spawn": Box.can_spawn,
                       "build": Box.can_build}
WIDTH, HEIGHT = [int(i) for i in input().split()]
DISTANCE_MAX = WIDTH ** 2 + HEIGHT ** 2
current_grid = Grid(width=WIDTH, height=HEIGHT)


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
                # scrap_interest
                # is_frontier

    aggregated_zones = AggregatedZones(zone_assembler)
    boxes_classifier = BoxesClassifier(boxes_clusters_dict=BOXES_CLUSTERS_DICT, aggregated_zones=aggregated_zones)
    boxes_classifier.classify_boxes(current_grid.get_all_boxes())

    #boxes_classifier.print_boxes_clustering()
    # print_grid_boxes_attribute(current_grid, "calculated_aggr_zone_id")

    print("WAIT")

    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
