from pathlib import Path
import networkx as nx

from aoc_utils import timing


def parse_file(path: Path) -> nx.Graph:
    graph = nx.Graph()
    with open(path, "r") as fin:
        text = fin.read()
    for line in text.splitlines():
        line = line.strip()
        source, targets = line.split(": ")
        for target in targets.split(" "):
            graph.add_edge(source, target)
            graph.add_edge(target, source)
    return graph


def part_one(path: Path) -> int:
    graph = parse_file(path)
    cutset = nx.minimum_edge_cut(graph)
    graph.remove_edges_from(cutset)
    components = nx.connected_components(graph)
    return len(components[0]) * len(components[1])


with timing():
    result = part_one(Path(__file__).parent / "input.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    parse_file(path)


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
