"""subset-sum-backtracking: deterministic recursive backtracking."""

from collections.abc import Sequence
import json
import re
import sys


def subset_sum_backtracking(values: Sequence[int], target: int) -> list[int] | None:
    """First include-before-exclude matching index subset; target=0 gives [].

    Check the current sum before branching. Values can be negative, zero, or
    repeated. No positive-only pruning; returned indices refer to positions.
    """
    if type(target) is not int or any(type(value) is not int for value in values):
        raise TypeError("target and values must be native ints")
    path: list[int] = []
    answer: list[int] | None = None

    def visit(index: int, total: int) -> bool:
        nonlocal answer
        if total == target:
            answer = path.copy()
            return True
        if index == len(values):
            return False
        path.append(index)
        found = visit(index + 1, total + values[index])
        path.pop()
        if found:
            return True
        return visit(index + 1, total)

    visit(0, 0)
    return answer


def main() -> int:
    """Read the documented signed-decimal CLI and print compact JSON."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
        print("error: expected signed decimal integer tokens", file=sys.stderr)
        return 1
    numbers = [int(token, 10) for token in tokens]
    try:
        if not numbers:
            raise ValueError("target required")
        result = subset_sum_backtracking(numbers[1:], numbers[0])
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
