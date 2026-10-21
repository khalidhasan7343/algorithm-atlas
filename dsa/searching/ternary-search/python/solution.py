"""First-match ternary lookup in sorted data, not unimodal optimization."""

from collections.abc import Sequence
import re
import sys
from typing import TypeVar

T = TypeVar("T")


def ternary_search(values: Sequence[T], target: T, *, validate: bool = True) -> int:
    """Return the first equivalent index or -1 in nondecreasing input.

    The iterative two-pivot lower-bound core uses only < and O(log n) work;
    default order validation adds O(n). No input mutation or slices occur.
    """
    if type(validate) is not bool:
        raise TypeError("validate must be bool")
    if validate:
        for index in range(1, len(values)):
            if values[index] < values[index - 1]:
                raise ValueError("values must be nondecreasing")
    lower, upper = 0, len(values)
    while lower < upper:
        third = (upper - lower) // 3
        first = lower + third
        second = upper - 1 - third
        if not values[first] < target:
            upper = first
        elif values[second] < target:
            lower = second + 1
        else:
            lower, upper = first + 1, second
    if lower < len(values) and not target < values[lower]:
        return lower
    return -1


def main() -> int:
    """Read target first, then sorted integer values; no leading count."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if not tokens or any(re.fullmatch(r"[+-]?[0-9]+", t) is None for t in tokens):
        print("error: expected target followed by decimal integer values", file=sys.stderr)
        return 1
    numbers = [int(token, 10) for token in tokens]
    try:
        print(ternary_search(numbers[1:], numbers[0]))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
