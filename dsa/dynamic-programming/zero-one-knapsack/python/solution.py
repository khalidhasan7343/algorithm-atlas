"""0/1 knapsack: maximum value only, descending capacity updates."""
import sys
import re


def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    if type(capacity) is not int or not 0 <= capacity <= 10000:
        raise ValueError("capacity must be an integer in 0..10000")
    if len(weights) != len(values) or len(weights) > 1000:
        raise ValueError("equal lengths of at most 1000 required")
    if len(weights) * (capacity + 1) > 2000000:
        raise ValueError("DP work limit exceeded")
    if any(type(w) is not int or not 0 <= w <= 10**9 for w in weights):
        raise ValueError("weights must be integers in 0..10^9")
    if any(type(v) is not int or not -10**9 <= v <= 10**9 for v in values):
        raise ValueError("values must be integers in +/-10^9")
    best = [0] * (capacity + 1)
    for weight, value in zip(weights, values):
        for room in range(capacity, weight - 1, -1):
            best[room] = max(best[room], best[room - weight] + value)
    return best[capacity]


def _parse(token: str) -> int:
    if not re.fullmatch(r"[+-]?[0-9]+", token):
        raise ValueError("expected ASCII decimal integer")
    return int(token)


if __name__ == "__main__":
    try:
        tokens = [_parse(x) for x in sys.stdin.read().split()]
        if len(tokens) < 2:
            raise ValueError("expected capacity, item count, weight/value pairs")
        capacity, count = tokens[:2]
        if not 0 <= count <= 1000 or len(tokens) != 2 + 2 * count:
            raise ValueError("invalid item count")
        print(knapsack(tokens[2::2], tokens[3::2], capacity))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
