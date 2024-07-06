from pathlib import Path
import re
from collections import defaultdict

from aoc_utils import timing


class Segment:
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.is_aligned = (self.x1 == self.x2) or (self.y1 == self.y2)

    def expand(self) -> list[tuple[int, int]]:
        occupied = []
        direction = [
            self._get_unit_direction(self.x1, self.x2),
            self._get_unit_direction(self.y1, self.y2),
        ]
        distance = max(abs(self.x1 - self.x2), abs(self.y1 - self.y2))
        for i in range(distance + 1):
            occupied.append((self.x1 + i * direction[0], self.y1 + i * direction[1]))
        return occupied

    @staticmethod
    def _get_unit_direction(first_coordinate: int, second_coordinate: int) -> int:
        if first_coordinate == second_coordinate:
            return 0
        elif first_coordinate > second_coordinate:
            return -1
        else:
            return 1


def parse_file(path: Path) -> list[tuple[int, int, int, int]]:
    with open(path, "r") as fin:
        text = fin.read()
    pattern = re.compile(r"(\d+),(\d+) -> (\d+),(\d+)")
    entries = pattern.findall(text)
    return [(int(val) for val in entry) for entry in entries]


def visualize(occupations: dict[tuple[int, int], int]) -> None:
    max_x = max(val[0] for val in occupations.keys())
    min_x = min(val[0] for val in occupations.keys())
    max_y = max(val[0] for val in occupations.keys())
    min_y = min(val[0] for val in occupations.keys())
    lines = []
    for y in range(min_y, max_y + 1):
        line = "".join(
            [str(occupations.get((x, y), ".")) for x in range(min_x, max_x + 1)]
        )
        lines.append(line)
    print("\n".join(lines))


def part_one(path: Path) -> int:
    segments = [Segment(*vals) for vals in parse_file(path)]
    occupations = defaultdict(int)
    for segment in segments:
        if segment.is_aligned:
            for position in segment.expand():
                occupations[position] += 1
    return sum((int(val > 1) for val in occupations.values()))


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    segments = [Segment(*vals) for vals in parse_file(path)]
    occupations = defaultdict(int)
    for segment in segments:
        for position in segment.expand():
            occupations[position] += 1
    return sum((int(val > 1) for val in occupations.values()))


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
