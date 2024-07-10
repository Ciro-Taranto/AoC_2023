from pathlib import Path
import re
from collections import Counter, defaultdict
from tqdm import tqdm

from aoc_utils import timing


def evolve(
    original_combinations: dict[str, int], substitutions: dict[str, str]
) -> dict[str, int]:
    new_combinations: dict[str, int] = defaultdict(int)
    for combination, count in original_combinations.items():
        if combination in substitutions:
            new_combinations[combination[0] + substitutions[combination]] += count
            new_combinations[substitutions[combination] + combination[1]] += count
        else:
            new_combinations[combination] += count
    return new_combinations


def polymerize(original_string: str, substitutions: dict[str, str]):
    replacement_dict = dict()
    for sub in substitutions:
        matches = [
            match.start() for match in re.finditer(f"(?=({sub}))", original_string)
        ]
        for match in matches:
            replacement_dict[match] = sub
    new_string = ""
    for i, char in enumerate(original_string):
        new_string += char
        if i in replacement_dict:
            new_string += substitutions[replacement_dict[i]]
    return new_string


def parse_file(path: Path) -> tuple[str, dict[str, str]]:
    with open(path, "r") as fin:
        text = fin.read()
    original_string, substitutions = text.split("\n\n")
    substitutions = re.findall("([A-Z]{2}) -> ([A-Z])", substitutions)
    substitutions = dict(substitutions)
    return original_string, substitutions


def part_one(path: Path, iterations: int = 10) -> int:
    original_string, substitutions = parse_file(path)
    for _ in tqdm(range(iterations)):
        original_string = polymerize(original_string, substitutions)
    counts = Counter(original_string)
    return max(counts.values()) - min(counts.values())


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    original_string, substitutions = parse_file(path)
    pairs = defaultdict(int)
    for i in range(len(original_string) - 1):
        pairs[original_string[i : i + 2]] += 1
    for _ in range(40):
        pairs = evolve(pairs, substitutions)
    counts = defaultdict(int)
    for pair, number in pairs.items():
        counts[pair[0]] += number
        counts[pair[1]] += number
    counts[original_string[-1]] += 1
    counts[original_string[0]] += 1
    counts = {key: val // 2 for key, val in counts.items()}
    counts = sorted(counts.items(), key=lambda x: -x[1])
    return counts[0][1] - counts[-1][1]


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
