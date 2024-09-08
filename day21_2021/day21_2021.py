from __future__ import annotations
from pathlib import Path
from typing import Optional
from collections import defaultdict
from dataclasses import dataclass, replace
from typing import Literal

from aoc_utils import timing


class TrivialDice:
    def __init__(self, n_rolls: int = 3):
        """
        n_rolls: number of times the dice gets rolled in a set
        """
        self.n_rolls = n_rolls
        self.n_sets = 0

    def roll_a_set(self) -> int:
        min_value = 1 + self.n_rolls * self.n_sets
        value = 3 * min_value + (self.n_rolls * (self.n_rolls - 1)) // 2
        self.n_sets += 1
        return value


class Game:
    def __init__(self, position_1: int, position_2: int):
        self.scores = [0, 0]
        self.positions = [position_1, position_2]

    def play_a_round(self, dice: TrivialDice) -> Optional[int]:
        for i, (position, score) in enumerate(zip(self.positions, self.scores)):
            value = dice.roll_a_set()
            self.positions[i] = (position - 1 + value) % 10 + 1
            self.scores[i] += self.positions[i]
            if self.scores[i] >= 1000:
                return self.scores[(i + 1) % 2] * dice.n_sets * dice.n_rolls
        return None


@dataclass(frozen=True, unsafe_hash=True)
class State:
    p1: int
    p2: int
    s1: int
    s2: int

    def update_score(self, player: Literal[1, 2]) -> State:
        return replace(
            self,
            **{f"s{player}": getattr(self, f"s{player}") + getattr(self, f"p{player}")},
        )


class QuantumGame:
    def __init__(self, position_1: int, position_2: int):
        self.states = {State(position_1, position_2, 0, 0): 1}
        self.winning_1 = 0
        self.winning_2 = 0

    def roll_a_dice(self, player: Literal[1, 2]) -> None:
        total_states = sum(self.states.values())
        new_states = defaultdict(int)
        for outcome in range(1, 4):
            for state, copies in self.states.items():
                p = getattr(state, f"p{player}")
                np = (p - 1 + outcome) % 10 + 1
                new_state = replace(state, **{f"p{player}": np})
                new_states[new_state] += copies
        new_total_states = sum(new_states.values())
        if total_states * 3 != new_total_states:
            raise ValueError("The number of states should increase by a factor 3.")
        self.states = new_states

    def update_scores(self, player: Literal[1, 2]) -> None:
        new_states = defaultdict(int)
        for state, count in self.states.items():
            new_state = state.update_score(player)
            new_states[new_state] += count
        self.states = new_states

    def play_a_round(self):
        for _ in range(3):
            self.roll_a_dice(player=1)
        self.update_scores(player=1)
        w = self.check_winning_states(player=1)
        self.winning_1 += w
        for _ in range(3):
            self.roll_a_dice(player=2)
        self.update_scores(player=2)
        w = self.check_winning_states(player=2)
        self.winning_2 += w

    def check_winning_states(self, player: Literal[1, 2]) -> int:
        new_states = dict()
        winning = 0
        for state, copies in self.states.items():
            score = getattr(state, f"s{player}")
            if score >= 21:
                winning += copies
            else:
                new_states[state] = copies
        self.states = new_states
        return winning


def part_one() -> int:
    dice = TrivialDice()
    game = Game(4, 5)
    while (value := game.play_a_round(dice)) is None:
        continue
    return value


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    game = QuantumGame(4, 5)
    i = 0
    while game.states:
        game.play_a_round()
        number_of_states = len(game.states)
        number_of_universes = sum(game.states.values())
        i += 1
        print(
            f"Round {i}: \n\t States: {number_of_states}, Universes: {number_of_universes}"
        )
        print(f"\t W1: {game.winning_1}, W2: {game.winning_2}")
        for k, v in game.states.items():
            print(f"\t{k}: {v}")
    return max([game.winning_1, game.winning_2])


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
