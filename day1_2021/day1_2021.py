from pathlib import Path

from aoc_utils import timing


def parse_file(path: Path) -> list[int]:
    with open(path, "r") as fin:
        return list(map(int, fin.readlines()))


def part_one(path: Path) -> int:
    numbers = parse_file(path)
    return sum([int(a > b) for a, b in zip(numbers[1:], numbers[:-1])])


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    numbers = parse_file(path)
    return sum([int(a > b) for a, b in zip(numbers[3:], numbers[:-3])])


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
