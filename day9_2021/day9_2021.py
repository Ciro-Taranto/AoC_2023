from typing import Optional
from pathlib import Path
from tqdm import tqdm
import math
from timeit import timeit

from aoc_utils import timing


def parse_file(path: Path) -> dict[tuple[int, int], int]:
    locations = dict()
    with open(path, "r") as fin:
        for i, line in enumerate(fin.readlines()):
            for j, char in enumerate(line.strip()):
                locations[(i, j)] = int(char)
    return locations


class Map(dict):
    def get_neightbors(self, position: tuple[int, int]) -> list[int]:
        neighoring_positions = self.get_neighboring_positions(position)
        neighbors = [self.get(np, 10) for np in neighoring_positions]
        return neighbors

    @staticmethod
    def get_neighboring_positions(position: tuple[int, int]) -> list[tuple[int, int]]:
        positions = list()
        for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            positions.append(tuple([c + d for c, d in zip(position, direction)]))
        return positions

    def location_risk(self, position: tuple[int, int]) -> int:
        value = self[position]
        neighbors = self.get_neightbors(position)
        if any(neighbor <= value for neighbor in neighbors):
            return 0
        return value + 1

    def get_low_points(self) -> list[tuple[int, int]]:
        return [position for position in self if self.location_risk(position) > 0]

    def find_basin(self, position: tuple[int, int]) -> set[tuple[int, int]]:
        basin = {
            position,
        }
        frontier = [position]
        while frontier:
            next_position = frontier.pop()
            for neighbor in self.get_neighboring_positions(next_position):
                if neighbor not in basin and self.get(neighbor, 9) < 9:
                    basin.add(neighbor)
                    frontier.append(neighbor)
        return basin


def part_one(path: Path) -> int:
    locations = parse_file(path)
    location_map = Map(zip(locations.keys(), locations.values()))
    return sum(location_map.location_risk(location) for location in location_map)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)


# Part two


def part_two(path: Path, log: bool = False) -> int:
    locations = parse_file(path)
    location_map = Map(zip(locations.keys(), locations.values()))
    all_low_points = location_map.get_low_points()
    basin_sizes = list()
    pbar = tqdm(all_low_points) if log else iter(all_low_points)
    for low_point in pbar:
        basin = location_map.find_basin(low_point)
        if log:
            pbar.write(str(low_point))
            pbar.write(str(basin))
            pbar.write("=========================")
        basin_sizes.append(len(basin))
    basin_sizes = sorted(basin_sizes, reverse=True)[:3]
    return math.prod(basin_sizes)


print(timeit(lambda: part_two(Path(__file__).parent / "input.txt"), number=100))
with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
