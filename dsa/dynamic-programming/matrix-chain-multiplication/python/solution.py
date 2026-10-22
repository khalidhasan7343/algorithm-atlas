"""Interval DP for optimal compatible-matrix-chain scalar cost."""
import re
import sys


def matrix_chain_cost(dimensions: list[int]) -> int:
    """dimensions=[d0,...,dn] describes matrices di x d(i+1); [] is empty."""
    if len(dimensions) == 1 or len(dimensions) > 101:
        raise ValueError("use [] or 2..101 dimensions")
    if any(type(d) is not int or not 1 <= d <= 100000 for d in dimensions):
        raise ValueError("dimensions must be integers in 1..100000")
    n = len(dimensions) - 1
    if n <= 1:
        return 0
    cost = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            cost[left][right] = min(
                cost[left][split] + cost[split+1][right]
                + dimensions[left] * dimensions[split+1] * dimensions[right+1]
                for split in range(left, right)
            )
    return cost[0][n-1]


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if any(not re.fullmatch(r"[+-]?[0-9]+", x) for x in tokens):
            raise ValueError("expected ASCII decimal integers")
        numbers = [int(x) for x in tokens]
        if not numbers or not 0 <= numbers[0] <= 101 or len(numbers) != numbers[0] + 1:
            raise ValueError("expected dimension count followed by dimensions")
        print(matrix_chain_cost(numbers[1:]))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
