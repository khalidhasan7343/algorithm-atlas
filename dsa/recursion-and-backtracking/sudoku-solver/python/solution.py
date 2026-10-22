"""sudoku-solver: deterministic recursive backtracking."""

from collections.abc import Sequence
import json
import re
import sys


def solve_sudoku(board: Sequence[Sequence[int]]) -> list[list[int]] | None:
    """First row-major/digit-ascending 9x9 completion, without input mutation.

    Zero means blank. Contradictory givens are invalid; consistent unsolvable
    boards return None. All search assignments are undone, including success.
    """
    if len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("board must be 9 by 9")
    work = [list(row) for row in board]
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    blanks: list[tuple[int, int]] = []
    for row in range(9):
        for col in range(9):
            value = work[row][col]
            if type(value) is not int:
                raise TypeError("cells must be native ints")
            if not 0 <= value <= 9:
                raise ValueError("cells must be in 0..9")
            if value == 0:
                blanks.append((row, col))
                continue
            box, bit = (row // 3) * 3 + col // 3, 1 << value
            if (rows[row] | cols[col] | boxes[box]) & bit:
                raise ValueError("contradictory givens")
            rows[row] |= bit
            cols[col] |= bit
            boxes[box] |= bit
    answer: list[list[int]] | None = None

    def visit(index: int) -> bool:
        nonlocal answer
        if index == len(blanks):
            answer = [row.copy() for row in work]
            return True
        row, col = blanks[index]
        box = (row // 3) * 3 + col // 3
        for value in range(1, 10):
            bit = 1 << value
            if not ((rows[row] | cols[col] | boxes[box]) & bit):
                work[row][col] = value
                rows[row] |= bit
                cols[col] |= bit
                boxes[box] |= bit
                found = visit(index + 1)
                work[row][col] = 0
                rows[row] &= ~bit
                cols[col] &= ~bit
                boxes[box] &= ~bit
                if found:
                    return True
        return False

    visit(0)
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
        if len(numbers) != 81:
            raise ValueError("exactly 81 cells required")
        result = solve_sudoku([numbers[i:i + 9] for i in range(0, 81, 9)])
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
