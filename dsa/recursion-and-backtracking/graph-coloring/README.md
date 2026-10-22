# Graph Coloring

## 1. Algorithm Name

Graph Coloring

## 2. Overview

Find one proper vertex coloring of a small undirected graph using at most m colors through exact recursive trial and restoration.

## 3. Problem Statement

Input is a square, symmetric binary adjacency matrix and a native nonnegative integer m. Vertices are positions 0..n-1; color labels are 0..m-1. Return the lexicographically first valid label vector, assigning vertices and trying colors in ascending order, or None/nullopt/null if impossible. Empty graph returns [] even when m=0. A nonempty graph with m=0 is impossible. Self-loops are valid graph data but make proper coloring impossible. Disconnected components use the same palette. Inputs are read only.

## 4. Why Do We Need This Algorithm?

Some assignments conflict pairwise: endpoints of a conflict edge cannot share a resource label. Greedy assignment can fail with a fixed palette even when another earlier choice would work; backtracking revisits those choices.

## 5. Real-World Applications

- Model small conflict-free scheduling instances where adjacent tasks cannot share a time slot.
- Build exact reference answers for testing coloring heuristics.
- Explain resource-label assignment in interference graphs. Real register allocators require additional constraints and scale beyond this educational solver.

## 6. Core Intuition

At vertex v, only earlier vertices are assigned. Try a color that differs from each already-colored neighbor, then recurse. A future conflict is discovered when its later endpoint is assigned.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Validate m, square binary shape, and undirected symmetry. Reject malformed graphs before trivial answers.
2. If any diagonal entry is 1, return no coloring.
3. Assign vertices 0..n-1 and try color labels ascending. Use min(m,n) candidates: at most n colors can be needed for n vertices.
4. Skip colors matching an earlier neighbor. Append a valid color and recurse.
5. Copy the first complete assignment; pop the trial color before propagating success. Every assigned prefix is proper; each feasible assignment’s choices are explored in lexicographic order until the first success.

## 9. Pseudocode

```text
validate undirected matrix and m
if any self-loop: return null
visit(v):
  if v = n: answer = copy(path); return true
  for color = 0 .. min(m,n)-1:
    if every earlier neighbor has a different color:
      append color
      found = visit(v+1)
      pop
      if found: return true
  return false
visit(0); return answer or null
```

## 10. Dry Run

For a triangle with m=2: v0 takes 0; v1 cannot take 0, so takes 1; v2 conflicts with both colors. Pop v1 and v0, then try v0=1 and v1=0; v2 again fails. Return null. With m=3, the first branch reaches `[0,1,2]`. For one edge (0,1) plus isolated vertex 2 with m=2, output is `[0,1,0]`: an isolated vertex reuses the smallest label.

## 11. Time Complexity

Let n be vertices and c=min(m,n). Matrix validation costs Θ(n²+1). A safe worst-case upper bound is O(n² + n·c^n + 1), accounting for checking up to n earlier neighbors per trial; c=0 returns immediately after validation for nonempty graphs. For c=1, the linear-depth checks are covered by the n² term. Early solutions or loops reduce search. No distributional average is assumed.

## 12. Space Complexity

Auxiliary space is O(n) for the label path, one copied answer, and recursion stack, beyond the caller’s Θ(n²) matrix. Only one coloring is returned. CLI matrix/token storage and JSON text are additional.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `graph_coloring(adjacency, m) -> list[int] | None`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '3 3 0 1 1 1 0 1 1 1 0\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-graph-coloring
printf '3 3 0 1 1 1 0 1 1 1 0\n' | /tmp/atlas-graph-coloring
```

Both commands print:

```json
[0,1,2]
```

CLI grammar: `m n` followed by exactly n*n binary adjacency entries in row-major order.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/graph-coloring/tests
```

## 16. Edge Cases

Empty graph, zero palette, isolated/disconnected vertices, self-loops, triangles, and impossible palettes are covered. Duplicate binary entries represent separate vertex pairs, not repeated vertices. Asymmetric matrices are invalid; directed coloring is outside this API. Tests exhaust undirected simple graphs through four vertices and compare all candidate palettes with independent Cartesian-product coloring checks; additional tests cover malformed matrices, huge palettes, repeated calls, and input preservation.

## 17. Advantages

Produces an exact witness or proves palette infeasibility by exhausting choices. Fixed vertex/color ordering gives reproducible results. Restricting candidate labels to n handles oversized palettes safely.

## 18. Disadvantages and Limitations

Worst-case search is exponential, the dense input costs Θ(n²), and recursion can exhaust resources. This function does not minimize colors, enumerate all colorings, accept weighted/list constraints, or promise large-graph performance. Python supports arbitrary-size m; C++ m uses signed long long.

## 19. When to Use It

Use it for exact small fixed-palette feasibility and as a reference for heuristic implementations.

## 20. When Not to Use It

Avoid it for large scheduling instances, chromatic-number optimization without an outer policy, or directed/list/edge-coloring variants.

## 21. Comparison With Related Algorithms

| Approach | Guarantee | Tradeoff |
| --- | --- | --- |
| This backtracking | First proper coloring within m, or exhaustive failure | Exponential worst case |
| Greedy coloring | A coloring with its chosen palette | May exceed m despite feasible alternatives |
| [N-Queens](../n-queens/README.md) | Nonattacking board assignments | Specialized occupancy constraints |

## 22. Interview Questions

1. Why can only earlier neighbors be checked?
2. Why is a self-loop unsatisfiable for every m?
3. Why does min(m,n) preserve the first answer?
4. Why does a disconnected graph share one palette rather than adding component palettes?

## 23. Practice Problems

1. Trace a 3-cycle with two and three colors.
2. Construct a graph where greedy order affects the number of colors.
3. Design a separate minimum-color wrapper and account for repeated searches.

## 24. References

- [NIST, A graph coloring algorithm for large scheduling problems](https://nvlpubs.nist.gov/nistpubs/jres/84/jresv84n6p489_a1b.pdf), for scheduling context and a different coloring method.
- [NIST backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
