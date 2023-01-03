import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from math import floor
from random import randrange


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
    calculated_zone_id: int = -1
    calculated_aggr_zone_id: int = -1
    calculated_is_frontier: bool = False
    calculated_scrap_interest: int = 0
    calculated_move_interest: int = 0

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

    def spawn_frontier(self) -> bool:
        assertions = [self.spawn == 1,
                      self.calculated_is_frontier]
        return all(assertions)

    def not_mine_frontier(self) -> bool:
        assertions = [not self.is_grass,
                      self.owner != 1,
                      self.calculated_is_frontier]
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
                box = self.get_box(x, y)
                if box.calculated_aggr_zone_id != -1:
                    all_boxes.append(box)
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


def synchronize_frontier(center_box: Box, left_box: Box, upper_box: Box):
    if center_box.is_grass:
        pass
    elif (left_box is not None) and (upper_box is not None):
        if (not left_box.is_grass):
            if (left_box.owner != center_box.owner):
                left_box.calculated_is_frontier = True
                center_box.calculated_is_frontier = True
        if (not upper_box.is_grass):
            if (upper_box.owner != center_box.owner):
                upper_box.calculated_is_frontier = True
                center_box.calculated_is_frontier = True
    elif (left_box is None) and (upper_box is None):
        pass
    elif left_box is None:
        if (not upper_box.is_grass):
            if (upper_box.owner != center_box.owner):
                upper_box.calculated_is_frontier = True
                center_box.calculated_is_frontier = True
    elif upper_box is None:
        if (not left_box.is_grass):
            if (left_box.owner != center_box.owner):
                left_box.calculated_is_frontier = True
                center_box.calculated_is_frontier = True


def scrap_interest(center: Box, grid: Grid) -> int:
    xc, yc = center.x, center.y
    scrap_coords = [(xc, yc), (xc, yc - 1), (xc + 1, yc), (xc, yc + 1), (xc - 1, yc)]
    sc = center.scrap_amount
    total_scrap = 0
    for x, y in scrap_coords:
        box = grid.get_box(x, y)
        if box is None:
            continue
        if box.owner == 0:
            total_scrap += min(sc, floor(box.scrap_amount / (1 + box.in_range_of_recycler)))
    return total_scrap


def spawn_interest(center: Box, grid: Grid) -> int:
    pass


def move_interest(center: Box, grid: Grid) -> int:
    if not center.calculated_is_frontier:
        return 0
    xc, yc = center.x, center.y
    neighbors_coords = [(xc, yc - 1), (xc + 1, yc), (xc, yc + 1), (xc - 1, yc)]
    for x, y in neighbors_coords:
        box = grid.get_box(x, y)
        if box is None:
            continue
        if box.owner == 1:
            return 1
    return 0


def get_boxes_with_max_attribute_value(boxes: List[Box], box_attr_name: str, min_value: int = 0) \
        -> Tuple[List[Box], List[int]]:
    max_attr_value = min_value
    max_attr_boxes, index_in_boxes = [], []
    for index, box in enumerate(boxes):
        attr_value = getattr(box, box_attr_name)
        if attr_value > max_attr_value:
            max_attr_value = attr_value
            max_attr_boxes, index_in_boxes = [box], [index]
        elif attr_value == max_attr_value:
            max_attr_boxes.append(box)
            index_in_boxes.append(index)
    return max_attr_boxes, index_in_boxes


def remove_boxes_from_list(boxes: List[Box], boxes_to_remove: List[Box]) -> List[Box]:
    filtered_boxes = boxes.copy()
    for box_to_remove in boxes_to_remove:
        for i, box in enumerate(boxes):
            if (box.x, box.y) == (box_to_remove.x, box_to_remove.y):
                filtered_boxes.pop(i)
    return filtered_boxes


def print_grid_boxes_attribute(grid: Grid, box_attribute_name: str):
    for y in range(grid.height):
        grid_line = ""
        for x in range(grid.width):
            box = grid.get_box(x, y)
            attr_value = str(getattr(box, box_attribute_name))
            grid_line += attr_value + " "
        print(grid_line, file=sys.stderr, flush=True)


def print_boxes_xy(boxes: List[Box]):
    print([(box.x, box.y) for box in boxes], file=sys.stderr, flush=True)


BOXES_CLUSTERS_DICT = {"move": Box.can_move,
                       "build": Box.can_build,
                       "spawn_frontier": Box.spawn_frontier,
                       "not_mine_frontier": Box.not_mine_frontier}
WIDTH, HEIGHT = [int(i) for i in input().split()]
DISTANCE_MAX = WIDTH ** 2 + HEIGHT ** 2
current_grid = Grid(width=WIDTH, height=HEIGHT)


while True:
    my_matter, opp_matter = [int(i) for i in input().split()]
    zone_assembler = ZoneAssembler()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            scrap_amount, owner, units, recycler, build, spawn, in_range_of_recycler = [int(k) for k in input().split()]
            current_box = Box(x=x, y=y, scrap_amount=scrap_amount, owner=owner, units=units, recycler=recycler,
                              build=build, spawn=spawn, in_range_of_recycler=in_range_of_recycler)
            current_grid.update(box=current_box)
            current_left_box, current_upper_box = current_grid.get_left_and_upper_neighbors(center_box=current_box)
            zone_assembler.synchronize_zone(center_box=current_box, left_box=current_left_box,
                                            upper_box=current_upper_box)
            synchronize_frontier(center_box=current_box, left_box=current_left_box, upper_box=current_upper_box)

    aggregated_zones = AggregatedZones(zone_assembler)
    boxes_classifier = BoxesClassifier(boxes_clusters_dict=BOXES_CLUSTERS_DICT, aggregated_zones=aggregated_zones)
    boxes_classifier.classify_boxes(current_grid.get_all_boxes())

    # TODO: quick stats on aggregated zones

    actions = ""

    build_boxes = boxes_classifier.get_boxes_from_cluster("build")
    for box in build_boxes:
        box.calculated_scrap_interest = scrap_interest(box, current_grid)
    build_boxes_chosen = []
    while (len(build_boxes) > 0) and (my_matter >= 10) and (len(build_boxes_chosen) <= 2):
        best_build_boxes, build_boxes_index = get_boxes_with_max_attribute_value(boxes=build_boxes,
                                                                                 box_attr_name="calculated_scrap_interest",
                                                                                 min_value=10)
        if len(best_build_boxes) == 0:
            break
        i = 0
        while (i < len(best_build_boxes)) and (my_matter >= 10) and (len(build_boxes_chosen) <= 2):
            best_build_box, build_box_index = best_build_boxes[i], build_boxes_index[i]
            action = f"BUILD {best_build_box.x} {best_build_box.y};"
            actions += action
            my_matter += -10
            build_boxes.pop(build_box_index)
            build_boxes_chosen.append(best_build_box)
            i += 1

    spawn_frontier_boxes = boxes_classifier.get_boxes_from_cluster("spawn_frontier")
    spawn_frontier_boxes = remove_boxes_from_list(boxes=spawn_frontier_boxes, boxes_to_remove=build_boxes_chosen)
    # TODO : add spawn interest
    while ((my_matter >= 10) and len(spawn_frontier_boxes) > 0):
        spawn_box_chosen = spawn_frontier_boxes.pop(randrange(len(spawn_frontier_boxes)))
        action = f"SPAWN 1 {spawn_box_chosen.x} {spawn_box_chosen.y};"
        actions += action
        my_matter += -10

    for aggr_zone_id in boxes_classifier.aggregated_zones_ids:
        boxes_not_mine_frontier = boxes_classifier.get_boxes_from_cluster_and_zone("not_mine_frontier", aggr_zone_id)
        boxes_to_target = []
        for box in boxes_not_mine_frontier:
            interest = move_interest(box, current_grid) # TODO : improve move interest
            if interest > 0:
                box.calculated_move_interest = interest
                boxes_to_target.append(box)

        boxes_with_my_units = boxes_classifier.get_boxes_from_cluster_and_zone("move", aggr_zone_id)
        my_units = []
        for box in boxes_with_my_units:
            for u in range(box.units):
                my_units.append(box)

        for box_to_target in boxes_to_target:
            if len(my_units) == 0:
                break
            closest_unit_index, closest_unit = closest(from_box=box_to_target, to_boxes=my_units)
            my_units.pop(closest_unit_index)
            action = f"MOVE 1 {str(closest_unit.x)} {str(closest_unit.y)} {str(box_to_target.x)} {str(box_to_target.y)};"
            actions += action

        for my_unit in my_units:
            closest_box_index, closest_box = closest(from_box=my_unit, to_boxes=boxes_to_target)
            action = f"MOVE 1 {str(my_unit.x)} {str(my_unit.y)} {str(closest_box.x)} {str(closest_box.y)};"
            actions += action

    if actions == "":
        actions = "WAIT"
    print(actions)

    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
