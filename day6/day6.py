from pathlib import Path
import math
from aoc_utils import timing
from functools import reduce


def parse_input(file_path: Path) -> tuple[list[int], list[int]]:
    with open(file_path, "r") as fin:
        times = [int(x) for x in fin.readline().split(":")[-1].split(" ") if x]
        records = [int(x) for x in fin.readline().split(":")[-1].split(" ") if x]
    return times, records


def solve_quadratic(time: int, record: int) -> tuple[float, float]:
    root_part = math.sqrt(time**2 - 4 * record)
    return (time - root_part) / 2, (time + root_part) / 2


def is_record(proposed_solution: int, time: int, record: int) -> bool:
    new_time = proposed_solution * (time - proposed_solution)
    return new_time > record


def find_number_of_states(time: int, record: int) -> int:
    min_time, max_time = solve_quadratic(time, record)
    min_time = int(math.ceil(max(min_time, 1)))
    max_time = int(math.floor(min(max_time, time - 1)))
    if not is_record(min_time, time, record):
        min_time += 1
    if not is_record(max_time, time, record):
        max_time -= 1
    return max_time - min_time + 1


def part_one(path: Path):
    times, records = parse_input(path)
    return reduce(
        int.__mul__, map(lambda x: find_number_of_states(*x), zip(times, records))
    )


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)


# Part 2
def part_two(path: Path):
    times, records = parse_input(path)
    time = int("".join([str(time) for time in times]))
    record = int("".join([str(record) for record in records]))
    return find_number_of_states(time, record)


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
