from pathlib import Path
from collections import defaultdict, deque
from itertools import product

from aoc_utils import timing


def add_to_cursor(cursor: tuple[int, int], direction: str, steps: int = 1):
    if direction == "U":
        return cursor[0] - steps, cursor[1]
    if direction == "D":
        return cursor[0] + steps, cursor[1]
    if direction == "L":
        return cursor[0], cursor[1] - steps
    if direction == "R":
        return cursor[0], cursor[1] + steps
    raise ValueError


def parse_file(path: Path) -> list[tuple[str, int, str]]:
    with open(path, "r") as fin:
        lines = fin.readlines()
    instructions = list()
    for line in lines:
        direction, steps, code = line.split(" ")
        steps = int(steps)
        code = code.replace("(", "").replace(")", "")
        instructions.append((direction, steps, code))
    return instructions


def visualize_map(digged_map: set[tuple[int, int]]) -> None:
    digged_map_by_row = defaultdict(list)
    for entry in digged_map:
        digged_map_by_row[entry[0]].append(entry[1])
    digged_map_by_row = dict(sorted(digged_map_by_row.items()))
    min_column = min(min(value) for value in digged_map_by_row.values())
    max_column = max(max(value) for value in digged_map_by_row.values())
    lines = []
    for _, values in digged_map_by_row.items():
        lines.append(
            "".join(
                "#" if i in values else "." for i in range(min_column, max_column + 1)
            )
        )
    with open(Path(__file__).parent / "output.txt", "w") as fout:
        fout.write("\n".join(lines))


def count_by_navigating(digged_map: set[tuple[int, int]]) -> int:
    # This only works assuming that the diggins are "not touching" otherwise one could create an
    # 'enclave' of points which cannot be reached
    min_row = min(entry[0] for entry in digged_map)
    max_row = max(entry[0] for entry in digged_map)
    min_column = min(entry[1] for entry in digged_map)
    max_column = max(entry[1] for entry in digged_map)
    borders = list((min_row, x) for x in range(min_column, max_column + 1))
    borders += list((max_row, x) for x in range(min_column, max_column + 1))
    borders += list((y, min_column) for y in range(min_row, max_row + 1))
    borders += list((y, max_column) for y in range(min_row, max_row + 1))
    queue = deque(borders)  # The corner is not in the graph
    visited = set()
    while queue:
        node = queue.popleft()
        if node in visited or node in digged_map:
            continue
        visited.add(node)
        for move in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_node = (node[0] + move[0], node[1] + move[1])
            if (min_row <= next_node[0] <= max_row) and (
                min_column <= next_node[1] <= max_column
            ):
                queue.append(next_node)
    return (max_row + 1 - min_row) * (max_column + 1 - min_column) - len(visited)


def count_inside(
    instructions: list[tuple[str, int, str]], visualize: bool = False
) -> int:
    start_cursor = (0, 0)
    digged_map = set([start_cursor])
    graph = dict()  # currently not used
    cursor = start_cursor
    for direction, steps, _ in instructions:
        for _ in range(steps):
            next_cursor = add_to_cursor(cursor, direction)
            digged_map.add(next_cursor)
            graph[cursor] = next_cursor
            cursor = next_cursor
    if visualize:
        visualize_map(digged_map)
    return count_by_navigating(digged_map)


def count_by_parity(graph: dict[tuple[int, int], tuple[int, int]]) -> int:
    # TODO: This is not working due to the incorrect treatment of the horizontal sections.
    # To be fixed after christmas
    total = len(graph)
    reversed_graph = {val: key for key, val in graph.items()}
    min_y = min(node[0] for node in graph)
    max_y = max(node[0] for node in graph)
    min_x = min(node[1] for node in graph)
    max_x = max(node[1] for node in graph)
    for y in range(min_y, max_y + 1):
        crossings = 0
        total_by_line = 0
        for x in range(min_x, max_x + 1):
            if (y, x) in graph:
                neighbors = {graph[(y, x)], reversed_graph[(y, x)]}
                c1 = (y, x + 1) not in neighbors
                c2 = (y, x - 1) not in neighbors
                crossings += int(c1) + int(c2)
            else:
                if crossings % 2 == 0 and (crossings // 2) % 2 == 1:
                    total_by_line += 1
        total += total_by_line
    return total


def part_one(path: Path) -> int:
    instructions = parse_file(path)
    return count_inside(instructions, visualize=False)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two

hexa_directions = {"0": "R", "1": "D", "2": "L", "3": "U"}


def decode_hexadecimal(hexa_code: str) -> tuple[str, int]:
    hexa_code = hexa_code.strip("\n")
    direction = hexa_directions[hexa_code[-1]]
    steps = int(hexa_code[1:-1], 16)
    return direction, steps


def shoelace_formula(graph: dict[tuple[int, int]]):
    total_area = 0
    for previous, next in graph.items():
        total_area += int((previous[0] + next[0]) * (next[1] - previous[1]) / 2)
    return abs(total_area)


def part_two(path: Path) -> int:
    instructions = parse_file(path)
    start_cursor = (0, 0)
    digged_map = set([start_cursor])
    graph = dict()
    cursor = start_cursor
    perimeter = 0
    for _, _, hexa in instructions:
        direction, steps = decode_hexadecimal(hexa)
        perimeter += steps
        next_cursor = add_to_cursor(cursor, direction, steps=steps)
        digged_map.add(next_cursor)
        graph[cursor] = next_cursor
        cursor = next_cursor
    return int(shoelace_formula(graph) + perimeter // 2 + 1)


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
