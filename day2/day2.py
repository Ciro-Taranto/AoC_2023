import re
from pathlib import Path
from functools import reduce
from aoc_utils import timing

# Part one


def parse_line(line: str) -> tuple[str, list[dict[str, int]]]:
    id_line, value_line = line.split(":")
    game_id = int(re.findall(r"Game (\d+)", id_line)[0])
    game_results = []
    for game in value_line.split(";"):
        extraction_results = dict()
        for entry in game.split(","):
            value, color = re.findall(r"(\d+) ([a-z]+)", entry)[0]
            extraction_results[color] = int(value)
        game_results.append(extraction_results)
    return game_id, game_results


def is_game_valid(
    game_results: list[dict[str, int]], value_limits: dict[str, int]
) -> bool:
    return all(map(lambda x: is_extraction_valid(x, value_limits), game_results))


def is_extraction_valid(extraction_results: dict[str, int], value_limits) -> bool:
    return all(value <= value_limits[key] for key, value in extraction_results.items())


with timing():
    total = 0
    value_limits = {"red": 12, "green": 13, "blue": 14}
    with open(Path(__file__).parent / "input.txt") as fin:
        for line in fin.readlines():
            game_id, game_result = parse_line(line)
            if is_game_valid(game_result, value_limits):
                total += game_id
print(total)


# Part two


def find_game_power(game_results: list[dict[str, int]]) -> int:
    mins = {"red": 0, "green": 0, "blue": 0}
    for extraction in game_results:
        for color, value in extraction.items():
            mins[color] = max(mins[color], value)
    return reduce(lambda a, b: a * b, mins.values())


with timing():
    with open(Path(__file__).parent / "input.txt") as fin:
        total = sum(
            map(lambda x: find_game_power(x[-1]), map(parse_line, fin.readlines()))
        )

print(total)
