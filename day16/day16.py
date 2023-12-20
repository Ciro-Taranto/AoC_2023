from __future__ import annotations
from pathlib import Path
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from tqdm import tqdm

from aoc_utils import timing


class Direction(Enum):
    RIGHT = "right"
    LEFT = "LEFT"
    UP = "up"
    DOWN = "down"


direction_changes = {}
direction_changes[Direction.RIGHT] = {
    "|": [Direction.UP, Direction.DOWN],
    "\\": [Direction.DOWN],
    "/": [Direction.UP],
}
direction_changes[Direction.LEFT] = {
    "|": [Direction.UP, Direction.DOWN],
    "\\": [Direction.UP],
    "/": [Direction.DOWN],
}
direction_changes[Direction.UP] = {
    "-": [Direction.LEFT, Direction.RIGHT],
    "\\": [Direction.LEFT],
    "/": [Direction.RIGHT],
}
direction_changes[Direction.DOWN] = {
    "-": [Direction.LEFT, Direction.RIGHT],
    "\\": [Direction.RIGHT],
    "/": [Direction.LEFT],
}


@dataclass(frozen=True)
class Ray:
    """
    Object representing a ray.
    """

    y: int
    x: int
    direction: Direction

    def move_one(self, layout: Layout) -> list[Ray]:
        """
        A function for moving the ray one step after the other
        """
        mirror = layout[self]
        if not mirror:
            new_directions = [self.direction]
        else:
            new_directions = direction_changes[self.direction][mirror]
        return [self + direction for direction in new_directions]

    def __add__(self, direction: Direction) -> Ray:
        if direction == Direction.RIGHT:
            return Ray(self.y, self.x + 1, direction)
        if direction == Direction.LEFT:
            return Ray(self.y, self.x - 1, direction)
        if direction == Direction.UP:
            return Ray(self.y - 1, self.x, direction)
        if direction == Direction.DOWN:
            return Ray(self.y + 1, self.x, direction)
        raise TypeError

    def in_bound(self, layout: Layout) -> bool:
        return (0 <= self.y < layout.n_rows) and (0 <= self.x < layout.n_cols)

    def move_many(self, layout: Layout) -> list[Ray]:
        """
        A function for moving a ray in one direction until the next splitter or deviator.
        Could be useful to speed up the calculation.
        """
        raise NotImplementedError


class Layout:
    special_chars = "|-\\/"

    def __init__(self, layout_strings: list[str]):
        self.n_rows = len(layout_strings)
        all_columns = set(map(len, layout_strings))
        self.n_cols = all_columns.pop()
        if all_columns:
            raise ValueError("Rows have different lengths")
        self.special_chars_positions = dict()
        for y, line in enumerate(layout_strings):
            for x, char in enumerate(line):
                if char in self.special_chars:
                    self.special_chars_positions[(y, x)] = char

    def __getitem__(self, ray: Ray) -> Optional[str]:
        char = self.special_chars_positions.get((ray.y, ray.x), None)
        if char == "-" and ray.direction in {Direction.LEFT, Direction.RIGHT}:
            return None
        if char == "|" and ray.direction in {Direction.UP, Direction.DOWN}:
            return None
        return char


def parse_file(path: Path) -> Layout:
    with open(path, "r") as fin:
        layout = Layout([line.strip() for line in fin.readlines()])
    return layout


def explore(layout: Layout, start_position: Ray) -> int:
    explored: set[Ray] = set()
    queue = deque([start_position])
    counter = 0
    while queue:
        counter += 1
        ray: Ray = queue.popleft()
        explored.add(ray)
        next_rays = ray.move_one(layout)
        for next_ray in next_rays:
            if next_ray not in explored and next_ray.in_bound(layout):
                queue.append(next_ray)
    energized = set((ray.y, ray.x) for ray in explored)
    return len(energized)


def part_one(path: Path) -> int:
    layout = parse_file(path)
    return explore(layout, Ray(0, 0, Direction.RIGHT))


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    layout = parse_file(path)
    possible_starts = (
        [Ray(y, 0, Direction.RIGHT) for y in range(0, layout.n_rows)]
        + [Ray(y, layout.n_cols - 1, Direction.LEFT) for y in range(0, layout.n_rows)]
        + [Ray(0, x, Direction.DOWN) for x in range(0, layout.n_cols)]
        + [Ray(layout.n_rows - 1, x, Direction.UP) for x in range(0, layout.n_cols)]
    )
    progress_bar = tqdm(total=len(possible_starts))
    max_energy = 0
    for start_ray in possible_starts:
        energy = explore(layout, start_ray)
        max_energy = max([max_energy, energy])
        progress_bar.update(1)
        progress_bar.set_postfix({"Current max": max_energy})
    return max_energy


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
