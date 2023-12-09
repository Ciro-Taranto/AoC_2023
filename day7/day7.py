from __future__ import annotations
from collections import Counter
from pathlib import Path
from aoc_utils import timing


value_mapping = {str(val): val for val in range(2, 10)}
value_mapping = value_mapping | {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}


class Card:
    def __init__(self, card: str, bid: int):
        self.values = [value_mapping[char] for char in card]
        self.sorted_count = list(reversed(sorted(Counter(self.values).values())))
        self.bid = bid
        self._str = card

    def __lt__(self, other: Card):
        if self.sorted_count != other.sorted_count:
            return self.sorted_count < other.sorted_count
        return self.values < other.values

    @classmethod
    def from_line(cls, line: str):
        card, bid = line.split(" ")
        bid = int(bid)
        return cls(card, bid)

    def __str__(self):
        return self._str


def parse_input(path: Path) -> list[Card]:
    with open(path, "r") as fin:
        return list(map(Card.from_line, fin.readlines()))


def part_one(path: Path) -> int:
    cards = parse_input(path)
    cards = sorted(cards)
    return sum((i + 1) * card.bid for i, card in enumerate(cards))


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part 2

value_mapping_with_joker = {key: val for key, val in value_mapping.items()}
value_mapping_with_joker["J"] = 1


class CardWithJoker(Card):
    """
    Not a good inheritance, since the init is rewritten completely :-(
    """

    def __init__(self, card: str, bid: int):
        super().__init__(card, bid)

        self.values = [value_mapping_with_joker[char] for char in card]
        if card == "JJJJJ":
            self.sorted_count = [
                5,
            ]
        else:
            self.sorted_count = list(
                reversed(sorted(Counter(char for char in card if char != "J").values()))
            )
            self.sorted_count[0] += 5 - sum(self.sorted_count)
        self.bid = bid
        self._str = card

    @classmethod
    def from_card(cls, card: Card) -> CardWithJoker:
        return cls(card._str, card.bid)


def part_two(path: Path) -> int:
    cards = map(CardWithJoker.from_card, parse_input(path))
    cards = sorted(cards)
    return sum((i + 1) * card.bid for i, card in enumerate(cards))


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
