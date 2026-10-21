"""First-match sorted lookup with doubling followed by binary narrowing."""

from collections.abc import Sequence
import re
import sys
from typing import TypeVar

T = TypeVar("T")


def exponential_search(
    values: Sequence[T], target: T, *, validate: bool = True
) -> int:
    """Find the first equivalent index, or -1; input is never changed.

    Require nondecreasing random-access data under consistent < ordering.
    Default validation adds O(n); unchecked core costs O(1+log(p+1)), where p
    is the first not-smaller insertion position.
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
    if not values[0] < target:
        return 0 if not target < values[0] else -1
    lower = bound = 1
    while bound < size and values[bound] < target:
        lower = bound + 1
        bound = size if bound >= size - bound else bound + bound
    upper = bound + 1 if bound < size else size
    while lower < upper:
        middle = lower + (upper - lower) // 2
        if values[middle] < target:
            lower = middle + 1
        else:
            upper = middle
    if lower < size and not target < values[lower]:
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
        print(exponential_search(numbers[1:], numbers[0]))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
