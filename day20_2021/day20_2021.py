from __future__ import annotations
from pathlib import Path
from collections import defaultdict
from functools import cached_property, lru_cache
from tqdm import tqdm

from aoc_utils import timing


@lru_cache(512)
def _list_of_bool_to_int(l: tuple[bool, ...]) -> int:
    return sum(val * 2**i for i, val in enumerate(l[::-1]))


class Image:
    def __init__(self, pixels: dict[int, set[int]], dark: bool = True):
        self.pixels = pixels
        self.dark = dark

    def count_lights(self) -> int:
        if self.dark is False:
            raise ValueError(f"Cannot count up to infinity")
        return sum(len(line) for line in self.pixels.values())

    def __str__(self) -> str:
        lines = []
        for y in range(self.min_y, self.max_y + 1):
            pixels_on_line = self.pixels.get(y, {})
            lines.append(
                "".join(
                    [
                        "#" if i in pixels_on_line else "."
                        for i in range(self.min_x, self.max_x + 1)
                    ]
                )
            )
        return "\n".join(lines)

    @classmethod
    def from_string(cls, image_string: str) -> Image:
        pixels = defaultdict(set)
        for y, line in enumerate(image_string.split("\n")):
            for x, char in enumerate(line):
                if char == "#":
                    pixels[y].add(x)
                elif char != ".":
                    raise ValueError(f"{line} contains invalid chars")
        return cls(pixels)

    def enhance(self, mapping: set[int]):
        dark = self.dark
        new_pixels = defaultdict(set)
        for y in range(self.min_y - 1, self.max_y + 2):
            for x in range(self.min_x - 1, self.max_x + 2):
                is_lit = self.get_pixel_code(y, x) in mapping
                if is_lit:
                    new_pixels[y].add(x)
        if 0 in mapping:
            dark = not self.dark
            if self.dark:
                if 2**9 - 1 in mapping:
                    raise ValueError(f"0 and {2**9} both in mapping.")
                # Create a "frame" of thickness 2 which around.
                # In the odd iterations all will be lit, in the even all
                # the pixels will be off.
                min_x, max_x = min(min(val) for val in new_pixels.values()), max(
                    max(val) for val in new_pixels.values()
                )
                min_y, max_y = min(new_pixels), max(new_pixels)
                all_x = set(range(min_x - 2, max_x + 3))
                for y in [
                    min_y - 2,
                    min_y - 1,
                    max_y + 1,
                    max_y + 2,
                ]:
                    new_pixels[y] = all_x
                for _, line in new_pixels.items():
                    for x in [
                        min_x - 2,
                        min_x - 1,
                        max_x + 1,
                        max_x + 2,
                    ]:
                        line.add(x)
        return Image(new_pixels, dark=dark)

    def get_pixel_code(self, y: int, x: int) -> int:
        pixel_string = sum(
            [self.get_horizontal_triplet(yy, x) for yy in range(y - 1, y + 2)], []
        )
        return _list_of_bool_to_int(tuple(pixel_string))

    def get_horizontal_triplet(self, y: int, x: int) -> list[bool]:
        if self.min_y <= y <= self.max_y:
            line = self.pixels.get(y, {})
            return [
                (val in line) if self.min_x <= val <= self.max_x else not self.dark
                for val in range(x - 1, x + 2)
            ]

        else:
            return [not self.dark] * 3

    @cached_property
    def min_x(self) -> int:
        return min(min(val) for val in self.pixels.values())

    @cached_property
    def max_x(self) -> int:
        return max(max(val) for val in self.pixels.values())

    @cached_property
    def min_y(self) -> int:
        return min(self.pixels)

    @cached_property
    def max_y(self) -> int:
        return max(self.pixels)


def parse_file(path: Path) -> tuple[set[int], Image]:
    with path.open("r") as fin:
        mapping_text, image_text = fin.read().split("\n\n")
    mapping = {
        i for i, char in enumerate("".join(mapping_text.split("\n"))) if char == "#"
    }
    image = Image.from_string(image_text)
    return mapping, image


def part_one(path: Path) -> int:
    mapping, image = parse_file(path)
    for _ in tqdm(
        range(50)
    ):  # For the part 1 replace with 2/home/ciro/Projects/AoC_2023/day20_2021/day20_2021.py
        image = image.enhance(mapping)
    return image.count_lights()


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)
