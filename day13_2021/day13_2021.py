from typing_extensions import Self
from typing import Optional, Sequence
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
import re

from aoc_utils import timing


class Direction(Enum):
    x = "x"
    y = "y"

    def as_axis(self):
        return 0 if self == Direction.x else 1


@dataclass(frozen=True)
class Dot:
    x: int
    y: int

    def reflect(self, direction: Direction, fold_location: int) -> Optional[Self]:
        # TODO: remove code duplication
        if direction == Direction.x:
            new_x = self._new_location(self.x, fold_location)
            if new_x is not None:
                return Dot(new_x, self.y)
            else:
                return None

        elif direction == Direction.y:
            new_y = self._new_location(self.y, fold_location)
            if new_y is not None:
                return Dot(self.x, new_y)
            else:
                return None

    @staticmethod
    def _new_location(own_value: int, fold_location: int) -> Optional[int]:
        if own_value == fold_location:
            return None
        if own_value < fold_location:
            return own_value
        return 2 * fold_location - own_value


class Dots:
    def __init__(self, dots: set[Dot]):
        self.dots: set[Dot] = dots

    def fold(self, direction: Direction, fold_location: int) -> Self:
        new_dots = set()
        for dot in self.dots:
            if (new_dot := dot.reflect(direction, fold_location)) is not None:
                new_dots.add(new_dot)
        return Dots(new_dots)

    def __len__(self):
        return len(self.dots)

    def visualize(self) -> str:
        max_x = max(dot.x for dot in self.dots)
        max_y = max(dot.y for dot in self.dots)
        lines = []
        for y in range(max_y + 1):
            line = ""
            for x in range(max_x + 1):
                if Dot(x, y) in self.dots:
                    line += "#"
                else:
                    line += "."
            lines.append(line)
        return "\n".join(lines)


def parse_file(path: Path) -> tuple[Dots, list[tuple[Direction, int]]]:
    with open(path, "r") as fin:
        text = fin.read()
    dot_lines, instructions_lines = text.split("\n\n")
    dots = set()
    for line in dot_lines.split("\n"):
        x, y = line.split(",")
        dots.add(Dot(int(x), int(y)))
    dots = Dots(dots)
    folds = re.findall(r"([x-y])=(\d+)", instructions_lines)
    folds = [(Direction(fold[0]), int(fold[1])) for fold in folds]
    return dots, folds


def part_one(path: Path) -> int:
    dots, folds = parse_file(path)
    dots = dots.fold(*folds[0])
    return len(dots)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    dots, folds = parse_file(path)
    for fold in folds:
        dots = dots.fold(*fold)
    print(dots.visualize())
    return


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
