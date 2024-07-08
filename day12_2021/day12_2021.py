from pathlib import Path
from collections import defaultdict, Counter

from aoc_utils import timing


class Graph:
    def __init__(self):
        self.connections: dict[str, list[str]] = defaultdict(list)

    def add_connection(self, source: str, target: str):
        self.connections[source].append(target)
        self.connections[target].append(source)

    def find_paths(self, day2: bool = False, log: bool = False):
        valid_paths = 0
        queue = [["start", neighbor] for neighbor in self.connections["start"]]
        while queue:
            path = queue.pop()
            last_visited = path[-1]
            for neighbor in self.connections[last_visited]:
                if neighbor == "end":
                    valid_paths += 1
                    if log:
                        print(path + [neighbor])
                elif neighbor.isupper() or neighbor not in path:
                    queue.append(path + [neighbor])
                elif day2:
                    count = Counter(path)
                    condition_1 = count[neighbor] < 2
                    condition_2 = all(
                        [val < 2 for key, val in count.items() if not key.isupper()]
                    )
                    condition_3 = neighbor != "start"
                    if condition_1 and condition_2 and condition_3:
                        queue.append(path + [neighbor])
        return valid_paths


def parse_file(path: Path) -> Graph:
    graph = Graph()
    with open(path, "r") as fin:
        for line in fin.readlines():
            line = line.strip()
            source, target = line.split("-")
            graph.add_connection(source.strip(), target.strip())
    return graph


def part_one(path: Path) -> int:
    graph = parse_file(path)
    return graph.find_paths()


with timing():
    result = part_one(Path(__file__).parent / "example.txt")
print(result)

# Part two


def part_two(path: Path) -> int:
    graph = parse_file(path)
    return graph.find_paths(day2=True)


with timing():
    result = part_two(Path(__file__).parent / "input.txt")
print(result)
