# Rat in a Maze

## 1. Algorithm Name

Rat in a Maze

## 2. Overview

Enumerate all simple paths through a rectangular binary maze from its top-left cell to its bottom-right cell. Movement is orthogonal in four directions.

## 3. Problem Statement

Input is a rectangular sequence of binary integer rows: 1 is open and 0 blocked. Empty outer input returns []. Nonempty rows must have positive equal width. Return every path string, using D,L,R,U moves in that DFS order, without revisiting a cell. A 1×1 open maze returns `[""]` for the zero-move path; blocked endpoints or an unreachable destination return []. The maze is never modified.

## 4. Why Do We Need This Algorithm?

A route may need to move left or up to bypass obstacles. Simple-path enumeration must distinguish permanent obstacles from cells occupied only by the current path.

## 5. Real-World Applications

- Enumerate small puzzle routes to study alternatives.
- Build route fixtures that cover cycles and detours in grid interfaces.
- Explain temporary visited state; this exhaustive enumerator does not compute shortest paths or solve large navigation systems efficiently.

## 6. Core Intuition

Mark a cell only while it belongs to the current path. After exploring its suffixes, unmark it so a different route can use it. Never continue beyond the destination.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Validate rectangular shape, native integer cells, and binary values before testing blocked endpoints.
2. Mark (0,0) and recurse.
3. At the destination, copy the current move string.
4. Otherwise consider down, left, right, up in that order. Check bounds before indexing and skip blocked or currently visited cells.
5. Append the move, recurse, pop it. Unmark the current cell before returning. The visited set exactly equals the current route, so every emitted route is simple; trying every legal next move covers all such routes.

## 9. Pseudocode

```text
walk(r,c):
  visited[r][c] = true
  if (r,c) = destination: output copy(path)
  else:
    for direction in [D,L,R,U]:
      next = bounded neighbor in direction
      if next exists and open and not visited:
        append direction; walk(next); pop
  visited[r][c] = false
if endpoints open: walk(0,0)
return output
```

## 10. Dry Run

For the all-open 2×2 maze, mark (0,0), try D → (1,0), then R → destination; emit `DR`, unmark destination and (1,0). The next start branch R → (0,1), then D → destination emits `RD`. Returning to (0,0) inside either branch is forbidden by its temporary mark. Final output is `["DR","RD"]`; after traversal every visited flag is clear.

## 11. Time Complexity

Let V=rows·columns and P be the number of returned paths. Validation is Θ(V). A safe loose bound is O(4^V + V·P + V): recursion depth is at most V and each node considers at most four neighbors, while each path copy costs up to V-1 moves. This is exponential enumeration, not the O(V+E) bound for a one-pass reachability traversal. Blocked endpoints return after validation. No average-case distribution is assumed.

## 12. Space Complexity

Auxiliary storage is O(V): a visited grid, path of at most V-1 moves, and recursion stack of depth at most V. Output is O((V+1)·P), including string headers and the empty singleton path. Caller cells are read only; CLI buffers are additional.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `rat_in_a_maze(grid) -> list[str]`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '2 2 1 1 1 1\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-rat-in-a-maze
printf '2 2 1 1 1 1\n' | /tmp/atlas-rat-in-a-maze
```

Both commands print:

```json
["DR","RD"]
```

CLI grammar: `rows columns` followed by exactly rows*columns binary cells in row-major order. Only `0 0` represents an empty grid.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/rat-in-a-maze/tests
```

## 16. Edge Cases

Empty input, blocked start/end, no route, nonsquare grids, and cycles are covered. Invalid shape/cell values are errors even if an endpoint is blocked. Duplicate cell values are normal occupancy data, not duplicate entities; each coordinate is distinct. Tests exhaust binary 2×2, 2×3, 3×2 and narrow mazes, compare independent move-string enumeration, and include the open 3×3 grid, which exercises L/U detours. C++ CLI dimension validation uses division/remainder before allocation, avoiding overflow in rows*columns.

## 17. Advantages

Captures every simple route, handles detours in all four directions, and makes path-specific visited restoration visible.

## 18. Disadvantages and Limitations

The number of simple paths can grow exponentially. All strings are retained, recursion can exhaust stack resources, and there is no maximum-length or shortest-route mode. The empty-grid convention has no origin/destination; it deliberately yields no path.

## 19. When to Use It

Use it for small exhaustive maze puzzles and route enumeration demonstrations.

## 20. When Not to Use It

Avoid it for shortest routes, weighted costs, or large grids where reachability or one witness suffices.

## 21. Comparison With Related Algorithms

| Task | Appropriate traversal |
| --- | --- |
| All simple maze paths | This path-local backtracking |
| One reachable route | DFS with a permanent visited set |
| Fewest unweighted moves | Breadth-first search |
| [Hamiltonian Path](../hamiltonian-path/README.md) | Must visit every vertex exactly once |

## 22. Interview Questions

1. Why must a visited cell be unmarked on return?
2. Why stop at the destination instead of exploring its neighbors?
3. Why are D/R-only paths a different contract?
4. What causes exponential behavior despite only V cells?

## 23. Practice Problems

1. Trace every path in an open 2×3 grid.
2. Construct a maze whose route needs an upward move.
3. Design a separate length-limited enumerator and explain its completeness condition.

## 24. References

- [NIST backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).
- [NIST simple path](https://xlinux.nist.gov/dads/HTML/simplepath.html), the no-repeated-vertex concept represented here by cells.

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
