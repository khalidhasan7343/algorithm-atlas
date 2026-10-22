"""power-set-generation: deterministic recursive backtracking."""

from collections.abc import Sequence
import json
import re
import sys


def power_set_generation(values: Sequence[int]) -> list[list[int]]:
    """Enumerate positional subsets, exclude before include at each index.

    Within each row, values retain input order. Equal values can produce
    repeated rows. Empty input yields [[]]. The caller's values are untouched.
    """
    if any(type(value) is not int for value in values):
        raise TypeError("values must contain native ints")
    result: list[list[int]] = []
    path: list[int] = []

    def visit(index: int) -> None:
        if index == len(values):
            result.append(path.copy())
            return
        visit(index + 1)
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
        result = power_set_generation(numbers)
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
