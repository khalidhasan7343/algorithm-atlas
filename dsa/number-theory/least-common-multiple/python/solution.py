"""least-common-multiple: bounded canonical implementation."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_number_support", Path(__file__).resolve().parents[2]/"support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

_gcd = _support.load("euclidean-algorithm")


def solve(a: int, b: int) -> int:
    _support.operand(a)
    _support.operand(b)
    if a == 0 or b == 0:
        return 0
    return (abs(a)//_gcd.solve(a,b))*abs(b)


if __name__ == "__main__":
    _support.main(solve, 2)
