from pathlib import Path
from typing import Optional
from aoc_utils import timing


def parse_input(path: Path) -> list[list[str]]:
    with open(path, "r") as fin:
        return [text.split("\n") for text in fin.read().split("\n\n")]


def transpose(lines: list[str]) -> list[str]:
    lines_length = set(len(line) for line in lines).pop()
    result = [[None for _ in lines] for _ in range(lines_length)]
    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            result[j][i] = char
    return result


def find_reflection(lines: list[str]) -> Optional[int]:
    for lines_above in range(1, len(lines)):
        lines_below = len(lines) - lines_above

        if lines_below > lines_above:
            start = 0
            end = 2 * lines_above - 1
            extension = lines_above
        else:
            start = len(lines) - 2 * lines_below
            end = len(lines) - 1
            extension = lines_below

        if all(lines[start + i] == lines[end - i] for i in range(extension)):
            return lines_above
    return None


def find_number(lines: list[str]) -> int:
    transposed_lines = transpose(lines)
    if (lines_to_the_left := find_reflection(transposed_lines)) is not None:
        return lines_to_the_left
    if (lines_above := find_reflection(lines)) is not None:
        return 100 * lines_above
    raise ValueError


def part_one(path: Path) -> int:
    groups_of_lines = parse_input(path)
    values = list(map(find_number, groups_of_lines))
    return sum(values)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)


def find_reflection_with_correction(lines: list[str]) -> Optional[int]:
    for lines_above in range(1, len(lines)):
        lines_below = len(lines) - lines_above

        if lines_below > lines_above:
            start = 0
            end = 2 * lines_above - 1
            extension = lines_above
        else:
            start = len(lines) - 2 * lines_below
            end = len(lines) - 1
            extension = lines_below

        lines_with_error = [
            (lines[start + i], lines[end - i])
            for i in range(extension)
            if lines[start + i] != lines[end - i]
        ]
        # There can be only one line with an error
        if len(lines_with_error) == 1:
            # The error can only be one char
            if sum(int(a != b) for a, b in zip(*lines_with_error[0])) == 1:
                return lines_above
    return None


def find_number_part_two(lines: list[str]) -> int:
    transposed_lines = transpose(lines)
    if (
        lines_to_the_left := find_reflection_with_correction(transposed_lines)
    ) is not None:
        return lines_to_the_left
    if (lines_above := find_reflection_with_correction(lines)) is not None:
        return 100 * lines_above
    raise ValueError


def part_two(path: Path) -> int:
    groups_of_lines = parse_input(path)
    values = list(map(find_number_part_two, groups_of_lines))
    return sum(values)


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
