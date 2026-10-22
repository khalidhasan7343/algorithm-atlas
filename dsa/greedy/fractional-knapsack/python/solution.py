"""Fractional knapsack with exact rational decisions, value and fractions."""
from collections.abc import Sequence
from fractions import Fraction
from functools import cmp_to_key
import json
import re
import sys


def fractional_knapsack(weights: Sequence[int], values: Sequence[int], capacity: int) -> tuple[Fraction, list[Fraction]]:
    if type(capacity) is not int or not 0 <= capacity <= 10**9:
        raise ValueError("capacity must be an integer in 0..10^9")
    if len(weights) != len(values) or len(weights) > 10000:
        raise ValueError("equal weight/value lengths of at most 10000 required")
    if any(type(w) is not int or not 1 <= w <= 10**6 for w in weights):
        raise ValueError("weights must be integers in 1..10^6")
    if any(type(v) is not int or not 0 <= v <= 10**6 for v in values):
        raise ValueError("values must be integers in 0..10^6")

    def compare(left: int, right: int) -> int:
        difference = values[left]*weights[right] - values[right]*weights[left]
        return (-1 if difference > 0 else 1) if difference else left - right

    ordered = sorted(range(len(weights)), key=cmp_to_key(compare))
    fractions = [Fraction(0)] * len(weights)
    remaining = capacity
    total = Fraction(0)
    for index in ordered:
        if remaining == 0 or values[index] == 0:
            break
        taken_weight = min(weights[index], remaining)
        fractions[index] = Fraction(taken_weight, weights[index])
        total += values[index] * fractions[index]
        remaining -= taken_weight
    return total, fractions


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if any(not re.fullmatch(r"[+-]?[0-9]+", x) for x in tokens):
            raise ValueError("expected ASCII decimal integers")
        numbers = [int(x) for x in tokens]
        if len(numbers) < 2 or not 0 <= numbers[1] <= 10000 or len(numbers) != 2 + 2*numbers[1]:
            raise ValueError("expected capacity, count and weight/value pairs")
        total, fractions = fractional_knapsack(numbers[2::2], numbers[3::2], numbers[0])
        ratio = lambda value: [value.numerator, value.denominator]
        print(json.dumps({"value": ratio(total), "fractions": [ratio(f) for f in fractions]}, separators=(",", ":")))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
