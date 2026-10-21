"""First equivalent index via iterative lower-bound binary search."""

from collections.abc import Sequence
import re
import sys
from typing import TypeVar

T = TypeVar("T")


def binary_search(values: Sequence[T], target: T, *, validate: bool = True) -> int:
    """Find the first equivalent item in nondecreasing random-access data.

    Default validation costs O(n). Set validate=False only for data already
    known to satisfy a consistent strict ordering; the core costs O(log n).
    Equivalence means neither item is less than the other. Input is unchanged.
    """
    if type(validate) is not bool:
        raise TypeError("validate must be bool")
    if validate:
        for index in range(1, len(values)):
            if values[index] < values[index - 1]:
                raise ValueError("values must be nondecreasing")
    lower, upper = 0, len(values)
    while lower < upper:
        middle = lower + (upper - lower) // 2
        if values[middle] < target:
            lower = middle + 1
        else:
            upper = middle
    if lower < len(values) and not target < values[lower]:
        return lower
    return -1


def main() -> int:
    """Read target, then sorted integer values; no leading count."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if not tokens or any(re.fullmatch(r"[+-]?[0-9]+", t) is None for t in tokens):
        print("error: expected target followed by decimal integer values", file=sys.stderr)
        return 1
    numbers = [int(token, 10) for token in tokens]
    try:
        print(binary_search(numbers[1:], numbers[0]))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
