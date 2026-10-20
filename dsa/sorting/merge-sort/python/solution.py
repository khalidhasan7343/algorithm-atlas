"""Stable top-down merge sort with one reusable auxiliary buffer."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys
from typing import TypeVar


T = TypeVar("T")


def merge_sort(values: Sequence[T]) -> list[T]:
    """Return a stable sorted copy; values must support a consistent ``<``.

    The input sequence is unchanged. Element objects are shallowly copied,
    never modified. Every nontrivial range is merged, including sorted ranges.
    """
    result = list(values)
    buffer = result.copy()

    def sort_range(start: int, end: int) -> None:
        if end - start < 2:
            return
        middle = start + (end - start) // 2
        sort_range(start, middle)
        sort_range(middle, end)

        left, right = start, middle
        for destination in range(start, end):
            # Taking the left item on equal keys preserves original order.
            if right == end or (
                left < middle and not result[right] < result[left]
            ):
                buffer[destination] = result[left]
                left += 1
            else:
                buffer[destination] = result[right]
                right += 1
        for position in range(start, end):
            result[position] = buffer[position]

    sort_range(0, len(result))
    return result


def main() -> int:
    """Read signed decimal integers from stdin and print their sorted order."""
    tokens = sys.stdin.read().split()
    try:
        if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
            raise ValueError("expected signed decimal integers")
        values = [int(token, 10) for token in tokens]
    except ValueError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    print(" ".join(str(value) for value in merge_sort(values)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
