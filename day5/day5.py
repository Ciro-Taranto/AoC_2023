from dataclasses import dataclass
from pathlib import Path
import re
from functools import cached_property
import math
from bisect import bisect_right
from aoc_utils import timing


@dataclass
class MappingEntry:
    destination: int
    source: int
    range: int

    @cached_property
    def source_end(self) -> int:
        return self.source + self.range


class Mapping:
    def __init__(self, entries: list[MappingEntry]):
        self.entries = sorted(entries, key=lambda x: x.source)
        self._entries_sources = [entry.source for entry in self.entries]

    def __getitem__(self, value: int) -> int:
        if value < self._entries_sources[0]:
            return value
        nearest_smaller_entry = self.entries[
            bisect_right(self._entries_sources, value) - 1
        ]
        if nearest_smaller_entry.source <= value < nearest_smaller_entry.source_end:
            return (
                nearest_smaller_entry.destination + value - nearest_smaller_entry.source
            )
        return value


def parse_file(file_path: Path) -> tuple[list[int], dict[tuple[str, str], Mapping]]:
    mappings = dict()
    with open(file_path, "r") as fin:
        targets = [int(value) for value in re.findall(r"\d+", fin.readline())]
        fin.readline()
        for line in fin.readlines():
            line = line.strip()
            if matches := re.findall(r"([a-z]+)-to-([a-z]+) map:", line):
                source_name, destination_name = matches[0]
                entries = list()
            elif matches := re.findall(r"(\d+)", line):
                numbers = list(map(int, matches))
                entries.append(MappingEntry(*[int(val) for val in numbers]))
            else:
                mappings[(source_name, destination_name)] = Mapping(entries)
        mappings[(source_name, destination_name)] = Mapping(entries)
    return targets, mappings


def chain_mappings(
    value: int, source_name: str, mappings: dict[tuple[str, str], Mapping]
):
    for (new_source_name, new_target_name), mapping in mappings.items():
        if source_name != new_source_name:
            raise ValueError(f"Providing {new_source_name}, expecting {source_name}")
        value = mapping[value]
        source_name = new_target_name
    return value


# Part 2


def complete_entries(entries: list[MappingEntry]) -> tuple[list[int], list[int]]:
    entries = sorted(entries, key=lambda x: x.source)
    sources = [
        -1,
    ]
    destinations = [
        -1,
    ]
    for current_entry, next_entry in zip(entries[:-1], entries[1:]):
        sources.append(current_entry.source)
        destinations.append(current_entry.destination)
        current_end = current_entry.source + current_entry.range
        if next_entry.source > current_end:
            sources.append(current_end)
            destinations.append(current_end)
    last_entry = entries[-1]
    sources.append(last_entry.source)
    destinations.append(last_entry.destination)
    last_valid_range = last_entry.source + last_entry.range
    sources.append(last_valid_range)
    destinations.append(last_valid_range)
    sources.append(math.inf)
    destinations.append(math.inf)
    return sources, destinations


class ExtendedMapping:
    """
    Extension on mapping which "completes" the gap, so that it is complete over the integers.
    """

    def __init__(self, entries: list[MappingEntry]):
        self.sources, self.destinations = complete_entries(entries)

    def get_range(self, start_and_extension: tuple[int, int]) -> list[tuple[int, int]]:
        result = list()
        start, extension = start_and_extension
        first_index = current_index = bisect_right(self.sources, start) - 1
        last_index = bisect_right(self.sources, start + extension)
        for index in range(first_index, last_index):
            source, destination = self.get_source_and_destination(index)
            next_source, _ = self.get_source_and_destination(index + 1)
            destination_start = destination + start - source
            current_extension = min(extension, next_source - start)
            result.append((destination_start, current_extension))
            extension -= current_extension
            start = next_source
            current_index += 1
        return result

    def get_source_and_destination(self, index: int):
        return self.sources[index], self.destinations[index]

    def __getitem__(self, value: int) -> int:
        index = bisect_right(self.sources, value) - 1
        source, destination = self.get_source_and_destination(index)
        return destination + value - source


def chain_mappings_for_range(
    ranges: list[tuple[int, int]], mappings: dict[tuple[int, int], ExtendedMapping]
) -> list[tuple[int, int]]:
    for _, mapping in mappings.items():
        ranges = sum(map(mapping.get_range, ranges), [])
    return ranges


def part_one(input_path: Path) -> int:
    seeds, mappings = parse_file(input_path)
    mappings = {key: ExtendedMapping(val.entries) for key, val in mappings.items()}
    values = [chain_mappings(seed, "seed", mappings) for seed in seeds]
    return min(values)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)


def part_two(input_path: Path) -> int:
    seeds, mappings = parse_file(input_path)
    mappings = {key: ExtendedMapping(val.entries) for key, val in mappings.items()}
    ranges = [(seeds[i], seeds[i + 1]) for i in range(0, len(seeds), 2)]
    target_ranges = chain_mappings_for_range(ranges, mappings)
    return min([target_range[0] for target_range in target_ranges])


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
