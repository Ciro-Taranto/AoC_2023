from pathlib import Path

from aoc_utils import timing


def parse_file(path: Path) -> ...:
    ...


def part_one(path: Path) -> int:
    parse_file(path)
    ...


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    parse_file(path)


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
