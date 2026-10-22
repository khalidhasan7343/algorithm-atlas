"""combinations: deterministic recursive backtracking."""

from collections.abc import Sequence
import json
import re
import sys


def combinations(values: Sequence[int], k: int) -> list[list[int]]:
    """Enumerate k-element positional selections in increasing-index order.

    Equal values at different indices may produce equal rows. k=0 has one
    empty selection; k>n has none. Negative/non-native k is invalid.
    """
    if type(k) is not int:
        raise TypeError("k must be a native int")
    if k < 0:
        raise ValueError("k must be nonnegative")
    if any(type(value) is not int for value in values):
        raise TypeError("values must contain native ints")
    if k > len(values):
        return []
    result: list[list[int]] = []
    path: list[int] = []

    def visit(start: int) -> None:
        if len(path) == k:
            result.append(path.copy())
            return
        # Only choose indices leaving enough positions to finish the row.
        last = len(values) - (k - len(path))
        for index in range(start, last + 1):
            path.append(values[index])
            visit(index + 1)
            path.pop()

    visit(0)
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
        if not numbers:
            raise ValueError("k is required")
        result = combinations(numbers[1:], numbers[0])
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
