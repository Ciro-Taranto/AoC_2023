from pathlib import Path
import re
from collections import defaultdict

from aoc_utils import timing


def count_winning_numbers(line: str) -> int:
    _, line = line.split(":")
    winning_line, owned_line = line.split("|")
    pattern = re.compile(r"(\d+)")
    winning_numbers = pattern.findall(winning_line)
    own_numbers = pattern.findall(owned_line)
    intersection = set(winning_numbers).intersection(own_numbers)
    return len(intersection)


def count_points(line: str) -> int:
    winning_numbers = count_winning_numbers(line)
    if winning_numbers:
        return 2 ** (winning_numbers - 1)
    return 0


with timing():
    with open(Path(__file__).parent / "input.txt", "r") as fin:
        total_points = sum(map(count_points, fin.readlines()))
print(total_points)


# Part 2
def count_scratchards(lines: list[str]) -> int:
    copies_owned = defaultdict(int)
    for line_id, line in enumerate(lines):
        copies_owned[line_id] += 1
        points = count_winning_numbers(line)
        for i in range(points):
            copies_owned[line_id + i + 1] += copies_owned[line_id]
    return sum(copies_owned.values())


with timing():
    with open(Path(__file__).parent / "input.txt", "r") as fin:
        lines = fin.readlines()
    print(count_scratchards(lines))
