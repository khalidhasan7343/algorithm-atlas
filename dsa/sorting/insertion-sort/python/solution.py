"""Stable insertion sort with a reusable API and a decimal-integer CLI."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys
from typing import TypeVar


T = TypeVar("T")


def insertion_sort(values: Sequence[T]) -> list[T]:
    """Return a stable sorted copy; elements must support a consistent ``<``.

    Shift only elements strictly greater than the saved item, so equivalent
    items keep their original relative order. The input sequence is untouched.
    """
    result = list(values)
    for index in range(1, len(result)):
        item = result[index]
        position = index
        while position > 0 and item < result[position - 1]:
            result[position] = result[position - 1]
            position -= 1
        result[position] = item
    return result


def main() -> int:
    """Read whitespace-separated signed decimal integers and print the result."""
    # Integer magnitude is limited by memory, not Python's decimal digit guard.
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
    print(" ".join(str(value) for value in insertion_sort(values)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
