from __future__ import annotations
from pathlib import Path
import re
import dataclasses
import typing
from itertools import product
from functools import cached_property
from tqdm import tqdm
import bisect

from aoc_utils import timing

Coordinate = tuple[int, int, int]


@dataclasses.dataclass(unsafe_hash=True, frozen=False, order=True)
class Cuboid:
    status: typing.Literal["on", "off"]
    x0: int
    x1: int
    y0: int
    y1: int
    z0: int
    z1: int

    @cached_property
    def as_dict(self) -> dict:
        return {
            "x0": self.x0,
            "x1": self.x1,
            "y0": self.y0,
            "y1": self.y1,
            "z0": self.z0,
            "z1": self.z1,
        }

    def is_contained(self, other: Cuboid) -> bool:
        return all(
            [
                self.x0 >= other.x0,
                self.x1 <= other.x1,
                self.y0 >= other.y0,
                self.y1 <= other.y1,
                self.z0 >= other.z0,
                self.z1 <= other.z1,
            ]
        )

    @cached_property
    def operation(
        self,
    ) -> typing.Callable[[Coordinate, set[Coordinate]], set[Coordinate]]:
        return self._fn()

    def volume(self) -> int:
        return (
            (self.x1 - self.x0 + 1) * (self.y1 - self.y0 + 1) * (self.z1 - self.z0 + 1)
        )

    def overlaps(self, other: Cuboid) -> bool:
        self_as_dict = self.as_dict
        other_as_dict = other.as_dict
        for coordinate in "xyz":
            own0 = self_as_dict[f"{coordinate}0"]
            own1 = self_as_dict[f"{coordinate}1"]
            other0 = other_as_dict[f"{coordinate}0"]
            other1 = other_as_dict[f"{coordinate}1"]
            if own0 <= other0:
                if own1 < other0:
                    return False
            else:
                if other1 < own0:
                    return False
        return True

    def fully_overlaps(self, other: Cuboid) -> bool:
        return dataclasses.astuple(self)[1:] == dataclasses.astuple(other)[1:]

    def partially_overlaps(self, other: Cuboid) -> bool:
        return self.overlaps(other) and not self.fully_overlaps(other)

    def get_ranges(self, min_coord: int, max_coord: int):
        ranges = list()
        for coord in "xyz":
            start = max(getattr(self, f"{coord}0"), min_coord)
            end = min(getattr(self, f"{coord}1"), max_coord)
            ranges.append(range(start, end + 1))
        return ranges

    def apply(
        self, on_coordinates: set[Coordinate], min_coord: int = -50, max_coord: int = 50
    ) -> set[Coordinate]:
        # TODO: how to do this with a map / reduce (to make it less readable, obviously)
        for coordinate in product(*self.get_ranges(min_coord, max_coord)):
            on_coordinates = self.operation(coordinate, on_coordinates)
        return on_coordinates

    def _fn(self) -> typing.Callable[[set[Coordinate]], set[Coordinate]]:
        if self.status == "on":

            def func(
                coordinate: Coordinate, on_coordinates: set[Coordinate]
            ) -> set[Coordinate]:
                on_coordinates.add(coordinate)
                return on_coordinates

        elif self.status == "off":

            def func(
                coordinate: Coordinate, on_coordinates: set[Coordinate]
            ) -> set[Coordinate]:
                if coordinate in on_coordinates:
                    on_coordinates.remove(coordinate)
                return on_coordinates

        return func


def parse_file(path: Path) -> list[Cuboid]:
    pattern = re.compile(
        r"(on|off) x=(-*\d+)..(-*\d+),y=(-*\d+)..(-*\d+),z=(-*\d+)..(-*\d+)\n"
    )
    with path.open("r") as fin:
        all_values = pattern.findall(fin.read())
    cuboids = []
    for on_or_off, *coordinates in all_values:
        cuboids.append(Cuboid(on_or_off, *list(map(int, coordinates))))
    return cuboids


def part_one(path: Path) -> int:
    cuboids = parse_file(path)
    on_coordinates = set()
    for cuboid in cuboids:
        cuboid.apply(on_coordinates, -50, 50)
    return len(on_coordinates)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def _find_first_overlap(
    first_group: set[Cuboid], second_group: set[Cuboid], seen: set[Cuboid]
) -> typing.Optional[tuple[Cuboid, Cuboid]]:
    first_group = first_group.difference(seen)
    first_group = sorted(first_group, key=lambda x: x.x0)
    for first in first_group:
        second_group = [elem for elem in second_group if elem.x1 >= first.x0]
        second_group_filtered = filter_cuboids_by_overlap(first, second_group)
        for second in second_group_filtered:
            if first.partially_overlaps(second):
                return first, second
        seen.add(first)
    return None


def filter_cuboids_by_overlap(
    cuboid: Cuboid, others: typing.Sequence[Cuboid]
) -> list[Cuboid]:
    others = [other for other in others if other.x0 <= cuboid.x1]
    others = [other for other in others if other.y1 >= cuboid.y0]
    others = [other for other in others if other.y0 <= cuboid.y1]
    others = [other for other in others if other.z1 >= cuboid.z0]
    others = [other for other in others if other.z0 <= cuboid.z1]
    return others


def split_in_overlapping_and_non_overlapping(
    first_splits: set[Cuboid], second_splits: set[Cuboid]
) -> tuple[set[Cuboid], set[Cuboid]]:
    seen = set()
    while (
        overlap := _find_first_overlap(first_splits, second_splits, seen)
    ) is not None:
        first, second = overlap
        first_splits.remove(first)
        second_splits.remove(second)
        first_subset, second_subset = cut(first, second)
        first_splits = first_splits.union(first_subset)
        second_splits = second_splits.union(second_subset)
    return first_splits, second_splits


def cut(first: Cuboid, second: Cuboid) -> tuple[set[Cuboid], set[Cuboid]]:
    for direction in "xyz":
        if (result := _cut_along_direction(first, second, direction)) is not None:
            return result
    raise ValueError(f"{first} and {second} don't seem to overlap.")


def _cut_along_direction(
    first: Cuboid, second: Cuboid, direction: typing.Literal["x", "y", "z"]
) -> typing.Optional[tuple[set[Cuboid], set[Cuboid]]]:
    f0 = getattr(first, f"{direction}0")
    f1 = getattr(first, f"{direction}1")
    s0 = getattr(second, f"{direction}0")
    s1 = getattr(second, f"{direction}1")
    if f0 == s0 and f1 == s1:
        return None
    if f0 == s0:
        if f1 < s1:  # split the second
            split1 = dataclasses.replace(second, **{f"{direction}0": f1 + 1})
            split2 = dataclasses.replace(second, **{f"{direction}1": f1})
            return {first}, {split1, split2}
        else:  # split the first
            split1 = dataclasses.replace(first, **{f"{direction}0": s1 + 1})
            split2 = dataclasses.replace(first, **{f"{direction}1": s1})
            return {split1, split2}, {second}
    if f0 < s0:  # need to split the first
        split1 = dataclasses.replace(first, **{f"{direction}0": s0})
        split2 = dataclasses.replace(first, **{f"{direction}1": s0 - 1})
        return {split1, split2}, {second}
    if s0 < f0:  # need to split the second
        split1 = dataclasses.replace(second, **{f"{direction}0": f0})
        split2 = dataclasses.replace(second, **{f"{direction}1": f0 - 1})
        return {first}, {split1, split2}
    raise ValueError(f"{f0}-{f1} and {s0}-{s1} would not split?")


def part_two(path: Path) -> int:
    cuboids = parse_file(path)
    cuboid = cuboids[0]
    on_set = set()
    pbar = tqdm(cuboids)
    for _, cuboid in enumerate(pbar):
        new_set = set()
        cuboid_split = {cuboid}
        while on_set:
            on_set_cuboid = on_set.pop()
            if on_set_cuboid.partially_overlaps(cuboid):
                cuboid_split, on_cuboid_set = split_in_overlapping_and_non_overlapping(
                    cuboid_split, {on_set_cuboid}
                )
                new_set = new_set.union(on_cuboid_set)
            else:
                new_set.add(on_set_cuboid)
        on_set = new_set
        pbar.set_postfix(
            {
                "cuboid split": len(cuboid_split),
                "on_set": len(on_set),
                "cuboid_fraction": len(cuboid_split) / (len(on_set) + 1),
            }
        )

        if cuboid.status == "on":
            for sub_cuboid in cuboid_split:
                on_set.add(sub_cuboid)
        elif cuboid.status == "off":
            for sub_cuboid in cuboid_split:
                cuboid_to_remove = dataclasses.replace(sub_cuboid, **{"status": "on"})
                if cuboid_to_remove in on_set:
                    on_set.remove(cuboid_to_remove)
        else:
            raise ValueError("Status of cuboid either on or off.")
    return sum([c.volume() for c in on_set])


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
