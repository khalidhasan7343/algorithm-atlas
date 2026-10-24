"""Checked unique element, with an explicitly assumption-based XOR candidate."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "atlas_bit_support", Path(__file__).resolve().parents[2] / "bit_support.py"
)
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def xor_candidate(values: list[int] | tuple[int, ...]) -> int:
    """O(n)/O(1) XOR core; caller promises one singleton and exact pairs."""
    _support.sequence(values)
    if not values or len(values) % 2 != 1:
        raise ValueError("expected nonempty odd-length input")
    word = 0
    for value in values:
        word ^= value & _support.MASK
    return _support.signed(word)


def solve(values: list[int] | tuple[int, ...]) -> int:
    """Validate all multiplicities before returning the XOR-computed answer."""
    _support.paired(values, 1)
    return xor_candidate(values)


if __name__ == "__main__":
    _support.main(solve)
