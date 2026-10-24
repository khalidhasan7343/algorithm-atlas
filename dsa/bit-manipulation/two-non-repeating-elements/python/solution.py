"""Two unique elements via unsigned low-bit partition, checked by default."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "atlas_bit_support", Path(__file__).resolve().parents[2] / "bit_support.py"
)
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def partition_candidates(values: list[int] | tuple[int, ...]) -> list[int]:
    """O(n)/O(1) core under exactly two singletons and otherwise exact pairs."""
    _support.sequence(values)
    if len(values) < 2 or len(values) % 2:
        raise ValueError("expected even length at least two")
    total = 0
    for value in values:
        total ^= value & _support.MASK
    if total == 0:
        raise ValueError("two distinct singleton words must have nonzero XOR")
    differing_bit = total & ((-total) & _support.MASK)
    first = second = 0
    for value in values:
        word = value & _support.MASK
        if word & differing_bit:
            first ^= word
        else:
            second ^= word
    return sorted((_support.signed(first), _support.signed(second)))


def solve(values: list[int] | tuple[int, ...]) -> list[int]:
    _support.paired(values, 2)
    return partition_candidates(values)


if __name__ == "__main__":
    _support.main(solve)
