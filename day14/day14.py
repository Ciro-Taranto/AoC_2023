from pathlib import Path
from collections import defaultdict
from bisect import bisect_left
from aoc_utils import timing
from tqdm import tqdm


def parse_file(path: Path) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    with open(path, "r") as fin:
        lines = fin.readlines()
    blocks_by_row = defaultdict(list)
    rocks_by_row = defaultdict(list)
    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            if char == "O":
                rocks_by_row[i].append(j)
            if char == "#":
                blocks_by_row[i].append(j)
    return rocks_by_row, blocks_by_row


def from_rows_to_columns(row_format: dict[int, list[int]]) -> dict[int, list[int]]:
    column_format = defaultdict(list)
    for row, values in row_format.items():
        for column in values:
            column_format[column].append(row)
    return column_format


def move_rocks(
    rocks_by_column: dict[int, list[int]], blocks_by_column: dict[int, list[int]]
) -> dict[int, list[int]]:
    for key, val in rocks_by_column.items():
        rocks_by_column[key] = sorted(val)
    for key, val in blocks_by_column.items():
        blocks_by_column[key] = sorted(val)
    final_rock_positions = defaultdict(list)
    for key, rock_positions in rocks_by_column.items():
        block_positions = blocks_by_column.get(key, [])
        current_position = 0
        # @Andrew: if you are reading this, here is a proof that comments
        # can be very important to read the code and explain why something is done!
        for block_position in block_positions:
            block_insertion_point = bisect_left(rock_positions, block_position)
            final_rock_positions[key].extend(
                list(range(current_position, current_position + block_insertion_point))
            )
            current_position = block_position + 1
            rock_positions = rock_positions[block_insertion_point:]
        final_rock_positions[key].extend(
            list(range(current_position, current_position + len(rock_positions)))
        )
    return final_rock_positions


def part_one(path: Path) -> int:
    rocks_by_row, blocks_by_row = parse_file(path)
    rocks_by_column = from_rows_to_columns(rocks_by_row)
    blocks_by_column = from_rows_to_columns(blocks_by_row)
    number_of_rows = max(max(rocks_by_row), max(blocks_by_row)) + 1
    rock_positions = move_rocks(rocks_by_column, blocks_by_column)
    total = 0
    for _, rocks_on_column in rock_positions.items():
        total += sum(
            [number_of_rows - rock_position for rock_position in rocks_on_column]
        )
    return total


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)


# part 2


def move_north(
    rocks_by_column: dict[int, list[int]],
    blocks_by_column: dict[int, list[int]],
    number_of_rows: int,
) -> dict[int, list[int]]:
    return move_rocks(rocks_by_column, blocks_by_column)


def move_south(
    rocks_by_column: dict[int, list[int]],
    blocks_by_column: dict[int, list[int]],
    number_of_rows: int,
) -> dict[int, list[int]]:
    rocks_by_column = reflect_columns(rocks_by_column, number_of_rows)
    blocks_by_column = reflect_columns(blocks_by_column, number_of_rows)
    rocks_by_column = move_rocks(rocks_by_column, blocks_by_column)
    rocks_by_column = reflect_columns(rocks_by_column, number_of_rows)
    return rocks_by_column


def move_west(
    rocks_by_column: dict[int, list[int]],
    blocks_by_column: dict[int, list[int]],
    number_of_rows: int,
) -> dict[int, list[int]]:
    rocks_by_column = from_rows_to_columns(rocks_by_column)
    blocks_by_column = from_rows_to_columns(blocks_by_column)
    rocks_by_column = move_rocks(rocks_by_column, blocks_by_column)
    rocks_by_column = from_rows_to_columns(rocks_by_column)
    return rocks_by_column


def move_east(
    rocks_by_column: dict[int, list[int]],
    blocks_by_column: dict[int, list[int]],
    number_of_rows: int,
):
    rocks_by_column = from_rows_to_columns(rocks_by_column)
    blocks_by_column = from_rows_to_columns(blocks_by_column)
    rocks_by_column = move_south(rocks_by_column, blocks_by_column, number_of_rows)
    rocks_by_column = from_rows_to_columns(rocks_by_column)
    return rocks_by_column


def reflect_columns(rocks_by_column: dict[int, list[int]], number_of_rows: int):
    return {
        key: list(map(lambda value: number_of_rows - 1 - value, values))
        for key, values in rocks_by_column.items()
    }


def cycle_once(
    rocks_by_column: dict[int, list[int]],
    blocks_by_column: dict[int, list[int]],
    number_of_rows: int,
) -> dict[int, list[int]]:
    number_of_rows = max(max(rocks_by_column), max(blocks_by_column)) + 1
    rocks_by_column = move_north(rocks_by_column, blocks_by_column, number_of_rows)
    rocks_by_column = move_west(rocks_by_column, blocks_by_column, number_of_rows)
    rocks_by_column = move_south(rocks_by_column, blocks_by_column, number_of_rows)
    rocks_by_column = move_east(rocks_by_column, blocks_by_column, number_of_rows)
    return rocks_by_column


def part_two(path: Path) -> int:
    total_cycles = 10**9
    rocks_by_row, blocks_by_row = parse_file(path)
    rock_positions = from_rows_to_columns(rocks_by_row)
    blocks_by_column = from_rows_to_columns(blocks_by_row)
    number_of_rows = max(max(rocks_by_row), max(blocks_by_row)) + 1
    n_cycles = 0
    visited_positions = {}
    pbar = tqdm(total=total_cycles)
    while n_cycles < total_cycles:
        rock_positions = cycle_once(rock_positions, blocks_by_column, number_of_rows)
        configuration_hash = make_configuration_hash(rock_positions)
        n_cycles += 1
        pbar.update(1)
        pbar.set_postfix({"visited_positions": len(visited_positions)})
        if configuration_hash not in visited_positions:
            visited_positions[configuration_hash] = n_cycles
        else:
            cycle_period = n_cycles - visited_positions[configuration_hash]
            completable_periods = (total_cycles - n_cycles) // cycle_period
            pbar.update(completable_periods * cycle_period)
            n_cycles += completable_periods * cycle_period
    total = 0
    for _, rocks_on_column in rock_positions.items():
        total += sum(
            [number_of_rows - rock_position for rock_position in rocks_on_column]
        )
    return total


def make_configuration_hash(rocks_by_column: dict[int, list[int]]) -> int:
    rocks_by_column = tuple(
        [(key, tuple(values)) for key, values in rocks_by_column.items()]
    )
    rocks_by_column = tuple(sorted(rocks_by_column))
    return rocks_by_column.__hash__()


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
