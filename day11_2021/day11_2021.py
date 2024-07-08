from itertools import product
from pathlib import Path
from tqdm import tqdm

from aoc_utils import timing


def parse_file(path: Path) -> dict[tuple[int, int], int]:
    energy_levels = dict()
    with open(path, "r") as fin:
        for i, line in enumerate(fin.readlines()):
            for j, char in enumerate(line.strip()):
                energy_levels[(i, j)] = int(char)
    return energy_levels


directions = {(i, j) for i, j in product((-1, 1, 0), (-1, 1, 0))}
directions.remove((0, 0))
directions = sorted(directions)


class DumboOctopusMap(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steps = 0

    def get_neighbors(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        neighbors = list()
        for direction in directions:
            neighbor = tuple([i + j for i, j in zip(position, direction)])
            if neighbor in self:
                neighbors.append(neighbor)
        return neighbors

    def do_one_step(self) -> set[tuple[int, int]]:
        flashes_at_this_round = set()
        flashes_to_process = list()
        for position in self:
            new_value = self.increase_by_one(position)
            if new_value == 0:
                flashes_at_this_round.add(position)
                flashes_to_process.append(position)
        while flashes_to_process:
            flash = flashes_to_process.pop()
            neighbors = self.get_neighbors(flash)
            for neighbor in neighbors:
                if neighbor not in flashes_at_this_round:
                    new_value = self.increase_by_one(neighbor)
                    if new_value == 0:
                        flashes_at_this_round.add(neighbor)
                        flashes_to_process.append(neighbor)
        self.steps += 1
        return flashes_at_this_round

    def increase_by_one(self, position: tuple[int, int]) -> int:
        self[position] = (self[position] + 1) % 10
        return self[position]


def part_one(path: Path) -> int:
    energy_levels = parse_file(path)
    octopus_map = DumboOctopusMap(zip(energy_levels.keys(), energy_levels.values()))
    total = 0
    for _ in tqdm(range(100)):
        flashes = octopus_map.do_one_step()
        total += len(flashes)
    return total


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    energy_levels = parse_file(path)
    octopus_map = DumboOctopusMap(zip(energy_levels.keys(), energy_levels.values()))
    while True:
        flashes = octopus_map.do_one_step()
        if len(flashes) == 100:
            return octopus_map.steps


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
