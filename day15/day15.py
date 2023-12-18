from pathlib import Path
from aoc_utils import timing


def convert_string(string: str) -> int:
    val = 0
    for char in string:
        val += ord(char)
        val *= 17
        val %= 256
    return val


def part_one(path: Path) -> int:
    with open(path, "r") as fin:
        strings = fin.read().strip().split(",")
    return sum(map(convert_string, strings))


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# part 2


def parse_file(path: Path) -> list[str]:
    with open(path, "r") as fin:
        strings = fin.read().strip().split(",")
    return strings


def part_two(path: Path) -> int:
    strings = parse_file(path)
    # it's too late in the night to think about a good data structure.
    # I will just use the fact that the dict are ordered and use the del operation
    boxes = {i: {} for i in range(256)}
    for string in strings:
        if "-" in string:
            identifier, _ = string.split("-")
            box_id = convert_string(identifier)
            if identifier in boxes[box_id]:
                del boxes[box_id][identifier]
        if "=" in string:
            identifier, value = string.split("=")
            box_id = convert_string(identifier)
            boxes[box_id][identifier] = value
    total = 0
    for box_id, slots in boxes.items():
        total += sum((i + 1) * int(val) for i, val in enumerate(slots.values())) * (
            box_id + 1
        )
    return total


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
