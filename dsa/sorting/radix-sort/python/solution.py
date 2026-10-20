"""Stable base-256 LSD radix sort for signed, arbitrary-size Python ints."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys

RADIX = 256


def radix_sort(values: Sequence[int]) -> list[int]:
    """Return a sorted copy of native ints, preserving the original sequence.

    Booleans and int subclasses are rejected. Subtracting the minimum creates
    nonnegative ordering keys without restricting the signed integer range.
    Each counting pass is stable, including the movement of original objects.
    """
    result = list(values)
    if any(type(value) is not int for value in result):
        raise TypeError("radix_sort requires native Python ints; bool is not accepted")
    if len(result) < 2:
        return result

    minimum = min(result)
    keys = [value - minimum for value in result]
    passes = max(1, (max(keys).bit_length() + 7) // 8)
    buffer = result.copy()
    key_buffer = keys.copy()

    for digit_index in range(passes):
        shift = 8 * digit_index
        counts = [0] * RADIX
        for key in keys:
            counts[(key >> shift) & 255] += 1

        # Convert frequencies into the first free position for each digit.
        position = 0
        for digit in range(RADIX):
            frequency = counts[digit]
            counts[digit] = position
            position += frequency

        # Forward traversal and advancing offsets preserve equal-key order.
        for index, key in enumerate(keys):
            digit = (key >> shift) & 255
            destination = counts[digit]
            buffer[destination] = result[index]
            key_buffer[destination] = key
            counts[digit] += 1
        result, buffer = buffer, result
        keys, key_buffer = key_buffer, keys
    return result


def main() -> int:
    """Sort ASCII signed-decimal stdin tokens; reject malformed input."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
        print(
            "error: expected whitespace-separated signed decimal integers",
            file=sys.stderr,
        )
        return 1
    print(" ".join(map(str, radix_sort([int(token, 10) for token in tokens]))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
