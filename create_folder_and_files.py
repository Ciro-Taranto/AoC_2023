import sys
from pathlib import Path


if __name__ == "__main__":
    day = sys.argv[1]
    folder = Path(__file__).parent / f"day{day}"
    folder.mkdir(exist_ok=True)
    filenames = ["input.txt", "example.txt", f"day{day}.py"]
    for filename in filenames:
        with open(folder / filename, "w") as f:
            pass
