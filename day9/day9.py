from pathlib import Path
from aoc_utils import timing
from functools import partial


def parse_file(path: Path) -> list[list[int]]:
    with open(path, "r") as fin:
        return [[int(val) for val in line.split(" ")] for line in fin.readlines()]


def diff(sequence: list[int]) -> list[int]:
    if not sequence:
        raise ValueError(f"Empty list!")
    return list(map(lambda a, b: b - a, sequence[:-1], sequence[1:]))


def find_next_value(sequence: list[int], end: bool = True) -> int:
    differences = [
        sequence,
    ]

    while set(difference := diff(differences[-1])) != {0}:
        differences.append(difference)

    current_value = 0
    for difference in differences[::-1]:
        if end:
            current_value += difference[-1]
        else:
            current_value = difference[0] - current_value
    return current_value


def part_one(path: Path) -> int:
    sequences = parse_file(path)
    return sum(map(find_next_value, sequences))


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part 2


def part_two(path: Path) -> int:
    sequences = parse_file(path)
    find_previous_value = partial(find_next_value, end=False)
    return sum(map(find_previous_value, sequences))


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
