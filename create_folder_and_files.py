import sys
from pathlib import Path


if __name__ == "__main__":
    day = sys.argv[1]
    folder = Path(__file__).parent / f"day{day}"
    folder.mkdir(exist_ok=True)
    filenames = ["input.txt", "example.txt"]
    for filename in filenames:
        with open(folder / filename, "w") as f:
            pass
    with open(Path(__file__).parent / "template.py", "r") as fin:
        template = fin.read()
    with open(folder / f"day{day}.py", "w") as fout:
        fout.write(template)
