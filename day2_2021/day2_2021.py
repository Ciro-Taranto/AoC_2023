from pathlib import Path

from aoc_utils import timing


def parse_file(path: Path) -> list[tuple[int, int]]:
    mapping = {"forward": 0, "down": 1, "up": 1}
    commands = []
    with open(path, "r") as fin:
        for line in fin.readlines():
            dir_, steps = line.strip().split(" ")
            commands.append((mapping[dir_], int(steps) * (-1 if dir_ == "up" else 1)))
    return commands


def part_one(path: Path) -> int:
    commands = parse_file(path)
    position = [0, 0]
    for dir_, steps in commands:
        position[dir_] += steps
    return position[0] * position[1]


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two

import numba


def part_two(path: Path) -> int:
    commands = parse_file(path)
    position = [0, 0, 0]
    for dir_, steps in commands:
        if dir_ == 0:
            position[0] += steps
            position[1] += steps * position[2]
        else:
            position[2] += steps
    return position[1] * position[0]


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
