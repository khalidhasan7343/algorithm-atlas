"""First-match interpolation search for sorted native Python integers."""

from collections.abc import Sequence
import re
import sys


def interpolation_search(
    values: Sequence[int], target: int, *, validate: bool = True
) -> int:
    """Return the first equal index or -1, preserving input.

    Checked mode requires exact native ints (no bool/subclasses) and scans
    nondecreasing order in O(n). Unchecked mode requires those preconditions
    already established. Integer interpolation is exact, without float casts.
    """
    if type(validate) is not bool:
        raise TypeError("validate must be bool")
    if type(target) is not int:
        raise TypeError("target must be a native int")
    if validate:
        for index, value in enumerate(values):
            if type(value) is not int:
                raise TypeError("values must contain native ints")
            if index and value < values[index - 1]:
                raise ValueError("values must be nondecreasing")
    lower, upper = 0, len(values)
    found = -1
    while lower < upper and values[lower] <= target <= values[upper - 1]:
        if values[lower] == values[upper - 1]:
            return lower  # Range guard implies equality; no division by zero.
        offset = ((target - values[lower]) * (upper - lower - 1)
                  // (values[upper - 1] - values[lower]))
        position = lower + offset
        if values[position] < target:
            lower = position + 1
        else:
            if values[position] == target:
                found = position
            upper = position  # Continue left, without a linear backtracking pass.
    return found


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
        print(interpolation_search(numbers[1:], numbers[0]))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
