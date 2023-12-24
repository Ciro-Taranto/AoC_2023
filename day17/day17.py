from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from tqdm import tqdm
from heapq import heappop, heappush

from aoc_utils import timing

directions = {"right": (0, 1), "left": (0, -1), "up": (-1, 0), "down": (1, 0)}
possible_directions_by_dir = {
    "right": ["up", "down"],
    "left": ["up", "down"],
    "up": ["right", "left"],
    "down": ["right", "left"],
}


@dataclass(frozen=True)
class Crucible:
    y: int
    x: int
    direction: str
    steps_in_direction: int

    def possible_moves(self) -> list[Crucible]:
        possible_directions = list(possible_directions_by_dir[self.direction])
        if self.steps_in_direction < 3:
            possible_directions.append(self.direction)
        return [self + possible_direction for possible_direction in possible_directions]

    def coordinate(self) -> tuple[int, int]:
        return (self.y, self.x)

    def __add__(self, direction: str) -> Crucible:
        if direction == self.direction:
            steps = self.steps_in_direction + 1
        else:
            steps = 1
        return self.__class__(
            self.y + directions[direction][0],
            self.x + directions[direction][1],
            direction=direction,
            steps_in_direction=steps,
        )

    def __lt__(self, other: Crucible) -> bool:
        return self.coordinate() > other.coordinate()


class UltraCrucible(Crucible):
    def possible_moves(self) -> list[UltraCrucible]:
        if self.steps_in_direction < 4:
            possible_directions = [self.direction]
        elif self.steps_in_direction < 10:
            possible_directions = [self.direction] + possible_directions_by_dir[
                self.direction
            ]
        else:
            possible_directions = possible_directions_by_dir[self.direction]
        return [self + possible_direction for possible_direction in possible_directions]


def find_distance_bfs(
    start_Crucible: Crucible,
    grid: tuple[tuple[int]],
    target: tuple[int, int],
    update_every: int = 1_000,
    steps_to_stop: int = 1,
) -> int:
    count = 0
    queue: list[int, Crucible] = []
    n_rows = len(grid)
    n_cols = set(len(row) for row in grid).pop()
    progress_bar = tqdm(n_rows * n_cols)
    distances = {}

    def is_valid(Crucible: Crucible) -> bool:
        return (0 <= Crucible.y < n_rows) & (0 <= Crucible.x < n_cols)

    def Crucible_cost(Crucible: Crucible) -> int:
        return grid[Crucible.y][Crucible.x]

    for Crucible in start_Crucible.possible_moves():
        if is_valid(Crucible):
            heappush(queue, (Crucible_cost(Crucible), Crucible))

    while queue:
        count += 1
        if count % update_every == 0:
            progress_bar.update(update_every)
            progress_bar.set_postfix({"queue": len(queue), "visited": len(distances)})
        cost, Crucible = heappop(queue)
        Crucible: Crucible
        for next_Crucible in Crucible.possible_moves():
            if is_valid(next_Crucible) and next_Crucible not in distances:
                next_cost = Crucible_cost(next_Crucible)
                distance = next_cost + cost
                distances[next_Crucible] = distance
                if (
                    next_Crucible.coordinate() == target
                    and next_Crucible.steps_in_direction >= steps_to_stop
                ):
                    return distance
                heappush(queue, (distance, next_Crucible))


def parse_file(path: Path) -> tuple[tuple[int]]:
    with open(path, "r") as fin:
        grid = tuple(
            [
                tuple([int(char) for char in line.strip("\n")])
                for line in fin.readlines()
            ]
        )
    return grid


def part_one(path: Path) -> int:
    grid = parse_file(path)
    n_rows = len(grid)
    n_cols = set(len(row) for row in grid).pop()
    target = (n_rows - 1, n_cols - 1)
    start_Crucible = Crucible(0, 0, "right", 0)
    distance = find_distance_bfs(
        start_Crucible,
        grid,
        target=target,
    )
    return distance


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    grid = parse_file(path)
    n_rows = len(grid)
    n_cols = set(len(row) for row in grid).pop()
    target = (n_rows - 1, n_cols - 1)
    start_Crucible = UltraCrucible(0, 0, "right", 0)
    distance = find_distance_bfs(start_Crucible, grid, target=target, steps_to_stop=4)
    return distance


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
