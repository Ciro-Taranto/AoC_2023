from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, astuple
from aoc_utils import timing
from typing import Callable
from collections import Counter, defaultdict
from contextlib import contextmanager
from time import perf_counter
from itertools import product


@contextmanager
def inline_time(*args, **kwargs):
    start = perf_counter()
    yield None
    print(f"Elapsed {perf_counter() - start:2.4f} seconds.")


@dataclass(eq=True, unsafe_hash=True, order=True)
class XYZ:
    x: int
    y: int
    z: int

    def __sub__(self, other: XYZ) -> XYZ:
        return XYZ(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other: XYZ) -> XYZ:
        return XYZ(self.x + other.x, self.y + other.y, self.z + other.z)

    def __neg__(self) -> XYZ:
        return XYZ(*(-val for val in astuple(self)))

    def manhattan(self, other: XYZ):
        diff = self - other
        man = sum(abs(val) for val in astuple(diff))
        return man


def compose(first: Rotation, second: Rotation) -> Rotation:
    def composed(xyz: XYZ) -> XYZ:
        return second(first(xyz))

    return composed


def identity(xyz: XYZ) -> XYZ:
    return XYZ(*astuple(xyz))


def apply_n_times(rotation: Rotation, iterations: int) -> Rotation:
    composed_rotation = identity
    for _ in range(iterations):
        composed_rotation = compose(composed_rotation, rotation)
    return composed_rotation


def rotate_x(xyz: XYZ) -> XYZ:
    return XYZ(xyz.x, xyz.z, -xyz.y)


def rotate_y(xyz: XYZ) -> XYZ:
    return XYZ(-xyz.z, xyz.y, xyz.x)


def rotate_z(xyz: XYZ) -> XYZ:
    return XYZ(-xyz.y, xyz.x, xyz.z)


face_rotations = [apply_n_times(rotate_x, i) for i in range(4)] + [
    rotate_y,
    apply_n_times(rotate_y, 3),
]

all_rotations = []
for face in face_rotations:
    all_rotations.extend([compose(face, apply_n_times(rotate_z, i)) for i in range(4)])

Rotation = Callable[[XYZ], XYZ]
Distances = dict[tuple[int, int], XYZ]


class ScannerReadings:
    """
    Class mostly for caching the calculation of rotation and of distances.
    """

    def __init__(self, readings: list[XYZ], do_rotation: bool = True):
        self.all_readings = [
            [rotation(xyz) for xyz in readings]
            for rotation in all_rotations[: None if do_rotation else 1]
        ]
        self.all_distances = [
            find_distances(readings)
            for readings in self.all_readings[: None if do_rotation else 1]
        ]

    def convert_other_to_self(self, other: ScannerReadings) -> tuple[list[XYZ], XYZ]:
        my_reading = self.all_readings[0]
        my_distances = self.all_distances[0]
        for i, other_distances in enumerate(other.all_distances):
            overlap = count_overlap(my_distances, other_distances)
            if overlap >= 132:
                matching_pairs = find_matching_pairs(my_distances, other_distances)
                correspondences = find_correspondences(matching_pairs)
                return convert_coordinates(
                    my_reading, other.all_readings[i], correspondences
                )
        return None

    def merge(self, new_readings: set[XYZ]) -> ScannerReadings:
        my_readings = self.all_readings[0]
        with inline_time():
            return ScannerReadings(
                sorted(set(my_readings).union(new_readings)), do_rotation=False
            )

    def __len__(self) -> int:
        return len(self.all_readings[0])


def find_distances(readings: list[XYZ]) -> Distances:
    # Scales O(N**2) -> Bottleneck?
    distances = dict()
    for i, this in enumerate(readings):
        for j, that in enumerate(readings[i + 1 :], i + 1):
            distances[(i, j)] = that - this
            distances[(j, i)] = -distances[(i, j)]
    return distances


def find_matching_pairs(
    first: Distances, second: Distances
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    pairs = []
    if len(set(second.values())) == len(second):
        reverse = dict(zip(second.values(), second.keys()))
        for k1, v1 in first.items():
            if v1 in reverse:
                pairs.append((k1, reverse[v1]))
        return pairs
    print("Fallback strategy")
    # Fallback strategy for non unique
    for k1, v1 in first.items():
        for k2, v2 in second.items():
            if v1 == v2:
                pairs.append((k1, k2))
    return pairs


def find_correspondences(
    matching_pairs: list[tuple[tuple[int, int], tuple[int, int]]]
) -> dict[int, int]:
    correspondences = defaultdict(set)
    for (a1, b1), (a2, b2) in matching_pairs:
        correspondences[a1].add(a2)
        correspondences[b1].add(b2)
    if any(len(val) > 1 for val in correspondences.values()):
        raise ValueError
    correspondences = {key: val.pop() for key, val in correspondences.items()}
    return correspondences


def convert_coordinates(
    first: list[XYZ], second: list[XYZ], correspondences: dict[int, int]
) -> list[XYZ]:
    """
    Convert coordinates of second into coordinates of first.
    This assumes:
    - the systems are rotated correctly (enforced thanks to the 12 points).
    - any "correspondence" gives the offset;
    """
    a1, a2 = next(iter(correspondences.items()))
    offset = first[a1] - second[a2]
    return [val + offset for val in second], offset


def count_overlap(first_distances: Distances, second_distances: Distances) -> int:
    if len(set(first_distances.values())) == len(first_distances) or len(
        set(second_distances.values())
    ) == len(second_distances):
        return len(
            set(first_distances.values()).intersection(set(second_distances.values()))
        )
    # If a distance is present twice in the left set, I want to count it twice,
    # if it is present the same amount of times in the second set
    print(f"Using fallback strategy")
    c1 = Counter(first_distances.values())
    c2 = Counter(second_distances.values())
    overlap = 0
    for key, val in c1.items():
        overlap += min(val, c2.get(key, 0))
    return overlap


def explore(scanners: dict[str, list[XYZ]]) -> None:
    with inline_time():
        scanner_readings = {
            key: ScannerReadings(value) for key, value in scanners.items()
        }
    scanner_names = list(scanners)
    current_scanner = scanner_readings[scanner_names[0]]
    scanner_names = scanner_names[1:]
    all_locations = [XYZ(0, 0, 0)]
    while scanner_names:
        new_coordinates = set()
        added_scanners = set()
        for scanner_name in scanner_names:
            other_reading = scanner_readings[scanner_name]
            result = current_scanner.convert_other_to_self(other_reading)
            if result is not None:
                others_in_mine, scanner_location = result
                all_locations.append(scanner_location)
                added_scanners.add(scanner_name)
                print(f"Adding scanner: {scanner_name}")
                new_coordinates = new_coordinates.union(set(others_in_mine))
        scanner_names = [
            scanner_name
            for scanner_name in scanner_names
            if scanner_name not in added_scanners
        ]
        current_scanner = current_scanner.merge(new_coordinates)
        print(f"Current scanner has now len: {len(current_scanner)}")

    print(max(a.manhattan(b) for a, b in product(all_locations, all_locations)))


def parse_file(path: Path) -> dict[int, list[XYZ]]:
    sensor_readings = dict()
    with path.open("r") as fin:
        chunks = fin.read().split("\n\n")
    for chunk in chunks:
        lines = chunk.split("\n")
        name = lines[0].replace("-", "").strip()
        beacons = []
        for line in lines[1:]:
            beacons.append(XYZ(*map(int, line.split(","))))
        sensor_readings[name] = beacons
    return sensor_readings


def part_one(path: Path) -> int:
    readings = parse_file(path)
    explore(readings)
    return None


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)
