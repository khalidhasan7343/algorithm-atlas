"""Enumerate positional subsets in ascending-mask order, retaining duplicates."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "atlas_bit_support", Path(__file__).resolve().parents[2] / "bit_support.py"
)
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def solve(values: list[int] | tuple[int, ...]) -> list[list[int]]:
    _support.sequence(values, 16)
    result = []
    for mask in range(1 << len(values)):
        row = []
        for index, value in enumerate(values):
            if mask & (1 << index):
                row.append(value)
        result.append(row)
    return result


if __name__ == "__main__":
    _support.main(solve, limit=16)
