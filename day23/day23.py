from pathlib import Path
from collections import deque
from tqdm import tqdm
from itertools import product
import math

from aoc_utils import timing

slide_moves = {">": (0, 1), "<": (0, -1), "v": (1, 0), "^": (-1, 0)}


def parse_file(path: Path) -> list[list[str]]:
    with open(path, "r") as fin:
        input_txt = fin.read()
    return input_txt.splitlines()


def get_possible_moves(
    position: tuple[int, int],
    lines: list[list[str]],
    n_rows: int,
    n_cols: int,
    force_slopes: bool = True,
) -> list[tuple[int, int]]:
    def is_in_bounds(pos: tuple[int, int]) -> bool:
        return 0 <= pos[0] < n_rows and 0 <= pos[1] < n_cols

    possible_positions = list()
    char = lines[position[0]][position[1]]
    if char in slide_moves and force_slopes:
        possible_moves = [slide_moves[char]]
    else:
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for move in possible_moves:
        new_position = (position[0] + move[0], position[1] + move[1])
        if (
            is_in_bounds(new_position)
            and lines[new_position[0]][new_position[1]] != "#"
        ):
            possible_positions.append(new_position)
    return possible_positions


def explore_all_paths(
    lines: list[list[str]],
    start_position: tuple[int, int],
    end_position: tuple[int, int],
    force_slopes: bool = True,
) -> list[set[tuple[int, int]]]:
    n_rows = len(lines)
    n_cols = len(lines[0])
    queue = deque([(start_position, set())])
    valid_paths = list()
    progress_bar = tqdm()
    counter = 0
    while queue:
        position, path = queue.popleft()
        path = path.union({position})
        for next_position in get_possible_moves(
            position, lines, n_rows, n_cols, force_slopes=force_slopes
        ):
            if next_position == end_position:
                valid_paths.append(
                    path.union({end_position}).difference({start_position})
                )
            elif next_position not in path:
                queue.append((next_position, set(path)))
        counter += 1
        if counter % 1_000 == 0:
            progress_bar.update(1_000)
            progress_bar.set_postfix(
                {"queue": len(queue), "possible_paths": len(valid_paths)}
            )
    return valid_paths


def visualize_path(path: set[tuple[int, int]], lines: list[list[str]]):
    new_lines = list()
    for i, line in enumerate(lines):
        new_line = list()
        for j, char in enumerate(line):
            if (i, j) in path:
                new_line.append("O")
            else:
                new_line.append(char)
        new_line = "".join(new_line)
        new_lines.append(new_line)
    print("\n".join(new_lines))
    with open(Path(__file__).parent / "output.txt", "w") as fout:
        fout.write("\n".join(new_lines))
    return None


def part_one(path: Path, visualize: bool = False) -> int:
    lines = parse_file(path)
    start_position = (0, lines[0].index("."))
    end_position = (len(lines) - 1, lines[-1].index("."))
    valid_paths = explore_all_paths(lines, start_position, end_position)
    valid_paths = sorted(valid_paths, key=lambda x: len(x))
    if visualize:
        visualize_path(valid_paths[-1], lines)
    return len(valid_paths[-1])


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def find_points_with_deviations(lines: list[list[str]]):
    n_rows = len(lines)
    n_cols = len(lines[0])
    points = list()
    for i, j in product(range(n_rows), range(n_cols)):
        if (
            len(get_possible_moves((i, j), lines, n_rows, n_cols)) >= 3
            and lines[i][j] != "#"
        ):
            points.append((i, j))
    return points


def find_point_distances(
    points: list[tuple[int, int]], lines: list[list[int]]
) -> dict[tuple[int, int], dict[tuple[int, int]], int]:
    n_rows = len(lines)
    n_cols = len(lines[0])
    graph = {point: {} for point in points}
    for point in tqdm(points):
        queue = deque([(0, point)])
        visited = {point}
        while queue:
            distance, current_point = queue.popleft()
            if distance > 0 and current_point in points:
                graph[point][current_point] = distance
                continue
            for next_point in get_possible_moves(
                current_point, lines, n_rows, n_cols, False
            ):
                if next_point not in visited:
                    queue.append((distance + 1, next_point))
                    visited.add(next_point)
    return graph


class WithLogging:
    def __init__(self):
        self.counter = 1
        self.progress_bar = tqdm()
        self.update_every = 1_000

    def __call__(self, func):
        def wrapped_func(*args, **kwargs):
            self.counter += 1
            if self.counter % self.update_every == 0:
                self.progress_bar.update(self.update_every)
            return func(*args, **kwargs)

        return wrapped_func


@WithLogging()
def dfs(
    position: tuple[int, int],
    end_position: tuple[int, int],
    graph_distances: dict[tuple[int, int], dict[tuple[int, int]], int],
    seen: set[tuple[int, int]],
) -> int:
    if position == end_position:
        return 0
    distance = -math.inf
    seen.add(position)
    for next_point, next_distance in graph_distances[position].items():
        if next_point not in seen:
            distance = max(
                distance,
                next_distance + dfs(next_point, end_position, graph_distances, seen),
            )
    seen.remove(position)
    return distance


def depth_first_search(
    lines: list[list[str]],
    start_position: tuple[int, int],
    end_position: tuple[int, int],
) -> int:
    points_with_deviations = find_points_with_deviations(lines)
    points_with_deviations = [start_position, end_position] + points_with_deviations
    graph_distances = find_point_distances(points_with_deviations, lines)
    return dfs(start_position, end_position, graph_distances, set())


def part_two(path: Path, visualize: bool = False) -> int:
    lines = parse_file(path)
    start_position = (0, lines[0].index("."))
    end_position = (len(lines) - 1, lines[-1].index("."))
    distance = depth_first_search(lines, start_position, end_position)
    return distance


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
