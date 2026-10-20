"""Heap sort using bottom-up max-heap construction and iterative sift-down."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys
from typing import TypeVar


T = TypeVar("T")


def heap_sort(values: Sequence[T]) -> list[T]:
    """Return an ordered copy; elements need a consistent ``<`` relation.

    Input is unchanged. Heap sort is not stable. Beyond the returned copy,
    iterative heap construction and extraction use constant auxiliary space.
    """
    result = list(values)

    def sift_down(root: int, count: int) -> None:
        # Only internal nodes have children; count is an exclusive boundary.
        while root < count // 2:
            child = 2 * root + 1
            if child + 1 < count and result[child] < result[child + 1]:
                child += 1
            if not result[root] < result[child]:
                return
            result[root], result[child] = result[child], result[root]
            root = child

    for parent in range(len(result) // 2 - 1, -1, -1):
        sift_down(parent, len(result))
    for end in range(len(result) - 1, 0, -1):
        result[0], result[end] = result[end], result[0]
        sift_down(0, end)
    return result


def main() -> int:
    """Read signed decimal integers without a count, then print sorted data."""
    tokens = sys.stdin.read().split()
    try:
        if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
            raise ValueError("expected signed decimal integers")
        values = [int(token, 10) for token in tokens]
    except ValueError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    print(" ".join(str(value) for value in heap_sort(values)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
