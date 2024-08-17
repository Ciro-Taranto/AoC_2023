from __future__ import annotations
from pathlib import Path
import math
from dataclasses import dataclass
from typing import Optional, Literal
import json
from colorama import Fore, Style
from tqdm import tqdm
from itertools import product
from copy import deepcopy

from aoc_utils import timing


class Settings:
    level = 4
    verbose = False


@dataclass
class Node:
    root: Optional[Node]
    left: Node | int
    right: Node | int

    def is_left(self) -> bool:
        if self.root is None:
            return False
        return self.root.left is self

    def is_right(self) -> bool:
        if self.root is None:
            return False
        return self.root.right is self

    def is_right_leaf(self) -> bool:
        return isinstance(self.right, int)

    def is_left_leaf(self) -> bool:
        return isinstance(self.left, int)

    def is_leaf(self) -> bool:
        return self.is_right_leaf() and self.is_left_leaf()

    def is_root(self) -> bool:
        return self.root is None

    def side(self) -> str:
        return "left" if self.is_left() else "right"

    def other_side(self) -> str:
        return "left" if self.is_right() else "right"

    def level(self) -> int:
        if self.root is None:
            return 0
        return 1 + self.root.level()

    def get_tree_root(self) -> Node:
        if self.root is None:
            return self
        return self.root.get_tree_root()

    def get_first_node_to_explode(self) -> Optional[Node]:
        if self.is_leaf() and self.level() >= Settings.level:
            return self
        for side in ["left", "right"]:
            child = getattr(self, side)
            if isinstance(child, Node):
                exploding = child.get_first_node_to_explode()
                if exploding is not None:
                    return exploding
        return None

    def get_first_node_to_split(self) -> Optional[Node]:
        for side in ["left", "right"]:
            child = getattr(self, side)
            if isinstance(child, int) and child >= 10:
                return self
            elif isinstance(child, Node):
                splitting_node = child.get_first_node_to_split()
                if splitting_node is not None:
                    return splitting_node
        return None

    def __str__(self) -> str:
        if isinstance(self.left, Node) or self.left < 10:
            l = str(self.left)
        else:
            l = f"{Fore.RED}{self.left}{Style.RESET_ALL}"
        if isinstance(self.right, Node) or self.right < 10:
            r = str(self.right)
        else:
            r = f"{Fore.RED}{self.right}{Style.RESET_ALL}"
        if self.level() >= 4 and self.is_leaf():
            return f"{Fore.GREEN}[{l}, {r}]{Style.RESET_ALL}"
        return f"[{l}, {r}]"

    @staticmethod
    def split_value(value: int) -> tuple[int, int]:
        return math.floor(value / 2), math.ceil(value / 2)

    def split(self) -> None:
        for side in ["left", "right"]:
            child = getattr(self, side)
            if isinstance(child, int) and child >= 10:
                if Settings.verbose:
                    print(f"Splitting {self} on side {side}")
                new_node = Node(self, *Node.split_value(child))
                setattr(self, side, new_node)
                if Settings.verbose:
                    print(self.get_tree_root())
                return

    def replace(self) -> None:
        setattr(self.root, self.side(), 0)

    def explode(self) -> None:
        if Settings.verbose:
            print(f"Exploding node {self} with parent {self.root}")
        self.update_on_own_side()
        self.update_on_other_side()
        self.replace()
        if Settings.verbose:
            print(self.get_tree_root())

    def combine(self, other: Node) -> Node:
        result = Node(None, self, other)
        self.root = result
        other.root = result
        return result

    def reduce(self) -> bool:
        node_to_explode = self.get_first_node_to_explode()
        if node_to_explode is not None:
            node_to_explode.explode()
            return True
        node_to_split = self.get_first_node_to_split()
        if node_to_split is not None:
            node_to_split.split()
            return True
        return False

    def __add__(self, other: Node) -> Node:
        result = self.combine(other)
        need_to_reduce = True
        while need_to_reduce:
            need_to_reduce = result.reduce()
        return result

    @staticmethod
    def entries_to_graph(
        entries: list[list | int], root: Optional[Node] = None
    ) -> Node:
        node = Node(root=root, left=None, right=None)
        if isinstance(entries[0], int):
            left = entries[0]
        else:
            left = Node.entries_to_graph(entries[0], root=node)
        if isinstance(entries[1], int):
            right = entries[1]
        else:
            right = Node.entries_to_graph(entries[1], root=node)
        node.left = left
        node.right = right
        return node

    def add_to_first_leaf_on_side(
        self, value: int, side: Literal["left", "right"]
    ) -> Node:
        child = getattr(self, side)
        if isinstance(child, int):
            setattr(self, side, child + value)
            return (self, side)
        else:
            if not isinstance(child, Node):
                raise TypeError("child can be Node or int.")
            return child.add_to_first_leaf_on_side(value, side)

    def update_on_own_side(self) -> None:
        own_side = self.side()
        other_side = self.other_side()
        value = getattr(self, own_side)
        if not isinstance(value, int):
            raise TypeError(f"Trying to explode non leaf node.")
        current = self
        while getattr(current, f"is_{own_side}")():
            current = current.root
        if current.is_root():
            return None
        head = current.root
        node_or_value = getattr(head, own_side)
        if isinstance(node_or_value, int):
            new_value = node_or_value + value
            setattr(head, own_side, new_value)
            return (head, own_side)
        elif isinstance(node_or_value, Node):
            return node_or_value.add_to_first_leaf_on_side(value, other_side)
        else:
            raise TypeError

    def update_on_other_side(self) -> None:
        own_side = self.side()
        other_side = self.other_side()
        value = getattr(self, other_side)
        parallel_node_or_value = getattr(self.root, other_side)
        if isinstance(parallel_node_or_value, int):
            setattr(self.root, other_side, parallel_node_or_value + value)
            return (self.root, other_side)
        elif isinstance(parallel_node_or_value, Node):
            return parallel_node_or_value.add_to_first_leaf_on_side(value, own_side)
        else:
            raise TypeError(f"{type(parallel_node_or_value)} is not valid.")

    def get_value(self) -> int:
        left_value = self.left if isinstance(self.left, int) else self.left.get_value()
        right_value = (
            self.right if isinstance(self.right, int) else self.right.get_value()
        )
        return 3 * left_value + 2 * right_value


def parse_file(path: Path) -> list[Node]:
    entries = []
    with path.open("r") as fin:
        for line in fin.readlines():
            entries.append(json.loads(line))
    return entries


def part_one(path: Path) -> int:
    entries = parse_file(path)
    entries = [Node.entries_to_graph(entry) for entry in entries]
    result = sum(entries[1:], entries[0])
    print(result)
    print(result.get_value())


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    entries = parse_file(path)
    entries = [Node.entries_to_graph(entry) for entry in entries]
    max_result = 0
    for a, b in tqdm(product(entries, entries)):
        if a is b:
            continue
        result = (deepcopy(a) + deepcopy(b)).get_value()
        max_result = max(result, max_result)
    return max_result


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
