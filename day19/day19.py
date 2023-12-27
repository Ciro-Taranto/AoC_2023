from pathlib import Path
from typing import Callable, Union
import re
from dataclasses import dataclass
from collections import deque
from tqdm import tqdm
from functools import reduce

from aoc_utils import timing

pattern = re.compile(r"([a-zA-Z]+)([<>])(\d+):([a-zA-Z]+)")
values_pattern = re.compile(r"([xmas])=(\d+)")


@dataclass
class PossibleOutcome:
    workflow_id: str
    condition_id: int
    variable_name: str
    variable_restriction: tuple[int, int]


def reduce_ranges(
    ranges: dict[str, tuple[int, int]],
    variable_name: str,
    variable_restriction: tuple[int, int],
) -> dict[str, tuple[int, int]]:
    ranges = dict(ranges)
    ranges[variable_name] = (
        max(ranges[variable_name][0], variable_restriction[0]),
        min(ranges[variable_name][1], variable_restriction[1]),
    )
    return ranges


@dataclass
class State:
    possible_outcome: PossibleOutcome
    ranges: dict[str, tuple[int, int]]


class Workflow:
    def __init__(
        self,
        workflow_id: str,
        comparisons: list[tuple[str, Callable[[int, int], bool], int, str]],
        final_condition: str,
    ):
        self.comparisons = comparisons
        self.final_condition = final_condition
        self.workflow_id = workflow_id

    def __call__(self, values: dict[str, int]) -> str:
        for variable_name, comparison_function, value, outcome in self.comparisons:
            if comparison_function(values[variable_name], value):
                return outcome
        return self.final_condition

    def split_outcomes(self, condition_id: int) -> Union[list[PossibleOutcome], str]:
        if condition_id == len(self.comparisons) and self.final_condition in "AR":
            return self.final_condition
        elif condition_id == len(self.comparisons):
            return [PossibleOutcome(self.final_condition, 0, "x", (1, 4000))]

        variable, comparison_fn, value, outcome = self.comparisons[condition_id]
        if comparison_fn == int.__lt__:
            positive_range, negative_range = (1, value - 1), (value, 4000)
        elif comparison_fn == int.__gt__:
            negative_range, positive_range = (1, value), (value + 1, 4000)
        else:
            raise ValueError
        if_false_outcome = PossibleOutcome(
            self.workflow_id,
            condition_id=condition_id + 1,
            variable_name=variable,
            variable_restriction=negative_range,
        )
        if_true_outcome = PossibleOutcome(
            outcome,
            condition_id=0,
            variable_name=variable,
            variable_restriction=positive_range,
        )
        return [if_true_outcome, if_false_outcome]


def parse_condition(
    condition: str,
) -> tuple[str, Callable[[int, int], bool], int, str]:
    letter_to_compare, comparison, value, goto = pattern.findall(condition)[0]
    value = int(value)
    comparison_fn = int.__lt__ if comparison == "<" else int.__gt__
    return letter_to_compare, comparison_fn, value, goto


def parse_file(path: Path) -> tuple[dict[str, Workflow], list[dict[str, int]]]:
    with open(path, "r") as fin:
        input_text = fin.read()
    workflow_text, values_text = input_text.split("\n\n")
    workflows = {}
    for line in workflow_text.split("\n"):
        idx, rest = line.split("{")
        rest = rest.replace("}", "")
        conditions = rest.split(",")
        parsed_conditions = [
            parse_condition(condition) for condition in conditions[:-1]
        ]
        workflows[idx] = Workflow(idx, parsed_conditions, conditions[-1])
    values = []
    for line in values_text.splitlines():
        names_and_values = values_pattern.findall(line)
        values.append({name: int(val) for name, val in names_and_values})
    return workflows, values


def part_one(path: Path) -> int:
    workflows, values = parse_file(path)
    total = 0
    for value in values:
        outcome = workflows["in"](value)
        while outcome not in {"A", "R"}:
            outcome = workflows[outcome](value)
        if outcome == "A":
            total += sum(value.values())
    return total


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    workflows, _ = parse_file(path)
    return explore_combinations(workflows)


def compute_state_volume(ranges: dict[str, int]) -> int:
    return reduce(int.__mul__, map(lambda x: max(x[1] - x[0] + 1, 0), ranges.values()))


def explore_combinations(workflows: dict[str, Workflow]) -> int:
    workflow = workflows["in"]
    ranges = {char: (1, 4000) for char in "xmas"}
    accepted_states: list[State] = list()
    possible_states = deque(
        [
            State(
                path,
                reduce_ranges(ranges, path.variable_name, path.variable_restriction),
            )
            for path in workflow.split_outcomes(0)
        ]
    )
    progress_bar = tqdm(total=4000**4)
    while possible_states:
        state = possible_states.popleft()
        if state.possible_outcome.workflow_id in "AR":
            child_states = state.possible_outcome.workflow_id
        else:
            workflow = workflows[state.possible_outcome.workflow_id]
            child_states = workflow.split_outcomes(state.possible_outcome.condition_id)
        if isinstance(child_states, str) or state.possible_outcome.workflow_id in "AR":
            volume = compute_state_volume(state.ranges)
            progress_bar.update(volume)
            progress_bar.set_postfix({"queue len": len(possible_states)})
            if child_states == "A":
                accepted_states.append(state)
        else:
            next_states = [
                State(
                    path,
                    reduce_ranges(
                        state.ranges, path.variable_name, path.variable_restriction
                    ),
                )
                for path in child_states
            ]
            possible_states.extend(next_states)
    return sum(compute_state_volume(state.ranges) for state in accepted_states)


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
