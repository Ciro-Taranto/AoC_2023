"""
For this one I got really great inspiration from:    
https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb 

This is again about visualizing stuff. The structure of the problem guarantees that the distance
between any "center" is just the manhattan distance. This gives the property that we can know 
the distance of any point n-grids away can be decomposed as 
(distance in one grid + grid width * number of grids).
It should also be noted that the start position IS a center. 

Once this is understood, the last logical step is to expand point in the "edges" and points in the 
"corners"  

            CEC
            ESE
            CSC
            
The points in the edges are just expanded once for each grid step that can be reached. 
The points in the corners have different combinations since the distance can be allocated to x or y.

A lot, but really a lot, of inspiration is also taken from here: 
https://github.com/jonathanpaulson/AdventOfCode/blob/master/2023/21.py
"""

from pathlib import Path
from collections import deque
from tqdm import tqdm
from itertools import product
from functools import lru_cache

from aoc_utils import timing


class MapOfTheWorld:
    def __init__(self, lines: list[str], repeated: bool = False):
        self.repeated = repeated
        self.n_rows = len(lines)
        self.n_cols = (column_length := set(len(line) for line in lines)).pop()
        if column_length:
            raise ValueError
        self.rock_positions = set()
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                if char == "S":
                    self.start_position = (i, j)
                elif char == "#":
                    self.rock_positions.add((i, j))
                elif char != ".":
                    raise ValueError

    def get_moves(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        possible_moves = list()
        for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_position = tuple((p + d) for p, d in zip(position, direction))
            if self.is_in_bounds(new_position) and self.is_land(new_position):
                possible_moves.append(new_position)
        return possible_moves

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        if self.repeated:
            return True
        return (0 <= position[0] < self.n_rows) and (0 <= position[1] < self.n_cols)

    def is_land(self, position: tuple[int, int]) -> bool:
        return (
            position[0] % self.n_rows,
            position[1] % self.n_cols,
        ) not in self.rock_positions


def parse_file(path: Path, repeated: bool = False) -> MapOfTheWorld:
    with open(path, "r") as fin:
        input_text = fin.read()
    return MapOfTheWorld(input_text.splitlines(), repeated=repeated)


def part_one(path: Path) -> int:
    map_of_the_world = parse_file(path)
    frontier = {0: {map_of_the_world.start_position}}
    max_steps = 64
    for i in range(1, max_steps + 1):
        possible_positions_at_previous_steps = frontier[i - 1]
        frontier[i] = set()
        for position in possible_positions_at_previous_steps:
            frontier[i] = frontier[i].union(map_of_the_world.get_moves(position))
    return len(frontier[max_steps])


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def find_distances(map_of_the_world: MapOfTheWorld) -> dict[tuple[int, int], int]:
    # find distances up to a multiplier of the border
    queue = deque([(0, map_of_the_world.start_position)])
    progress_bar = tqdm()
    distances = dict()
    grid_size = map_of_the_world.n_rows
    while queue:
        progress_bar.set_postfix(
            {
                "distances": len(distances),
                "queue": len(queue),
            }
        )
        distance, position = queue.popleft()
        if position in distances:
            continue
        distances[position] = distance
        for next_position in map_of_the_world.get_moves(position):
            if (-grid_size <= next_position[0] < 2 * grid_size) and (
                -grid_size <= next_position[1] < 2 * grid_size
            ):
                queue.append((distance + 1, next_position))
    return distances


@lru_cache(maxsize=2**16)
def get_number_of_reachable(
    distance: int, steps: int, n_rows: int, is_corner: bool
) -> int:
    """
    Number of possible way to reach an element at distance d, considering that it can be reached
    within d + n_rows * grid_steps on a grid at a manhattan distance of grid_steps.
    This does not consider the distance on the first grid, i.e., the original one
    """
    parity = steps % 2
    grids = (steps - distance) // n_rows
    reachable = sum(
        n + 1 if is_corner else 1
        for n in range(1, grids + 1)
        if (distance + n * n_rows) % 2 == parity
    )
    return reachable


def part_two(path: Path) -> int:
    map_of_the_world = parse_file(path, repeated=True)
    n_rows = map_of_the_world.n_rows
    assert map_of_the_world.n_rows == map_of_the_world.n_cols
    steps = 26501365
    parity = steps % 2
    with timing():
        distances = find_distances(map_of_the_world)
    total = 0
    for elem, distance in tqdm(distances.items()):
        y_grid_id = elem[0] // n_rows
        x_grid_id = elem[1] // n_rows
        total += int(distance % 2 == parity)
        if x_grid_id != 0 or y_grid_id != 0:
            is_corner = abs(x_grid_id) == 1 and abs(y_grid_id) == 1
            total += get_number_of_reachable(distance, steps, n_rows, is_corner)
    return total


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
