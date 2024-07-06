from pathlib import Path
from collections import defaultdict

from aoc_utils import timing


def parse_file(path: Path) -> list[int]:
    with open(path, "r") as fin:
        return list(map(int, fin.read().strip().split(",")))


def part_one(path: Path) -> int:
    # This naive algo with scale quadratically
    numbers = parse_file(path)
    locations = defaultdict(int)
    for number in numbers:
        locations[number] += 1
    fuels = []
    for i in range(min(numbers), max(numbers) + 1):
        fuel = sum(abs(i - key) * val for key, val in locations.items())
        fuels.append(fuel)
    return min(fuels)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    numbers = parse_file(path)
    locations = defaultdict(int)
    for number in numbers:
        locations[number] += 1
    fuels = []
    for i in range(min(numbers), max(numbers) + 1):
        fuel = sum(
            (abs(i - key) * (abs(i - key) + 1)) / 2 * val
            for key, val in locations.items()
        )
        fuels.append(fuel)
    return min(fuels)


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
