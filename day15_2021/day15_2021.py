from pathlib import Path
from typing import Optional
from typing_extensions import Self
from heapq import heappop, heappush
from itertools import product


from aoc_utils import timing


class CaveMap:
    def __init__(self, values: dict[tuple[int, int], int]):
        self.values = values
        self.min_x = min(val[0] for val in values)
        self.max_x = max(val[0] for val in values)
        self.min_y = min(val[1] for val in values)
        self.max_y = max(val[1] for val in values)

    def expand(self, times: int) -> Self:
        if self.min_x != 0 or self.min_y != 0:
            raise ValueError
        new_values = {}
        for x, y in product(
            range((self.max_x + 1) * times), range((self.max_y + 1) * times)
        ):
            value = (
                self.values[(x % (self.max_x + 1), y % (self.max_y + 1))]
                + x // (self.max_x + 1)
                + y // (self.max_y + 1)
            )
            while value > 9:
                value -= 9
            new_values[(x, y)] = value
        return CaveMap(new_values)

    def get_neighbors(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        neighbors = list()
        for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_position = tuple(a + b for a, b in zip(position, direction))
            if new_position in self.values:
                neighbors.append(new_position)
        return neighbors

    def find_best_path_bfs(
        self, start: tuple[int, int], target: tuple[int, int], visualize: bool = False
    ) -> int:
        queue = [(0, [start])]
        visited = set()
        visited.add(start)
        while queue:
            cost, path = heappop(queue)
            last_visited = path[-1]
            neighbors = self.get_neighbors(last_visited)
            for neighbor in neighbors:
                if neighbor == target:
                    if visualize:
                        self.visualize(path + [neighbor])
                    return cost + self.values[neighbor]
                if neighbor not in visited:
                    next_cost = self.values[neighbor] + cost
                    next_path = path + [neighbor]
                    visited.add(neighbor)
                    heappush(queue, (next_cost, next_path))
        raise RuntimeError("Should not reach")

    def visualize(self, path: Optional[list[tuple[int, int]]] = None):
        lines = list()
        print(max(self.values.values()))
        for x in range(self.min_x, self.max_x + 1):
            line = ""
            for y in range(self.min_y, self.max_y + 1):
                if path is not None:
                    line += "." if (x, y) not in path else str(self.values[(x, y)])
                else:
                    line += str(self.values[(x, y)])
            lines.append(line)
        print("\n".join(lines))


def parse_file(path: Path) -> CaveMap:
    values = dict()
    with path.open("r") as fin:
        for i, line in enumerate(fin.readlines()):
            for j, char in enumerate(line.strip()):
                values[(i, j)] = int(char)
    return CaveMap(values)


def part_one(path: Path) -> int:
    cave_map = parse_file(path)
    cost = cave_map.find_best_path_bfs(
        (cave_map.min_x, cave_map.min_y),
        (cave_map.max_x, cave_map.max_y),
    )
    return cost


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    cave_map = parse_file(path)
    cave_map = cave_map.expand(5)
    cost = cave_map.find_best_path_bfs(
        (cave_map.min_x, cave_map.min_y),
        (cave_map.max_x, cave_map.max_y),
        visualize=False,
    )
    return cost


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
