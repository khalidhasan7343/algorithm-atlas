"""Stable bucket sort for finite native real values in the closed unit interval."""

from __future__ import annotations

from collections.abc import Sequence
import math
import re
import sys


def bucket_sort(
    values: Sequence[float], *, bucket_count: int | None = None
) -> list[float]:
    """Return a sorted shallow copy; accept native int/float values in [0, 1].

    The default bucket count is max(1, n). Explicit counts must be positive
    native ints within the platform container-index range. Each bucket uses
    stable insertion sort; equal original objects retain their relative order.
    """
    result = list(values)
    if bucket_count is None:
        bucket_count = max(1, len(result))
    elif type(bucket_count) is not int:
        raise TypeError("bucket_count must be a native int or None")
    if bucket_count < 1 or bucket_count > sys.maxsize:
        raise ValueError(
            "bucket_count must be positive and fit the platform index range"
        )
    for value in result:
        if type(value) not in (int, float):
            raise TypeError(
                "bucket_sort requires native int/float values; bool is excluded"
            )
        # Check range first: math.isfinite on an enormous int can overflow.
        if not 0 <= value <= 1 or not math.isfinite(value):
            raise ValueError("bucket_sort requires finite values in [0, 1]")
    if len(result) < 2:
        return result

    buckets: list[list[float]] = [[] for _ in range(bucket_count)]
    for value in result:
        index = min(bucket_count - 1, int(value * bucket_count))
        buckets[index].append(value)

    result.clear()
    for bucket in buckets:
        for index in range(1, len(bucket)):
            value = bucket[index]
            position = index
            while position > 0 and value < bucket[position - 1]:
                bucket[position] = bucket[position - 1]
                position -= 1
            bucket[position] = value
        result.extend(bucket)
    return result


def main() -> int:
    """Read finite decimal/scientific real tokens in [0, 1] and print a line."""
    tokens = sys.stdin.read().split()
    decimal = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
    if any(re.fullmatch(decimal, token) is None for token in tokens):
        print("error: expected decimal real values in [0, 1]", file=sys.stderr)
        return 1
    try:
        result = bucket_sort([float(token) for token in tokens])
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(" ".join(format(value, ".17g") for value in result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
