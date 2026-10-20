"""Shell sort with Knuth's 3h+1 gaps and gapped insertion passes."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys
from typing import TypeVar


T = TypeVar("T")


def shell_sort(values: Sequence[T]) -> list[T]:
    """Return an unstable sorted copy, preserving the input sequence.

    Elements need a consistent ``<``. The core uses constant extra slots;
    the returned copy requires linear storage. No gap list is allocated.
    """
    result = list(values)
    gap = 1
    while gap < len(result) // 3:
        gap = 3 * gap + 1
    while gap >= 1:
        for index in range(gap, len(result)):
            item = result[index]
            position = index
            while position >= gap and item < result[position - gap]:
                result[position] = result[position - gap]
                position -= gap
            result[position] = item
        gap //= 3
    return result


def main() -> int:
    """Read whitespace-separated signed decimal integers, without a count."""
    tokens = sys.stdin.read().split()
    try:
        if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
            raise ValueError("expected signed decimal integers")
        values = [int(token, 10) for token in tokens]
    except ValueError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    print(" ".join(str(value) for value in shell_sort(values)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
