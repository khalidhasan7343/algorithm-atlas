"""n-queens: deterministic recursive backtracking."""

from collections.abc import Sequence
import json
import re
import sys


def n_queens(n: int) -> list[list[int]]:
    """All row-to-column placements in lexicographic order; n=0 yields [[]]."""
    if type(n) is not int:
        raise TypeError("n must be a native int")
    if n < 0:
        raise ValueError("n must be nonnegative")
    result: list[list[int]] = []
    path: list[int] = []
    columns = [False] * n
    diagonal = [False] * max(0, 2 * n - 1)
    anti = [False] * max(0, 2 * n - 1)

    def visit(row: int) -> None:
        if row == n:
            result.append(path.copy())
            return
        for col in range(n):
            d, a = row + col, row + (n - 1 - col)
            if not (columns[col] or diagonal[d] or anti[a]):
                columns[col] = diagonal[d] = anti[a] = True
                path.append(col)
                visit(row + 1)
                path.pop()
                columns[col] = diagonal[d] = anti[a] = False

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
        if len(numbers) != 1:
            raise ValueError("exactly one n required")
        result = n_queens(numbers[0])
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
