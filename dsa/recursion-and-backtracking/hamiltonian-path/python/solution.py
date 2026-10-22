"""hamiltonian-path: deterministic recursive backtracking."""

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


def hamiltonian_path(adjacency: Sequence[Sequence[int]], *,
                     directed: bool = False) -> list[int] | None:
    """First lexicographic all-vertex path, across all possible starts.

    No cycle-closing edge is required. Self-loops are ignored. Empty graph
    has the vacuous path []; disconnected nonempty graphs may have no path.
    """
    if type(directed) is not bool:
        raise TypeError("directed must be bool")
    _validate_graph(adjacency, directed)
    n = len(adjacency)
    path: list[int] = []
    used = [False] * n
    answer: list[int] | None = None

    def visit() -> bool:
        nonlocal answer
        if len(path) == n:
            answer = path.copy()
            return True
        for vertex in range(n):
            if not used[vertex] and (not path or adjacency[path[-1]][vertex]):
                used[vertex] = True
                path.append(vertex)
                found = visit()
                path.pop()
                used[vertex] = False
                if found:
                    return True
        return False

    visit()
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
        if mode not in (0, 1):
            raise ValueError("directed must be 0 or 1")
        result = hamiltonian_path(graph, directed=bool(mode))
        print(json.dumps(result, separators=(",", ":")))
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
