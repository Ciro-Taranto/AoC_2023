from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timing():
    start = perf_counter()
    yield None
    print(f"Elapsed {perf_counter() - start:2.4f} seconds.")
