"""Stable bubble sort with an early exit; run as an integer sorting CLI."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys
from typing import TypeVar

T = TypeVar("T")


def bubble_sort(values: Sequence[T]) -> list[T]:
    """Return a sorted shallow copy using only strict less-than comparisons.

    Values must provide a consistent strict ordering. Equivalent values retain
    their input order. The original sequence and its elements are not modified.
    """
    result = list(values)
    for end in range(len(result) - 1, 0, -1):
        swapped = False
        for index in range(end):
            if result[index + 1] < result[index]:
                result[index], result[index + 1] = result[index + 1], result[index]
                swapped = True
        if not swapped:
            break
    return result


def main() -> int:
    """Read signed decimal integer tokens; reject malformed input atomically."""
    # The CLI, like the reusable function, supports arbitrary-size Python ints.
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
    print(" ".join(map(str, bubble_sort(values))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
