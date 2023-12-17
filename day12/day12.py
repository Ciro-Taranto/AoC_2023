from pathlib import Path
import re
from functools import lru_cache
from tqdm import tqdm
from aoc_utils import timing

PATTERN = re.compile(r"(\#+)")


def parse_file(path: Path) -> list[tuple[str, list[int]]]:
    records = list()
    with open(path, "r") as fin:
        for line in list(fin.readlines()):
            symbols, numbers = line.strip().split(" ")
            numbers = tuple([int(num) for num in numbers.split(",")])
            records.append((symbols, numbers))
    return records


@lru_cache(maxsize=2**12)
def find_combinations_for_line(
    symbols: str,
    numbers: tuple[int, ...],
    currently_open: int = 0,
) -> list[str]:
    valid_combinations = list()
    if "?" not in symbols:
        if is_valid(symbols, numbers, currently_open=currently_open):
            valid_combinations.append(symbols)
        return valid_combinations

    char = symbols[0]
    rest = symbols[1:]

    if char == "?":
        valid_combinations = find_combinations_for_line(
            "." + rest, numbers, currently_open=currently_open
        ) + find_combinations_for_line(
            "#" + rest, numbers, currently_open=currently_open
        )
        return valid_combinations

    if char == ".":
        if (currently_open > 0) and (currently_open != numbers[0]):
            # Not a valid combination, discard.
            return []
        elif currently_open > 0:
            # Close the previous combination and go on
            valid_combinations = find_combinations_for_line(
                rest, numbers[1:], currently_open=0
            )
        else:
            # Go on, but do not reduce the numbers
            valid_combinations = find_combinations_for_line(
                rest, numbers, currently_open=0
            )

    elif char == "#":
        currently_open += 1
        if (not numbers) or (currently_open > numbers[0]):
            # Not a valid combination, discard.
            return []
        else:
            valid_combinations = find_combinations_for_line(
                rest, numbers, currently_open=currently_open
            )

    return [char + combination for combination in valid_combinations]


def is_valid(line: str, numbers: list[int], currently_open: int):
    matches = PATTERN.findall("#" * currently_open + line)
    sequences = tuple(map(len, matches))
    return sequences == numbers


def part_one(path: Path) -> int:
    records = parse_file(path)
    total = 0
    for symbols, numbers in tqdm(records):
        total += len(find_combinations_for_line(symbols, numbers))
    return total


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)


# part 2


def deal_with_dot(
    symbols: str,
    numbers: tuple[int, ...],
    cursor: int,
    currently_open: int,
):
    if currently_open == 0:
        return find_combinations_efficient(symbols, numbers, cursor + 1, 0)
    if not numbers or numbers[0] != currently_open:
        return 0
    return find_combinations_efficient(
        symbols, numbers[1:], cursor + 1, currently_open=0
    )


def deal_with_hash(
    symbols: str, numbers: tuple[int, ...], cursor: int, currently_open: int
):
    return find_combinations_efficient(symbols, numbers, cursor + 1, currently_open + 1)


@lru_cache(maxsize=2**14)
def find_combinations_efficient(
    symbols: str, numbers: tuple[int, ...], cursor: int, currently_open: int
):
    if cursor == len(symbols):
        if not numbers and currently_open == 0:
            return 1
        elif len(numbers) == 1 and numbers[0] == currently_open:
            return 1
        else:
            return 0

    char = symbols[cursor]
    if char == ".":
        return deal_with_dot(symbols, numbers, cursor, currently_open)
    if char == "#":
        return deal_with_hash(symbols, numbers, cursor, currently_open)
    if char == "?":
        return deal_with_dot(symbols, numbers, cursor, currently_open) + deal_with_hash(
            symbols, numbers, cursor, currently_open
        )


def part_two(path: Path) -> int:
    records = parse_file(path)
    total = 0
    for symbols, numbers in tqdm(records):
        symbols = "?".join([symbols] * 5)
        numbers = numbers * 5
        total += find_combinations_efficient(symbols, numbers, 0, 0)
    return total


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
