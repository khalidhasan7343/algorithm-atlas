"""Stable counting sort for native integers with a bounded key range."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys


def counting_sort(
    values: Sequence[int], *, max_range: int = 1_000_000
) -> list[int]:
    """Return sorted native integers without changing the input.

    ``max_range`` is a positive native integer, validated even for empty input.
    The inclusive range ``max(values) - min(values) + 1`` must not exceed it.
    Booleans and integer subclasses are rejected along with noninteger values.
    """
    if type(max_range) is not int:
        raise TypeError("max_range must be a native integer")
    if max_range <= 0:
        raise ValueError("max_range must be positive")
    items = list(values)
    if any(type(value) is not int for value in items):
        raise TypeError("values must contain only native integers")
    if not items:
        return []

    minimum = min(items)
    key_range = max(items) - minimum + 1
    if key_range > max_range:
        raise ValueError(f"key range {key_range} exceeds max_range {max_range}")

    counts = [0] * key_range
    for value in items:
        counts[value - minimum] += 1
    for index in range(1, key_range):
        counts[index] += counts[index - 1]

    result = [0] * len(items)
    # Reserve the final free position for each key, traversing right to left.
    for value in reversed(items):
        offset = value - minimum
        counts[offset] -= 1
        result[counts[offset]] = value
    return result


def main() -> int:
    """Sort signed ASCII decimal integers using the default range limit."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
        print("error: expected signed decimal integers", file=sys.stderr)
        return 1
    try:
        result = counting_sort([int(token, 10) for token in tokens])
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(" ".join(map(str, result)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
