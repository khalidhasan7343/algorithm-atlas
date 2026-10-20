"""Swap-based selection sort; run as an integer sorting CLI."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys
from typing import TypeVar

T = TypeVar("T")


def selection_sort(values: Sequence[T]) -> list[T]:
    """Return a sorted shallow copy using strict less-than comparisons.

    Values must provide a consistent strict ordering. This swap-based variant
    is not stable. The original sequence and its elements are not modified.
    """
    result = list(values)
    for start in range(len(result) - 1):
        minimum = start
        for index in range(start + 1, len(result)):
            if result[index] < result[minimum]:
                minimum = index
        if minimum != start:
            result[start], result[minimum] = result[minimum], result[start]
    return result


def main() -> int:
    """Read signed decimal integer tokens; reject malformed input atomically."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
        print(
            "error: expected whitespace-separated signed decimal integers",
            file=sys.stderr,
        )
        return 1
    values = [int(token, 10) for token in tokens]
    print(" ".join(map(str, selection_sort(values))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
