from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from itertools import combinations
from bisect import bisect_left
from aoc_utils import timing


@dataclass
class Coordinate:
    x: int
    y: int

    def __sub__(self, other: Coordinate) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def shift(self, row_shift: int, column_shift: int) -> Coordinate:
        return Coordinate(x=self.x + column_shift, y=self.y + row_shift)


def parse_file(path: Path) -> list[Coordinate]:
    galaxies = list()
    with open(path, "r") as fin:
        for y, line in enumerate(fin.readlines()):
            for x, char in enumerate(line.strip()):
                if char == "#":
                    galaxies.append(Coordinate(y=y, x=x))
    return galaxies


def expand_universe(galaxies: list[Coordinate], expansion: int = 1) -> list[Coordinate]:
    rows_with_galaxies = set(galaxy.y for galaxy in galaxies)
    columns_with_galaxies = set(galaxy.x for galaxy in galaxies)
    rows_without_galaxies = sorted(
        set(range(min(rows_with_galaxies), max(rows_with_galaxies))).difference(
            rows_with_galaxies
        )
    )
    columns_without_galaxies = sorted(
        set(range(min(columns_with_galaxies), max(columns_with_galaxies))).difference(
            columns_with_galaxies
        )
    )
    expanded_galaxies = list()
    for galaxy in galaxies:
        row_shift = bisect_left(rows_without_galaxies, galaxy.y) * expansion
        column_shift = bisect_left(columns_without_galaxies, galaxy.x) * expansion
        expanded_galaxies.append(
            galaxy.shift(row_shift=row_shift, column_shift=column_shift)
        )
    return expanded_galaxies


def part_one(path: Path) -> int:
    galaxies = parse_file(path)
    galaxies = expand_universe(galaxies)
    return sum([gal1 - gal2 for gal1, gal2 in combinations(galaxies, 2)])


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)


# part 2


def part_two(path: Path) -> int:
    galaxies = parse_file(path)
    galaxies = expand_universe(galaxies, expansion=999_999)
    return sum([gal1 - gal2 for gal1, gal2 in combinations(galaxies, 2)])


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
