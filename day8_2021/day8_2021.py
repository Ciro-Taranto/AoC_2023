from pathlib import Path
from functools import partial

from aoc_utils import timing


def parse_file(path: Path) -> list[tuple[list[str], list[str]]]:
    fun = partial(str.split, sep=" ")
    entries = []
    with open(path, "r") as fin:
        for line in fin.readlines():
            entries.append(tuple(map(fun, line.split(" | "))))
    return entries


def count(lists_of_strings: list[tuple[str, str, str, str]]) -> int:
    easy_digits = list(map(count_one_line, lists_of_strings))
    return sum(easy_digits)


def count_one_line(list_of_strings: tuple[str, str, str, str]) -> int:
    unique_lenghts = {2, 3, 4, 7}
    return sum(len(string.strip()) in unique_lenghts for string in list_of_strings)


def decode(entry: tuple[list[str], list[str]]) -> int:
    code = [val.strip() for val in entry[1]]
    code = ["".join(sorted(val)) for val in code]
    digits = entry[0]
    segment_lengths = list(map(len, digits))
    decoded = dict()
    decoded[1] = digits[segment_lengths.index(2)]
    decoded[4] = digits[segment_lengths.index(4)]
    decoded[8] = digits[segment_lengths.index(7)]
    decoded[7] = digits[segment_lengths.index(3)]
    decoded[3] = [
        digit for digit in digits if len(digit) == 5 and is_contained(decoded[1], digit)
    ][0]
    in_five_but_not_in_two = set(decoded[4]).difference(decoded[1])
    decoded[5] = [
        digit
        for digit in digits
        if len(digit) == 5 and is_contained(in_five_but_not_in_two, digit)
    ][0]
    decoded[2] = [
        digit
        for digit in digits
        if len(digit) == 5
        and not is_contained(in_five_but_not_in_two, digit)
        and not is_contained(decoded[1], digit)
    ][0]
    decoded[6] = [
        digit
        for digit in digits
        if len(digit) == 6 and not is_contained(decoded[7], digit)
    ][0]
    decoded[9] = [
        digit
        for digit in digits
        if len(digit) == 6 and is_contained(decoded[5], digit) and digit != decoded[6]
    ][0]
    decoded[0] = [
        digit
        for digit in digits
        if len(digit) == 6 and digit not in {decoded[9], decoded[6]}
    ][0]

    for key, val in decoded.items():
        decoded[key] = "".join(sorted(val))

    string_to_numbers = dict(zip(decoded.values(), decoded.keys()))

    decoded_code = int("".join([str(string_to_numbers[val]) for val in code]))
    return decoded_code


def is_contained(first_digit: str | set[str], second_digit: str | set[str]) -> bool:
    return all(char in second_digit for char in first_digit)


def part_one(path: Path) -> int:
    entries = parse_file(path)
    return count([entry[1] for entry in entries])


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    entries = parse_file(path)
    total = 0
    for entry in entries:
        total += decode(entry)
    return total


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
