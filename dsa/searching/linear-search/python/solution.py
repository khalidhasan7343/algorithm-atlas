"""First-match linear search, with no ordering requirement."""

from collections.abc import Sequence
import re
import sys
from typing import TypeVar

T = TypeVar("T")


def linear_search(values: Sequence[T], target: T) -> int:
    """Return the first index equal to target, or -1; never modify values."""
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def main() -> int:
    """Read target first, followed by zero or more signed decimal integers."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if not tokens or any(re.fullmatch(r"[+-]?[0-9]+", t) is None for t in tokens):
        print("error: expected target followed by decimal integer values", file=sys.stderr)
        return 1
    numbers = [int(token, 10) for token in tokens]
    print(linear_search(numbers[1:], numbers[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
