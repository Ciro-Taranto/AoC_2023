from __future__ import annotations
from pathlib import Path
from itertools import cycle
import re
from tqdm import tqdm
import math
from aoc_utils import timing


def parse_file(path: Path) -> tuple[list[int], dict[str, dict[str, str]]]:
    pattern = re.compile(r"([0-9A-Z]{3}) = \(([0-9A-Z]{3}), ([0-9A-Z]{3})\)")
    nodes = dict()
    with open(path, "r") as fin:
        moves = fin.readline().strip()
        _ = fin.readline()
        while line := fin.readline():
            node_id, left, right = pattern.findall(line)[0]
            nodes[node_id] = {"L": left, "R": right}
    return moves, nodes


def part_one(path: Path) -> int:
    moves, nodes = parse_file(path)
    current_node = "AAA"
    for i, move in tqdm(enumerate(cycle(moves))):
        if current_node == "ZZZ":
            break
        current_node = nodes[current_node][move]
    return i


with timing():
    result = part_one(Path(__file__).parent / "input.txt")

print(result)

# Part 2


def part_two_naive(path: Path) -> int:
    # Spoiler: it will work only if you have a lot of time
    # in my case ~4000h, so I would have the solution in about 6 months.
    moves, nodes = parse_file(path)
    current_nodes = [node for node in nodes if node.endswith("A")]
    for i, move in tqdm(enumerate(cycle(moves))):
        if all(node_id.endswith("Z") for node_id in current_nodes):
            break
        current_nodes = [nodes[node_id][move] for node_id in current_nodes]
    return i


def part_two_magic(path: Path) -> int:
    """
    The input is kind of magic.
    1. Each A location finishes on a Z location after an integer # of cycles;
    2. Call n the number of moves from 11A to 22Z, then each n moves you will be again on 22Z
    """
    moves, nodes = parse_file(path)
    current_nodes = [node for node in nodes if node.endswith("A")]
    breaks = list()
    for start_node in current_nodes:
        node = start_node
        for i, move in enumerate(cycle(moves)):
            if node.endswith("Z"):
                breaks.append(i)
                break
            node = nodes[node][move]
    return math.lcm(*breaks)


with timing():
    result = part_two_magic(Path(__file__).parent / "input.txt")

print(result)
