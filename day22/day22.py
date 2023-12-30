from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, replace

from aoc_utils import timing


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class Block:
    start: Coordinate
    end: Coordinate

    def __lt__(self, other: Block) -> bool:
        return self.start.z < other.start.z

    def shift_down(self, lower_z: int) -> Block:
        steps_below = self.start.z - lower_z
        if steps_below < 0:
            raise ValueError("blocks do not move up")
        return Block(
            replace(self.start, z=self.start.z - steps_below),
            replace(self.end, z=self.end.z - steps_below),
        )


def parse_file(path: Path) -> list[Block]:
    blocks = []

    def to_coordinate(coordinate_str: str) -> Coordinate:
        return Coordinate(*list(map(int, coordinate_str.split(","))))

    with open(path, "r") as fin:
        for line in fin.readlines():
            start_str, end_str = line.strip().split("~")
            blocks.append(Block(to_coordinate(start_str), to_coordinate(end_str)))
    return blocks


def blocks_overlap(first_block: Block, second_block: Block) -> bool:
    return (
        max(first_block.start.x, second_block.start.x)
        <= min(first_block.end.x, second_block.end.x)
    ) and (
        max(first_block.start.y, second_block.start.y)
        <= min(first_block.end.y, second_block.end.y)
    )


def move_all_blocks_to_the_ground(blocks: list[Block]) -> list[Block]:
    blocks = sorted(blocks)
    settled_blocks: list[Block] = list()
    for block in blocks:
        lower_possible_z = 1
        # This scales like N**2, any way to make NlogN? -> yes, index blocks by start and end.
        for low_block in settled_blocks:
            if blocks_overlap(block, low_block):
                lower_possible_z = max(lower_possible_z, low_block.end.z + 1)
        settled_block = block.shift_down(lower_possible_z)
        settled_blocks.append(settled_block)
    return settled_blocks


def find_supporting_blocks(
    blocks: list[Block],
) -> tuple[dict[Block, set[Block]], dict[Block, set[Block]]]:
    blocks = sorted(blocks)
    supports = {block: set() for block in blocks}
    supported_by = {block: set() for block in blocks}
    for i, block_above in enumerate(blocks):
        for block_below in blocks[:i]:
            if block_above.start.z == block_below.end.z + 1 and blocks_overlap(
                block_above, block_below
            ):
                supports[block_below].add(block_above)
                supported_by[block_above].add(block_below)
    return supports, supported_by


def find_removable_blocks(blocks: list[Block]) -> set[Block]:
    supports, supported_by = find_supporting_blocks(blocks)
    removable_blocks = set()
    for block, supported_blocks in supports.items():
        if all(
            len(supported_by[supported_block]) > 1
            for supported_block in supported_blocks
        ):
            removable_blocks.add(block)
    return removable_blocks


def part_one(path: Path) -> int:
    blocks = parse_file(path)
    blocks = move_all_blocks_to_the_ground(blocks)
    removable_blocks = find_removable_blocks(blocks)
    return len(removable_blocks)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def explode_chain_reaction(
    block: Block,
    supports: dict[Block, set[Block]],
    supported_by: dict[Block, set[Block]],
) -> int:
    falling_blocks = new_falling_blocks = {
        supported_block
        for supported_block in supports[block]
        if len(supported_by[supported_block]) == 1
    }
    while True:
        candidates = set.union(
            *[supports[falling_block] for falling_block in new_falling_blocks]
        )
        new_falling_blocks = {
            candidate
            for candidate in candidates
            if not supported_by[candidate].difference(falling_blocks)
        }
        if not new_falling_blocks:
            break
        falling_blocks = falling_blocks.union(new_falling_blocks)
    return len(falling_blocks)


def part_two(path: Path) -> int:
    blocks = parse_file(path)
    blocks = move_all_blocks_to_the_ground(blocks)
    blocks = sorted(blocks)
    blocks_that_can_be_removed = find_removable_blocks(blocks)
    supports, supported_by = find_supporting_blocks(blocks)
    total = 0
    for block in set(blocks).difference(blocks_that_can_be_removed):
        total += explode_chain_reaction(block, supports, supported_by)
    return total


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
