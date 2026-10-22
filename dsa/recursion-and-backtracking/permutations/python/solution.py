"""permutations: deterministic recursive backtracking."""

from collections.abc import Sequence
import json
import re
import sys


def permutations(values: Sequence[int]) -> list[list[int]]:
    """Enumerate positional permutations in input-index DFS order.

    Equal values at distinct positions are distinct choices; repeated value
    rows are intentional. Empty input has one empty permutation. No mutation.
    """
    if any(type(value) is not int for value in values):
        raise TypeError("values must contain native ints")
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(values)

    def visit() -> None:
        if len(path) == len(values):
            result.append(path.copy())
            return
        for index in range(len(values)):
            if not used[index]:
                used[index] = True
                path.append(values[index])
                visit()
                path.pop()
                used[index] = False

    visit()
    return result


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
        result = permutations(numbers)
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
