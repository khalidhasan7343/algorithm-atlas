"""First-match jump search with square-root blocks and a local scan."""

from collections.abc import Sequence
from math import isqrt
import re
import sys
from typing import TypeVar

T = TypeVar("T")


def jump_search(values: Sequence[T], target: T, *, validate: bool = True) -> int:
    """Return the first equivalent index, or -1, without changing input.

    Require nondecreasing random-access data under a consistent < ordering.
    Validation costs O(n); validate=False skips it and requires that precondition.
    """
    if type(validate) is not bool:
        raise TypeError("validate must be bool")
    if validate:
        for index in range(1, len(values)):
            if values[index] < values[index - 1]:
                raise ValueError("values must be nondecreasing")
    size = len(values)
    if size == 0:
        return -1
    step = max(1, isqrt(size))
    start, end = 0, min(step, size)
    while values[end - 1] < target:
        start = end
        if start == size:
            return -1
        end = start + min(step, size - start)
    for index in range(start, end):
        if not values[index] < target:
            return index if not target < values[index] else -1
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
        print(jump_search(numbers[1:], numbers[0]))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
