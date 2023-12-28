from __future__ import annotations
from pathlib import Path
from enum import Enum
from typing import Optional
from collections import defaultdict, deque
from tqdm import tqdm
from math import lcm


from aoc_utils import timing


class Pulse(Enum):
    high = "high"
    low = "low"


flip_flop_pulses = {False: Pulse.high, True: Pulse.low}


def parse_file(path: Path) -> dict[str, Module]:
    with open(path, "r") as fin:
        configuration_lines = fin.readlines()
    # first build a graph to collect all sources of the connectors
    modules = list()
    sources = defaultdict(list)
    for line in configuration_lines:
        module, targets = line.strip().split(" -> ")
        targets = targets.strip().replace(" ", "").split(",")
        if module.startswith("%"):
            module_name, module_type = module[1:], FlipFlop
        elif module.startswith("&"):
            module_name, module_type = module[1:], Conjunction
        elif module == "broadcaster":
            module_name, module_type = module, Module
        else:
            raise ValueError
        for target in targets:
            sources[target].append(module_name)
        modules.append([module_name, module_type, targets])
    configuration: dict[str, Module] = {}
    for module_name, module_type, targets in modules:
        if module_type == Conjunction:
            module_sources = sources[module_name]
            configuration[module_name] = module_type(targets, module_sources)
        else:
            configuration[module_name] = module_type(targets)
    return configuration


class Module:
    def __init__(self, targets: list[str]):
        self.targets = targets


class FlipFlop(Module):
    def __init__(self, targets: list[str]):
        # False means "off" in this context
        self.state = False
        super().__init__(targets)

    def __call__(self, pulse: Pulse, sender: str) -> Optional[Pulse]:
        if pulse == Pulse.high:
            return None
        pulse = flip_flop_pulses[self.state]
        self.state = not self.state
        return pulse


class Conjunction(Module):
    def __init__(self, targets: list[str], sources: list[str]):
        self.sources = {source: Pulse.low for source in sources}
        super().__init__(targets)

    def __call__(self, pulse: Pulse, sender: str) -> Pulse:
        self.sources[sender] = pulse
        return (
            Pulse.low
            if all(val == Pulse.high for val in self.sources.values())
            else Pulse.high
        )


def part_one(path: Path) -> int:
    configuration = parse_file(path)
    pulses = {Pulse.low: 0, Pulse.high: 0}
    for _ in tqdm(range(1000)):
        pulses[Pulse.low] += 1  # This is the button
        message_queue = deque(
            [
                ("broadcaster", receiver, Pulse.low)
                for receiver in configuration["broadcaster"].targets
            ]
        )
        while message_queue:
            sender, receiver, pulse = message_queue.popleft()
            pulses[pulse] += 1
            response_pulse = (
                configuration[receiver](pulse, sender)
                if receiver in configuration
                else None
            )
            if response_pulse is not None:
                for target in configuration[receiver].targets:
                    message_queue.append((receiver, target, response_pulse))
    return pulses[pulse.low] * pulses[pulse.high]


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    configuration = parse_file(path)
    target_module = "rx"
    module_name, module_connected_to_target = [
        (key, module)
        for key, module in configuration.items()
        if target_module in module.targets
    ][0]
    module_connected_to_target: Conjunction
    # The rx module is connected to a Conjunction, in order to receive a low pulse all the sources
    # must have an high value -> find the periodicity of high values
    sources = list(module_connected_to_target.sources)
    high_pulse_observations = defaultdict(list)
    button_pushes = 0
    while not all(
        len(high_pulse_observations.get(source, [])) > 2 for source in sources
    ):
        button_pushes += 1
        message_queue = deque(
            [
                ("broadcaster", receiver, Pulse.low)
                for receiver in configuration["broadcaster"].targets
            ]
        )
        while message_queue:
            sender, receiver, pulse = message_queue.popleft()
            if receiver == module_name and sender in sources and pulse == Pulse.high:
                high_pulse_observations[sender].append(button_pushes)

            response_pulse = (
                configuration[receiver](pulse, sender)
                if receiver in configuration
                else None
            )

            if response_pulse is not None:
                for target in configuration[receiver].targets:
                    message_queue.append((receiver, target, response_pulse))
    periods = list()
    for source in sources:
        observations = high_pulse_observations[source]
        differences = set(
            [x[1] - x[0] for x in zip(observations[:-1], observations[1:])]
        )
        periods.append(differences.pop())
        if differences:
            raise ValueError
    return lcm(*periods)


def part_two_trivial(path: Path) -> int:
    """
    This will not work, it would take too much time (roughly 300-400 years)
    """
    configuration = parse_file(path)
    can_stop = False
    for button_pushes in tqdm(range(0, 1000000)):
        if can_stop:
            break
        message_queue = deque(
            [
                ("broadcaster", receiver, Pulse.low)
                for receiver in configuration["broadcaster"].targets
            ]
        )
        while message_queue:
            sender, receiver, pulse = message_queue.popleft()

            response_pulse = (
                configuration[receiver](pulse, sender)
                if receiver in configuration
                else None
            )
            if receiver == "rx" and pulse == Pulse.low:
                can_stop = True

            if response_pulse is not None:
                for target in configuration[receiver].targets:
                    message_queue.append((receiver, target, response_pulse))
    return button_pushes


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
