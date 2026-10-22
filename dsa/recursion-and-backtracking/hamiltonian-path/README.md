# Hamiltonian Path

## 1. Algorithm Name

Hamiltonian Path

## 2. Overview

Find a path that visits each vertex exactly once, using recursive extension and a temporary used-vertex array. Both directed and undirected binary graphs are supported.

## 3. Problem Statement

Input is a square binary adjacency matrix plus a directed flag (Python bool, C++ bool; CLI 0 or 1). Undirected matrices must be symmetric. Return the lexicographically first vertex-index path over all possible starts, or None/nullopt/null when no path exists. Empty graph returns [] by convention; one vertex returns [0] without requiring an edge. A closing edge back to the start is not required. Self-loops are ignored because a used vertex cannot be selected again. Caller data is unchanged.

## 4. Why Do We Need This Algorithm?

Visiting each vertex once is a stronger requirement than reaching a destination. A locally legal next edge can leave remaining vertices inaccessible, so the solver must retract choices and sometimes choose another starting vertex.

## 5. Real-World Applications

- Explore small visit-once route feasibility instances.
- Generate exact witnesses for testing route heuristics.
- Model short sequences where allowed transitions form a directed graph. Weighted optimization and travel cost minimization are outside this feasibility API.

## 6. Core Intuition

A partial path is a distinct-vertex sequence whose consecutive vertices are connected in the required direction. Try the next unused vertex in ascending order; when the path is empty, every vertex is a possible start.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Validate the directed flag and square binary matrix; require symmetry for undirected input.
2. Start with no path and all vertices unused.
3. If path length equals n, copy the answer.
4. Scan candidate vertices ascending. A candidate must be unused and, for a nonempty path, adjacent from the current final vertex.
5. Mark, append, recurse; then pop and unmark even on success.
6. If no extension succeeds, return failure to the caller. Enumerating all starts avoids the invalid assumption that vertex 0 must begin a directed path. Prefix ordering gives the first lexicographic witness.

## 9. Pseudocode

```text
visit():
  if length(path) = n: answer = copy(path); return true
  for vertex = 0 .. n-1:
    if unused[vertex] and (path empty or edge[last][vertex]):
      mark vertex; append vertex
      found = visit()
      pop; unmark vertex
      if found: return true
  return false
visit(); return answer or null
```

## 10. Dry Run

For directed edges 2→1 and 1→0, try start 0: no outgoing extension, so undo. Start 1 reaches 0 but leaves 2 unvisited, so undo both. Start 2 reaches 1 then 0; path length is 3, so copy `[2,1,0]`. Undo 0,1,2 while propagating success. Reversing that answer is not valid in this directed graph. In an undirected 0—1—2 chain, the first path is `[0,1,2]`.

## 11. Time Complexity

Let n be vertices. Validation costs Θ(n²+1). A safe worst-case upper bound is O(n·n! + n² + 1), because the solver explores prefixes of vertex permutations and scans n candidates at internal nodes. Successful early branches can be much faster; for dense graphs a first path is found after O(n²) candidate work. No probabilistic average is claimed. Empty/singleton cases take constant API time apart from their tiny validation.

## 12. Space Complexity

Auxiliary storage is O(n) for used flags, working path, recursion frames, and one copied answer, beyond the Θ(n²) input matrix. There is no retained list of all paths. CLI buffers add matrix/token and output-text storage.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `hamiltonian_path(adjacency, *, directed=False) -> list[int] | None`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '1 3 0 0 0 1 0 0 0 1 0\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-hamiltonian-path
printf '1 3 0 0 0 1 0 0 0 1 0\n' | /tmp/atlas-hamiltonian-path
```

Both commands print:

```json
[2,1,0]
```

CLI grammar: `directed n` followed by exactly n*n binary adjacency entries; directed is 0 or 1.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/hamiltonian-path/tests
```

## 16. Edge Cases

Empty and singleton graphs, disconnected vertices, directed sinks, self-loops, multiple possible starts, and graphs with multiple paths are tested. Undirected asymmetric input is invalid; directed asymmetric input is normal. Tests exhaust all undirected simple graphs through four vertices and all directed loop-free graphs through three, add seeded larger cases, and compare the exact first answer with independent permutation filtering. Invalid cells, repeated calls, and caller immutability are checked in both languages.

## 17. Advantages

Simple invariant, exact feasibility result, and deterministic first witness. Directed edge orientation and changing start vertices are explicit.

## 18. Disadvantages and Limitations

Factorial search limits practical size; large impossible instances can take especially long. Recursion can overflow the runtime stack. No deadline, cycle requirement, all-path enumeration, shortest-weight objective, or multigraph representation is provided.

## 19. When to Use It

Use it for small exact visit-once path feasibility and understanding permutation pruning.

## 20. When Not to Use It

Avoid it for ordinary reachability, shortest paths, very large graphs, or Hamiltonian-cycle requirements without an explicit closing-edge extension.

## 21. Comparison With Related Algorithms

| Problem | Requirement |
| --- | --- |
| Hamiltonian path | Every vertex once; no required closing edge |
| Hamiltonian cycle | Every vertex once plus closing edge |
| Euler trail | Every edge once; vertices may repeat |
| [Rat in a Maze](../rat-in-a-maze/README.md) | Simple origin-to-destination route; can omit open cells |

## 22. Interview Questions

1. Why must all starts be tried in a directed graph?
2. Why do self-loops not help?
3. How does a cycle requirement change the base case?
4. Why does permanent global visited state invalidate this exhaustive search?

## 23. Practice Problems

1. Trace the directed reverse chain in the example.
2. Build a connected graph with no Hamiltonian path.
3. Design a separate cycle variant and specify rotation/reversal duplicate semantics.

## 24. References

- [NIST Hamiltonian path definition](https://xlinux.nist.gov/dads/HTML/hamiltonianPath.html).
- [NIST backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
