from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import sympy

from aoc_utils import timing


@dataclass
class Line2D:
    a: float
    b: float
    x0: int
    y0: int
    vx: int
    vy: int

    @classmethod
    def from_position_and_velocities_string(cls, input_string: str) -> Line2D:
        positions, velocities = input_string.split("@")
        positions = [int(position) for position in positions.split(",")]
        velocities = [int(velocity) for velocity in velocities.split(",")]
        assert velocities[0] != 0
        a = velocities[1] / velocities[0]
        b = positions[1] - a * positions[0]
        return Line2D(a, b, positions[0], positions[1], velocities[0], velocities[1])

    def intercept(
        self, other: Line2D
    ) -> Optional[tuple[int, int,]]:
        if self.a == other.a:
            return None
        x = (self.b - other.b) / (other.a - self.a)
        y = self.a * x + self.b
        return x, y

    def get_time(self, x: float) -> float:
        return (x - self.x0) / self.vx


def parse_file(path: Path) -> list[Line2D]:
    with open(path, "r") as fin:
        input_text = fin.read()
    return list(
        map(Line2D.from_position_and_velocities_string, input_text.splitlines())
    )


def part_one(path: Path) -> int:
    lines = parse_file(path)
    minimum_intercept = 200000000000000
    maximum_intercept = 400000000000000
    intercepting = 0
    for i, line in enumerate(lines):
        for other_line in lines[:i]:
            point = line.intercept(other_line)
            if point:
                t1 = line.get_time(point[0])
                t2 = other_line.get_time(point[0])
                if (
                    (minimum_intercept <= point[0] <= maximum_intercept)
                    and (minimum_intercept <= point[1] <= maximum_intercept)
                    and t1 > 0
                    and t2 > 0
                ):
                    intercepting += 1
    return intercepting


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


@dataclass
class Line3D:
    x0: int
    y0: int
    z0: int
    vx: int
    vy: int
    vz: int

    @classmethod
    def from_input_str(cls, input_str: str):
        return cls(*list(int(val) for val in input_str.replace("@", ",").split(",")))


def part_two(path: Path) -> int:
    with open(path, "r") as fin:
        lines = list(map(Line3D.from_input_str, fin.read().splitlines()))
    x, y, z, vx, vy, vz = sympy.symbols("x, y, z, vx, vy, vz")
    equations = []
    for i, line in enumerate(lines):
        equations.append(
            (vx - line.vx) * (y - line.y0) + (vy - line.vy) * (line.x0 - x)
        )
        equations.append(
            (vx - line.vx) * (z - line.z0) + (vz - line.vz) * (line.x0 - x)
        )
        if i < 2:
            continue
        sol = sympy.solve(equations)
        if len(sol) == 1:
            break
    sol = sol[0]
    return sol[x] + sol[y] + sol[z]


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
