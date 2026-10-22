"""Nonnegative 0/1 subset-sum existence using descending Boolean tabulation."""
import re
import sys


def subset_sum(values: list[int], target: int) -> bool:
    if type(target) is not int or not 0 <= target <= 10000:
        raise ValueError("target must be an integer in 0..10000")
    if len(values) > 1000 or len(values) * (target + 1) > 2000000:
        raise ValueError("DP work limit exceeded")
    if any(type(v) is not int or not 0 <= v <= 10**9 for v in values):
        raise ValueError("values must be integers in 0..10^9")
    reachable = [True] + [False] * target
    for value in values:
        for total in range(target, value - 1, -1):
            reachable[total] = reachable[total] or reachable[total - value]
    return reachable[target]


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if any(not re.fullmatch(r"[+-]?[0-9]+", x) for x in tokens):
            raise ValueError("expected ASCII decimal integers")
        numbers = [int(x) for x in tokens]
        if len(numbers) < 2 or not 0 <= numbers[1] <= 1000 or len(numbers) != numbers[1] + 2:
            raise ValueError("expected target, count, values")
        print("true" if subset_sum(numbers[2:], numbers[0]) else "false")
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
