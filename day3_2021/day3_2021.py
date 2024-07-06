from pathlib import Path

from aoc_utils import timing


def parse_file(path: Path) -> list[str]:
    with open(path, "r") as fin:
        lines = fin.readlines()
    return lines


def compute_bit_frequency(lines: list[str]) -> list[int]:
    n_digits = [int(char) for char in lines[0].strip()]
    for line in lines[1:]:
        for i, char in enumerate(line.strip()):
            n_digits[i] += int(char)
    return n_digits


def part_one(path: Path) -> int:
    lines = parse_file(path)
    n_digits = compute_bit_frequency(lines)
    gamma = "".join(["1" if digit / len(lines) > 0.5 else "0" for digit in n_digits])
    epsilon = "".join(["1" if digit / len(lines) < 0.5 else "0" for digit in n_digits])
    gamma = int(gamma, 2)
    epsilon = int(epsilon, 2)
    return gamma * epsilon


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    lines = parse_file(path)
    oxy_lines = [[int(char) for char in line.strip()] for line in lines]
    co2_lines = [[int(char) for char in line.strip()] for line in lines]
    for i in range(len(oxy_lines[0])):
        bit = int(sum(line[i] for line in oxy_lines) >= (len(oxy_lines) / 2))
        oxy_lines = [line for line in oxy_lines if line[i] == bit]
        if len(oxy_lines) == 1:
            break
    oxy_number = int("".join([str(bit) for bit in oxy_lines[0]]), 2)
    for i in range(len(co2_lines[0])):
        ones = sum(line[i] for line in co2_lines)
        if ones < len(co2_lines) / 2:
            bit = 1
        else:
            bit = 0
        co2_lines = [line for line in co2_lines if line[i] == bit]
        if len(co2_lines) == 1:
            break
    co2_number = int("".join([str(bit) for bit in co2_lines[0]]), 2)
    return co2_number * oxy_number


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
