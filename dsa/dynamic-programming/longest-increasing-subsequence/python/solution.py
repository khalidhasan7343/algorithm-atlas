"""Quadratic DP for the length of a strictly increasing subsequence."""
import re
import sys


def lis_length(values: list[int]) -> int:
    if len(values) > 1000:
        raise ValueError("at most 1000 values required")
    if any(type(v) is not int or not -10**9 <= v <= 10**9 for v in values):
        raise ValueError("values must be integers in +/-10^9")
    best = [1] * len(values)
    for end in range(len(values)):
        for previous in range(end):
            if values[previous] < values[end]:
                best[end] = max(best[end], best[previous] + 1)
    return max(best, default=0)


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if any(not re.fullmatch(r"[+-]?[0-9]+", x) for x in tokens):
            raise ValueError("expected ASCII decimal integers")
        numbers = [int(x) for x in tokens]
        if not numbers or not 0 <= numbers[0] <= 1000 or len(numbers) != numbers[0] + 1:
            raise ValueError("expected count followed by values")
        print(lis_length(numbers[1:]))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
