"""Three-way quicksort with bounded recursion and a decimal-integer CLI."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys
from typing import TypeVar


T = TypeVar("T")


def quick_sort(values: Sequence[T]) -> list[T]:
    """Return a sorted copy using three-way partitions and a middle pivot.

    Only the smaller outer partition recurses. The larger partition is handled
    by a loop, bounding stack depth by O(log n), even for poor pivot choices.
    Equivalent records can change relative order: this algorithm is unstable.
    """
    result = list(values)

    def sort_range(start: int, end: int) -> None:
        while end - start > 1:
            pivot = result[start + (end - start) // 2]
            lower, current, upper = start, start, end
            # [start,lower) < pivot; [lower,current) equivalent to pivot;
            # [current,upper) unknown; [upper,end) > pivot.
            while current < upper:
                if result[current] < pivot:
                    result[lower], result[current] = result[current], result[lower]
                    lower += 1
                    current += 1
                elif pivot < result[current]:
                    upper -= 1
                    result[current], result[upper] = result[upper], result[current]
                else:
                    current += 1
            if lower - start < end - upper:
                sort_range(start, lower)
                start = upper
            else:
                sort_range(upper, end)
                end = lower

    sort_range(0, len(result))
    return result


def main() -> int:
    """Read values only (no length prefix), rejecting malformed tokens."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
        print(
            "error: expected whitespace-separated signed decimal integers",
            file=sys.stderr,
        )
        return 1
    print(" ".join(map(str, quick_sort([int(token, 10) for token in tokens]))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
