from __future__ import annotations
from pathlib import Path
from typing import Union, Tuple
from dataclasses import dataclass
from functools import reduce

from aoc_utils import timing


def prod(entries: list[int]) -> int:
    return reduce(lambda x, y: x * y, entries)


operations = {
    0: sum,
    1: prod,
    2: min,
    3: max,
    5: lambda x: int(x[0] > x[1]),
    6: lambda x: int(x[0] < x[1]),
    7: lambda x: int(x[0] == x[1]),
}


@dataclass
class Packet:
    version: int
    type: int
    value: Union[int, list[Packet]]

    def total_version(self) -> int:
        if self.type == 4:
            return self.version
        if not isinstance(self.value, list):
            raise ValueError("Packet value should be a list for non-literal packets.")
        return self.version + sum(packet.total_version() for packet in self.value)

    def __str__(self) -> str:
        name = "Operator" if self.type != 4 else "Literal"
        representation = [f"{name}: Version: {self.version} Type: {self.type}"]
        if self.type == 4:
            representation.append(f"\t value={self.value}")
        else:
            extra_lines = sum(
                (str(packet).split("\n") for packet in self.value), start=[]
            )
            representation.extend("\t" + line for line in extra_lines)
        return "\n".join(representation)

    def execute(self) -> int:
        if self.type == 4:
            return self.value
        operation = operations[self.type]
        if not isinstance(self.value, list):
            raise ValueError("Packet value should be a list for non-literal packets.")
        return operation([packet.execute() for packet in self.value])


def hexa_to_binary(hexa: str) -> str:
    return "".join(f"{int(char, 16):04b}" for char in hexa)


def parse(message: str) -> Tuple[Packet, int]:
    version, packet_type = read_header(message)
    cursor = 6  # Digits already used
    if packet_type == 4:
        package_len, value = parse_literal(message[cursor:])
        return Packet(version, packet_type, value), cursor + package_len

    length_type_id = message[cursor]
    cursor += 1
    sub_packets = []
    if length_type_id == "0":
        sub_message_len = int(message[cursor : cursor + 15], 2)
        cursor += 15
        sub_message = message[cursor : cursor + sub_message_len]
        while sub_message:
            sub_packet, consumed_chars = parse(sub_message)
            sub_packets.append(sub_packet)
            sub_message = sub_message[consumed_chars:]
        cursor += sub_message_len
    else:
        number_of_packets = int(message[cursor : cursor + 11], 2)
        cursor += 11
        sub_message = message[cursor:]
        for _ in range(number_of_packets):
            sub_packet, consumed_chars = parse(sub_message)
            sub_packets.append(sub_packet)
            sub_message = sub_message[consumed_chars:]
            cursor += consumed_chars

    return Packet(version, packet_type, sub_packets), cursor


def parse_hexa(hexa_str: str) -> Packet:
    return parse(hexa_to_binary(hexa_str))[0]


def parse_literal(message: str) -> Tuple[int, int]:
    digits = ""
    cursor = 0
    while True:
        group = message[cursor : cursor + 5]
        digits += group[1:]
        cursor += 5
        if group[0] == "0":
            break
    return cursor, int(digits, 2)


def read_header(message: str) -> Tuple[int, int]:
    version = int(message[:3], 2)
    packet_type = int(message[3:6], 2)
    return version, packet_type


def parse_file(path: Path) -> str:
    with path.open("r") as fin:
        return fin.read().strip()


def part_one(path: Path) -> int:
    message = parse_file(path)
    packet = parse_hexa(message)
    return packet.total_version()


def part_two(path: Path) -> int:
    message = parse_file(path)
    packet = parse_hexa(message)
    return packet.execute()


if __name__ == "__main__":
    input_path = Path(__file__).parent / "input.txt"

    with timing():
        result = part_one(input_path)
    print(result)

    with timing():
        result = part_two(input_path)
    print(result)
