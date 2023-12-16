from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math
from collections import deque
from tqdm import tqdm
from aoc_utils import timing

right = (0, 1)
left = (0, -1)
up = (-1, 0)
down = (1, 0)

moves: dict[tuple[int, int], dict[str, tuple[int, int]]] = {
    right: {"J": up, "7": down, "-": right},
    up: {"F": right, "7": left, "|": up},
    left: {"F": down, "L": up, "-": left},
    down: {"J": left, "L": right, "|": down},
}


@dataclass(frozen=True)
class Coordinate:
    y: int
    x: int

    def __add__(self, move: tuple[int, int]) -> Coordinate:
        return Coordinate(self.y + move[0], self.x + move[1])

    def __sub__(self, move: tuple[int, int]) -> Coordinate:
        return Coordinate(self.y - move[0], self.x - move[1])

    def __getitem__(self, char_map: list[str]) -> str:
        """
        I still have to decide if this is a good idea.
        """
        return char_map[self.y][self.x]


def parse_file(path: Path) -> list[str]:
    with open(path, "r") as fin:
        return list(map(lambda x: x.strip(), fin.readlines()))


def find_start(lines: list[str]) -> tuple[int, int]:
    for i, line in enumerate(lines):
        if "S" in line:
            return i, line.index("S")


def navigate(lines: list[str]) -> tuple[list[list[Coordinate]], tuple[str, Coordinate]]:
    y, x = find_start(lines)
    start = Coordinate(y, x)
    paths: list[list[tuple[int, int]]] = []
    for direction in moves:
        if paths:
            break
        current_direction = direction
        current_position = start + current_direction
        possible_path = [current_position]
        while True:  # TODO: get rid of the while true
            if current_position == start:
                paths.append(possible_path)
                break
            current_char = current_position[lines]
            current_direction = moves[current_direction].get(current_char, None)
            if not current_direction:
                break
            current_position += current_direction
            possible_path.append(current_position)
    first = paths[0][0]
    last = paths[0][-2]  # start happens to be the entry [-1]
    if start.y == first.y:
        if start.y == last.y:
            start_tile = "-"
        elif start.y == last.y - 1 and start.x == first.x - 1:
            start_tile = "F"
        elif start.y == last.y - 1 and start.x == first.x + 1:
            start_tile = "7"
        elif start.y == last.y + 1 and first.x == start.x + 1:
            start_tile = "L"
        elif start.y == last.y + 1 and first.x == start.x - 1:
            start_tile = "J"
        else:
            raise ValueError
    if start.x == first.x:
        if start.x == last.x:
            start_tile = "|"
        elif start.x == last.x - 1 and first.y == start.y + 1:
            start_tile = "F"
        elif start.x == last.x - 1 and first.y == start.y - 1:
            start_tile = "L"
        elif start.x == last.x + 1 and first.y == start.y + 1:
            start_tile = "7"
        elif start.x == last.x + 1 and first.y == start.y - 1:
            start_tile = "J"
        else:
            raise ValueError
    return paths, (start_tile, start)


def part_one(path: Path):
    lines = parse_file(path)
    paths, _ = navigate(lines)
    return max(math.ceil(len(path) / 2) for path in paths)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)


# Part 2


def expand_map(lines: list[str], path: list[Coordinate]) -> list[str]:
    mappings = {
        "|": [".x."] * 3,
        "-": ["...", "xxx", "..."],
        "F": ["...", ".xx", ".x."],
        "J": [".x.", "xx.", "..."],
        "7": ["...", "xx.", ".x."],
        "L": [".x.", ".xx", "..."],
        ".": ["..."] * 3,
    }
    all_lines_expansion = []
    for i, line in tqdm(enumerate(lines)):
        line_expansion = ["", "", ""]
        for j, char in enumerate(line.strip()):
            if Coordinate(y=i, x=j) in path:
                extended_tile = mappings[char]
                for k in range(len(line_expansion)):
                    line_expansion[k] += extended_tile[k]
            else:
                for k in range(len(line_expansion)):
                    line_expansion[k] += "..."
        all_lines_expansion.extend(line_expansion)
    return all_lines_expansion


def explore(extended_map: list[str]) -> set[tuple[int, int]]:
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    n_lines = len(extended_map)
    line_length = set(len(line) for line in extended_map).pop()
    to_explore = deque([(0, 0)])
    assert extended_map[0][0] != "x"
    seen = set()
    reachable_from_outside = set()
    pbar = tqdm()
    while to_explore:
        pbar.set_postfix(
            {
                "seen": len(seen),
                "reachable_from_outside": len(reachable_from_outside),
                "to_explore": len(to_explore),
            }
        )
        node = to_explore.popleft()
        if node in seen:
            continue
        seen.add(node)
        is_center = ((node[0] - 1) % 3 == 0) & ((node[1] - 1) % 3 == 0)
        if is_center:
            reachable_from_outside.add(node)
        for move in moves:
            next_node = (node[0] + move[0], node[1] + move[1])
            if 0 <= next_node[0] < n_lines and 0 <= next_node[1] < line_length:
                char = extended_map[next_node[0]][next_node[1]]
                if char != "x":
                    to_explore.append(next_node)

    return reachable_from_outside


def part_two(path: Path) -> int:
    lines = parse_file(path)
    paths, (start_tile, start) = navigate(lines)
    lines[start.y] = lines[start.y].replace("S", start_tile)
    expansion = expand_map(lines, paths[0])
    reachable_from_outside = explore(expansion)
    total_tiles = sum(len(line) for line in lines)
    return total_tiles - len(reachable_from_outside) - len(paths[0])


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
