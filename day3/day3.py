from pathlib import Path
from aoc_utils import timing
import re


def find_all_numbers_on_line(line: str) -> list[tuple[int, int, int]]:
    result = list()
    pattern = re.compile(r"(\d+)")
    offset = 0
    while match := pattern.search(line[offset:]):
        result.append(
            (
                int(match.group()),
                match.start() + offset,
                match.end() + offset,
            )
        )
        offset += match.end()
    return result


def parse_line(line: str, excluded_chars="0123456789.") -> set[int]:
    result = set()
    for i, char in enumerate(line.strip()):
        if char not in excluded_chars:
            result.add(i)
    return result


def is_valid(
    start: int,
    end: int,
    upper_line: set[int],
    lower_line: set[int],
    current_line: set[int],
):
    valid_set = set(range(start - 1, end + 1))
    for line in [upper_line, lower_line, current_line]:
        if valid_set.intersection(line):
            return True
    return False


with timing():
    with open(Path(__file__).parent / "input.txt", "r") as fin:
        lines = fin.readlines()
    symbols = {-1: [], len(lines): []}
    numbers: dict[int, tuple[int, int, int]] = {}
    valid_numbers = []
    for i, line in enumerate(lines):
        symbols[i] = parse_line(line)
        numbers[i] = find_all_numbers_on_line(line)
    for line_id, numbers_on_line in numbers.items():
        for number, start, stop in numbers_on_line:
            if is_valid(
                start,
                stop,
                symbols[line_id + 1],
                symbols[line_id - 1],
                symbols[line_id],
            ):
                valid_numbers.append(number)
print(sum(valid_numbers))


# Part 2

with open(Path(__file__).parent / "input.txt", "r") as fin:
    lines = fin.readlines()


def find_gears_on_line(line: str) -> list[int]:
    return list(map(lambda x: x[0], filter(lambda x: x[1] == "*", enumerate(line))))


with timing():
    with open(Path(__file__).parent / "input.txt", "r") as fin:
        lines = fin.readlines()
    gears: dict[int, list[int]] = {}
    numbers: dict[int, tuple[int, int, int]] = {-1: [], len(lines): []}
    ratios = list()
    for i, line in enumerate(lines):
        gears[i] = parse_line(line)
        numbers[i] = find_all_numbers_on_line(line)
    for line_id, gears_on_line in gears.items():
        possible_neighbors = sum(
            (numbers[i] for i in range(line_id - 1, line_id + 2)), []
        )
        for gear_position in gears_on_line:
            neighbors = [
                number
                for number, start, stop in possible_neighbors
                if start - 1 <= gear_position <= stop
            ]
            if len(neighbors) == 2:
                ratios.append(neighbors[0] * neighbors[1])
print(sum(ratios))
