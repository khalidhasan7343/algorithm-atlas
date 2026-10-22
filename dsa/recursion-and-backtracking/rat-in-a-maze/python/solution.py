"""rat-in-a-maze: deterministic recursive backtracking."""

from collections.abc import Sequence
import json
import re
import sys


def rat_in_a_maze(grid: Sequence[Sequence[int]]) -> list[str]:
    """All simple top-left/bottom-right paths, in D,L,R,U DFS order."""
    if not grid:
        return []
    height, width = len(grid), len(grid[0])
    if width == 0 or any(len(row) != width for row in grid):
        raise ValueError("grid must be rectangular with nonempty rows")
    for row in grid:
        for value in row:
            if type(value) is not int:
                raise TypeError("cells must be native ints")
            if value not in (0, 1):
                raise ValueError("cells must be 0 or 1")
    result: list[str] = []
    if not grid[0][0] or not grid[-1][-1]:
        return result
    visited = [[False] * width for _ in range(height)]
    path: list[str] = []

    def visit(row: int, col: int) -> None:
        visited[row][col] = True
        if row == height - 1 and col == width - 1:
            result.append("".join(path))
        else:
            for step, dr, dc in (("D", 1, 0), ("L", 0, -1),
                                 ("R", 0, 1), ("U", -1, 0)):
                nr, nc = row + dr, col + dc
                if (0 <= nr < height and 0 <= nc < width
                        and grid[nr][nc] and not visited[nr][nc]):
                    path.append(step)
                    visit(nr, nc)
                    path.pop()
        visited[row][col] = False

    visit(0, 0)
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
        if len(numbers) < 2:
            raise ValueError("rows and columns required")
        height, width = numbers[:2]
        cells = numbers[2:]
        if height < 0 or width < 0 or (height == 0) != (width == 0):
            raise ValueError("invalid dimensions")
        if height * width != len(cells):
            raise ValueError("cell count does not match dimensions")
        grid = [cells[i * width:(i + 1) * width] for i in range(height)]
        result = rat_in_a_maze(grid)
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
