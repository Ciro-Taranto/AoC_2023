from pathlib import Path
from typing import Optional
from collections import UserString

from aoc_utils import timing


def parse_file(path: Path) -> list[str]:
    with open(path, "r") as fin:
        return fin.readlines()


pairs = {"<": ">", "{": "}", "[": "]", "(": ")"}
values = {">": 25137, "}": 1197, "]": 57, ")": 3}
openings = set(pairs)
closings = set(pairs.values())


class Line(str):
    def scan(self, return_context: bool = False) -> Optional[str | list[str]]:
        if self[0] not in openings:
            return self[0]
        context = [self[0]]
        for char in self[1:]:
            if char in openings:
                context.append(char)
            elif char in closings:
                if pairs[context[-1]] == char:
                    context.pop()
                else:
                    return char
            else:
                raise ValueError(f"{char} does not seem valid.")
        return context if return_context else None


def part_one(path: Path) -> int:
    lines = parse_file(path)
    faulty = []
    for line in lines:
        char_or_none = Line(line.strip()).scan()
        faulty.append(char_or_none)
    return sum(values.get(entry, 0) for entry in faulty)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two

completion_values = {">": 4, "}": 3, "]": 2, ")": 1}


def compute_completion_value(context: list[str]) -> int:
    current_value = 0
    for next_char in context[::-1]:
        current_value = update_completion_value(current_value, next_char=next_char)
    return current_value


def update_completion_value(current_value: int, next_char: str) -> int:
    current_value *= 5
    current_value += completion_values[pairs[next_char]]
    return current_value


def part_two(path: Path) -> int:
    lines = parse_file(path)
    incomplete = []
    for line in lines:
        char_or_context = Line(line.strip()).scan(return_context=True)
        if isinstance(char_or_context, list):
            incomplete.append(char_or_context)
    all_values = sorted(map(compute_completion_value, incomplete))
    return all_values[len(all_values) // 2]


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
