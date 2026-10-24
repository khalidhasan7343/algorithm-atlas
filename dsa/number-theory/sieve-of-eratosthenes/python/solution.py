"""sieve-of-eratosthenes: bounded canonical implementation."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_number_support", Path(__file__).resolve().parents[2]/"support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def solve(limit: int) -> list[int]:
    _support.bounded(limit, 0, 1000000)
    marked = bytearray(limit+1)
    p = 2
    while p*p <= limit:
        if not marked[p]:
            for multiple in range(p*p,limit+1,p):
                marked[multiple] = 1
        p += 1
    return [value for value in range(2,limit+1) if not marked[value]]


if __name__ == "__main__":
    _support.main(solve, 1)
