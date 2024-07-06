from pathlib import Path
from tqdm import tqdm

from aoc_utils import timing


class State(list):
    def next_generation(self) -> None:
        new = [8] * sum(elem == 0 for elem in self)
        old = [val - 1 if val - 1 >= 0 else 6 for val in self]
        return State(old + new)


class NonNaiveState:
    def __init__(self, numbers: list[int]):
        self._state = {i: 0 for i in range(9)}
        for number in numbers:
            self._state[number] += 1

    def next_generation(self):
        new_generation = {}
        for i in range(1, 9):
            new_generation[i - 1] = self._state[i]
        new_generation[8] = self._state[0]
        new_generation[6] += self._state[0]
        self._state = new_generation
        return self


def parse_file(path: Path) -> list[int]:
    with open(path, "r") as fin:
        return list(map(int, fin.read().strip().split(",")))


def part_one(path: Path) -> int:
    state = State(parse_file(path))
    for _ in tqdm(range(80)):
        state = state.next_generation()
    print(len(state))


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    state = NonNaiveState(parse_file(path))
    for _ in tqdm(range(256)):
        state = state.next_generation()
    return sum(state._state.values())


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
