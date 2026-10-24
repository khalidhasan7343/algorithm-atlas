"""Count bits in a signed input's finite 32-bit two's-complement word."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "atlas_bit_support", Path(__file__).resolve().parents[2] / "bit_support.py"
)
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def solve(value: int) -> int:
    word = _support.integer(value) & _support.MASK
    count = 0
    while word:
        word &= word - 1
        count += 1
    return count


if __name__ == "__main__":
    _support.main(solve, scalar=True)
