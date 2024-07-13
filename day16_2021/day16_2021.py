from __future__ import annotations
from pathlib import Path
from typing import Union
from dataclasses import dataclass

from aoc_utils import timing


def prod(entries: list[int]):
    value = entries[0]
    for entry in entries[1:]:
        value *= entry
    return value


operations = {
    0: sum,
    1: prod,
    2: min,
    3: max,
    5: lambda x: x[0] > x[1],
    6: lambda x: x[0] < x[1],
    7: lambda x: x[0] == x[1],
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
            raise ValueError
        return self.version + sum(packet.total_version() for packet in self.value)

    def __str__(self) -> str:
        name = "Operator" if self.type != 4 else "Literal"
        representation = [f"{name}: Version: {self.version} Type: {self.type}"]
        if self.type == 4:
            representation += [f"\t value={self.value}"]
        else:
            extra_lines = sum(
                [str(packet).split("\n") for packet in self.value], start=[]
            )
            representation += ["\t" + line for line in extra_lines]
        return "\n".join(representation)

    def execute(self) -> int:
        if self.type == 4:
            return self.value
        operation = operations[self.type]
        if not isinstance(self.value, list):
            raise ValueError
        return operation([packet.execute() for packet in self.value])


def hexa_to_binary(hexa: str) -> str:
    binary = []
    for char in hexa:
        binary.append("{:b}".format(int(char, base=16)).zfill(4))
    return "".join(binary)


def parse(message: str) -> tuple[Packet, int]:
    version, packet_type = read_header(message)
    cursor = 6  # Digits already used
    if packet_type == 4:
        package_len, value = parse_literal(message[6:])
        return Packet(version, packet_type, value), cursor + package_len
    else:
        length_type_id = message[cursor]
        cursor += 1
        if length_type_id == "0":
            sub_packets = []
            sub_message_len = int(message[cursor : cursor + 15], base=2)
            cursor += 15
            sub_message = message[cursor : cursor + sub_message_len]
            while sub_message:
                sub_packet, consumed_chars = parse(sub_message)
                sub_packets.append(sub_packet)
                sub_message = sub_message[consumed_chars:]
            return Packet(version, packet_type, sub_packets), cursor + sub_message_len
        else:
            number_of_packets = int(message[cursor : cursor + 11], base=2)
            cursor += 11
            sub_packets = []
            sub_message = message[cursor:]
            for _ in range(number_of_packets):
                sub_packet, consumed_chars = parse(sub_message)
                sub_message = sub_message[consumed_chars:]
                sub_packets.append(sub_packet)
                cursor += consumed_chars
            return Packet(version, packet_type, sub_packets), cursor


def parse_hexa(hexa_str: str) -> Packet:
    return parse(hexa_to_binary(hexa_str))[0]


def parse_literal(message: str) -> tuple[int, int]:
    digits = ""
    cursor = 0
    should_continue = True
    while should_continue:
        group = message[cursor : cursor + 5]
        should_continue = group[0] == "1"
        digits += group[1:]
        cursor += 5
    value = int(digits, base=2)
    return cursor, value


def read_header(message: str) -> tuple[int, int]:
    version = int(message[:3], base=2)
    packet_type = int(message[3:6], base=2)
    return version, packet_type


def find_total_version(packet: Packet) -> int:
    if packet.type == 4:
        return packet.version


def parse_file(path: Path) -> str:
    with path.open("r") as fin:
        return fin.read().strip()


def part_one(path: Path) -> int:
    message = parse_file(path)
    packet = parse_hexa(message)
    return packet.total_version()


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    message = parse_file(path)
    packet = parse_hexa(message)
    return packet.execute()


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
