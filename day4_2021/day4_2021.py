from typing import Optional
from pathlib import Path
import re
from collections import defaultdict

from aoc_utils import timing


class Table:
    def __init__(self, table: list[list[int]]):
        self._table = table
        self._numbers_to_rows = {}
        self._numbers_to_cols = {}
        for row_id, row in enumerate(self._table):
            for col_id, entry in enumerate(row):
                self._numbers_to_rows[entry] = row_id
                self._numbers_to_cols[entry] = col_id
        self._horizontal_matches = defaultdict(int)
        self._vertical_matches = defaultdict(int)
        self._unmarked_numbers = set(sum((row for row in table), []))
        if len(self._unmarked_numbers) != 5 * 5:
            raise ValueError
        self.is_solved = False

    def mark_number(self, number: int) -> Optional[int]:
        if number in self._unmarked_numbers and not self.is_solved:
            row_id = self._numbers_to_rows[number]
            col_id = self._numbers_to_cols[number]
            self._horizontal_matches[row_id] += 1
            self._vertical_matches[col_id] += 1
            self._unmarked_numbers.remove(number)
            if (
                self._horizontal_matches[row_id] == 5
                or self._vertical_matches[col_id] == 5
            ):
                self.is_solved = True
                return sum(self._unmarked_numbers)
        return None


def parse_file(path: Path) -> tuple[list[int], list[list[list[int]]]]:
    with open(path, "r") as fin:
        text = fin.read()
    numbers, *tables_text = text.split("\n\n")
    numbers = list(map(int, numbers.strip().split(",")))
    pattern = re.compile(r"(\d{1,2})")
    tables = []
    for table_text in tables_text:
        rows = table_text.split("\n")
        tables.append([list(map(int, pattern.findall(row))) for row in rows])
    return numbers, tables


def part_one(path: Path) -> int:
    numbers, tables = parse_file(path)
    tables = [Table(table) for table in tables]
    for number in numbers:
        for table in tables:
            sum_or_none = table.mark_number(number)
            if sum_or_none is not None:
                return sum_or_none * number


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    numbers, tables = parse_file(path)
    tables = [Table(table) for table in tables]
    last_solution = None
    for number in numbers:
        if all(table.is_solved for table in tables):
            break
        for table in tables:
            sum_or_none = table.mark_number(number)
            if sum_or_none is not None:
                last_solution = sum_or_none * number
    return last_solution


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
