"""euclidean-algorithm: bounded canonical implementation."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_number_support", Path(__file__).resolve().parents[2]/"support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def solve(a: int, b: int) -> int:
    _support.operand(a)
    _support.operand(b)
    a,b = abs(a),abs(b)
    while b:
        a,b = b,a%b
    return a


if __name__ == "__main__":
    _support.main(solve, 2)
