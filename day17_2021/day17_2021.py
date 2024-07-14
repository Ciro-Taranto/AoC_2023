from pathlib import Path
from collections import defaultdict
import re
from itertools import product

from aoc_utils import timing


def find_max_distance_coverable(speed: int) -> int:
    # Aka, the gauss summation
    return (speed * (speed + 1)) // 2


def find_minimal_x_speed_to_reach_target(target: int) -> int:
    # TODO: Invert the gauss formula to obtain this analytically
    speed = 1
    distance_coverable = find_max_distance_coverable(speed)
    while distance_coverable < target:
        speed += 1
        distance_coverable = find_max_distance_coverable(speed)
    return speed


def find_time_to_reach_target(speed: int, target: int) -> int:
    position = 0
    steps = 0
    while position < target:
        position += speed
        speed -= 1
        steps += 1
    return steps


def parse_file(path: Path) -> tuple[tuple[int, int], tuple[int, int]]:
    with path.open("r") as fin:
        text = fin.read()
        (min_x, max_x), (min_y, y_max) = re.findall(r"(-*\d+)..(-*\d+)", text)
    return (int(min_x), int(max_x)), (int(min_y), int(y_max))


def part_one(path: Path) -> int:
    (min_x, max_x), (min_y, y_max) = parse_file(path)
    # The speed has to be such that it does not go below min_y after one single step.
    # This means that the y axis will be at 0.
    # The velocity has to be <= -min_y - 1, so that after one step
    # the it will end up exactly at the border.
    max_velocity = -min_y - 1
    return find_max_distance_coverable(max_velocity)


with timing():
    result = part_one(Path(__file__).parent / "input.txt")

print(result)

# Part two


def part_two(path: Path) -> int:
    (min_x, max_x), (min_y, max_y) = parse_file(path)
    # The minimal and maximal y velocities are easy to find.
    max_y_velocity = -min_y - 1
    min_y_velocity = -max_y_velocity - 1
    # The minimal x velocity is also easy to find:
    # The speed such that the probe does not free fall before the target
    min_x_velocity = find_minimal_x_speed_to_reach_target(min_x)
    max_x_velocity = max_x
    # Now the problem is to find the combinations
    # This can be done naive, by iteration or smart
    x_speeds_that_stop_on_target = find_x_speed_that_stay_on_target(
        min_x, max_x, min_x_velocity, max_x_velocity
    )
    x_speeds_that_touch_the_target = find_when_on_target(
        0, min_x, max_x, max(x_speeds_that_stop_on_target) + 1, max_x_velocity
    )
    y_speeds_that_touch_the_target = find_when_on_target(
        0, max_y, min_y, min_y_velocity, max_y_velocity
    )
    valid_speeds = set()
    for initial_x_speed, x_times in x_speeds_that_touch_the_target.items():
        for initial_y_speed, y_times in y_speeds_that_touch_the_target.items():
            if x_times.intersection(y_times):
                valid_speeds.add((initial_x_speed, initial_y_speed))
    for initial_x_speed, min_x_time in x_speeds_that_stop_on_target.items():
        for initial_y_speed, y_times in y_speeds_that_touch_the_target.items():
            if min_x_time <= max(y_times):
                valid_speeds.add((initial_x_speed, initial_y_speed))

    return len(valid_speeds)


def find_x_speed_that_stay_on_target(
    min_x: int, max_x: int, min_x_velocity: int, max_x_velocity: int
) -> dict[int, int]:
    minimal_times_to_reach_target = {}
    for speed in range(min_x_velocity, max_x_velocity + 1):
        max_distance_coverable = find_max_distance_coverable(speed)
        if min_x <= max_distance_coverable <= max_x:
            minimal_times_to_reach_target[speed] = find_time_to_reach_target(
                speed, min_x
            )
        elif max_distance_coverable > max_x:
            return minimal_times_to_reach_target
        else:
            raise RuntimeError


def find_when_on_target(
    start_position: int,
    target_start: int,
    target_end: int,
    min_velocity: int,
    max_velocity: int,
) -> dict[int, set[int]]:
    times_to_reach_by_speed = defaultdict(set)
    if target_start >= start_position:
        is_end_of_target_ahead = int.__le__
        is_start_of_target_behind = int.__ge__
    else:
        is_end_of_target_ahead = int.__ge__
        is_start_of_target_behind = int.__le__
    for speed in range(min_velocity, max_velocity + 1):
        current_position = start_position
        current_speed = speed
        current_steps = 0
        while is_end_of_target_ahead(current_position, target_end):
            if is_start_of_target_behind(current_position, target_start):
                times_to_reach_by_speed[speed].add(current_steps)
            current_position += current_speed
            current_speed -= 1
            current_steps += 1
    return times_to_reach_by_speed


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
