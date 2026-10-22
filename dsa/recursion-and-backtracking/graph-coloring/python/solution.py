"""graph-coloring: deterministic recursive backtracking."""

from collections.abc import Sequence
import json
import re
import sys


def _validate_graph(adjacency: Sequence[Sequence[int]], directed: bool) -> None:
    n = len(adjacency)
    if any(len(row) != n for row in adjacency):
        raise ValueError("adjacency matrix must be square")
    for row in adjacency:
        for value in row:
            if type(value) is not int:
                raise TypeError("edges must be native ints")
            if value not in (0, 1):
                raise ValueError("edges must be binary")
    if not directed:
        for row in range(n):
            for col in range(row):
                if adjacency[row][col] != adjacency[col][row]:
                    raise ValueError("undirected matrix must be symmetric")


def graph_coloring(adjacency: Sequence[Sequence[int]], m: int) -> list[int] | None:
    """First lexicographic proper coloring, labels 0..m-1; None if impossible.

    Undirected binary matrix required. Self-loops are valid but unsatisfiable.
    Disconnected components share the palette. Empty graph has coloring [].
    """
    if type(m) is not int:
        raise TypeError("m must be a native int")
    if m < 0:
        raise ValueError("m must be nonnegative")
    _validate_graph(adjacency, False)
    n = len(adjacency)
    if any(adjacency[i][i] for i in range(n)):
        return None
    path: list[int] = []
    answer: list[int] | None = None
    colors = min(m, n)

    def visit(vertex: int) -> bool:
        nonlocal answer
        if vertex == n:
            answer = path.copy()
            return True
        for color in range(colors):
            if all(not adjacency[vertex][other] or path[other] != color
                   for other in range(vertex)):
                path.append(color)
                found = visit(vertex + 1)
                path.pop()
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
        if len(numbers) < 2:
            raise ValueError("mode and size required")
        mode, n = numbers[:2]
        cells = numbers[2:]
        if n < 0 or n * n != len(cells):
            raise ValueError("square cell count mismatch")
        graph = [cells[i * n:(i + 1) * n] for i in range(n)]
        result = graph_coloring(graph, mode)
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
