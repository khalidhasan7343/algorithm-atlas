# Dijkstra's Algorithm

## 1. Algorithm Name

Dijkstra's Algorithm

## 2. Overview

Compute single-source shortest paths with nonnegative integer weights using a lazy binary min-heap.

## 3. Problem Statement

Return distances, predecessor vertices and original predecessor edge IDs; unreachable vertices have null values.

**Contract:** `dijkstra(n, edges, source=None, directed=True)`. Directed or undirected weighted triples. All edges, even unreachable ones, must have weight in [0,10^12]. Source None is allowed only for V=0. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

Different edge costs invalidate BFS layers. A minimum tentative-distance choice identifies the next optimal weighted distance.

## 5. Real-World Applications

Road routing with nonnegative costs, network latency estimates and nonnegative state-space search.

## 6. Core Intuition

No nonnegative extension can improve a smaller already selected distance. Heap labels are tentative; obsolete labels must be skipped.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Understand adjacency lists, weighted paths, reachability and priority queues or relaxation as used below.

## 8. Step-by-Step Working Process

Initialize the source to zero. Pop (distance,vertex), ordered lexicographically; skip labels unequal to the current best. Scan input-order adjacency, update only strict improvements and push a fresh label. Equal distances keep the existing predecessor.

**Correctness:** For a nonstale popped vertex u, suppose a cheaper source path existed. Its first unselected vertex would already have a tentative distance no larger than that path cost, contradicting the heap minimum. Nonnegative weights justify this inequality. Strict updates avoid cyclic predecessor chains on zero-weight cycles.

## 9. Pseudocode

```text
best[source]=0; heap.push((0,source))
while heap:
    cost,u=pop_min()
    if cost != best[u]: continue
    for edge u→v of weight w:
        if cost+w < best[v]:
            best[v]=cost+w; parent[v]=edge; push(best[v],v)
```

## 10. Dry Run

Popping 0 offers labels 5 for 1 and 1 for 2. Popping 2 improves 1 to 2. The old (5,1) label is eventually skipped. Vertex 3 stays unreachable.

## 11. Time Complexity

O(V+E+(E+1) log(E+1)) for lazy heap entries, including input validation; parallel edges can produce O(E) heap labels, so log E is the direct bound.

## 12. Space Complexity

O(V+E) including adjacency, results and up to O(E) heap labels.

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `dijkstra(n, edges, source=None, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The core loop is local to this canonical module; shared support only validates and reconstructs paths.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. The typed result uses bounded long long distances, with distinct sentinels for unreachable and negative-cycle values. Sentinel values are never used in arithmetic.

## 15. Input and Output Examples

Python executable input:
```json
{"n":4,"edges":[[0,1,5],[0,2,1],[2,1,1]],"source":0,"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
4 3 1 0 0 1 5 0 2 1 2 1 1
```
Both output:
```json
{"distance":[0,2,1,null],"parent":[null,2,0,null],"parent_edge":[null,2,1,null]}
```
V≤1000, E≤10000 and weights≤10^12 imply a finite simple-path bound of 999*10^12. This fits signed 64-bit integers. Unreachable infinity is never added. path_to(result,target) returns vertices and original edge IDs, or empty arrays when unreachable.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Zero weights, equal-cost choices, unreachable regions and invalid signed bounds are explicit cases. Finite paths retain original edge IDs; affected or unreachable vertices have no predecessor.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7202 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Efficient sparse-graph shortest paths and deterministic predecessor reconstruction.

## 18. Disadvantages and Limitations

Negative edges are rejected, including those unreachable from the source. Lazy duplicates can occupy O(E) space.

## 19. When to Use It

Use for nonnegative weighted routes; it is the canonical Greedy graph implementation also referenced by A11.

## 20. When Not to Use It

Use Bellman-Ford for negative edges and BFS for unit weights.

## 21. Comparison With Related Algorithms

BFS agrees on unit weights. Bellman-Ford supports negative edges; A* uses a goal heuristic. Johnson reuses this canonical Dijkstra after reweighting.

[breadth-first-search](../breadth-first-search/README.md), [bellman-ford](../bellman-ford/README.md), [a-star-search](../a-star-search/README.md), [johnson](../johnson/README.md)

## 22. Interview Questions

Why is a stale entry safe to discard? Which inequality fails with a negative edge?

## 23. Practice Problems

Construct a stale-label example; verify predecessor edge weights sum to distance; compare with Bellman-Ford.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). For weighted-path theory see also [Princeton shortest paths](https://algs4.cs.princeton.edu/44sp/).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
