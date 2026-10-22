# Bellman-Ford

## 1. Algorithm Name

Bellman-Ford

## 2. Overview

Relax every arc repeatedly, then propagate the influence of source-reachable negative cycles.

## 3. Problem Statement

Return finite single-source distances, null for unreachable vertices, and "-inf" for vertices whose path cost is unbounded below.

**Contract:** `bellman_ford(n, edges, source=None, directed=True)`. Directed or undirected weighted triples in [-10^6,10^6]. A negative undirected edge permits a negative closed walk and affects its reachable component. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

Negative costs invalidate Dijkstra’s greedy selection. Cycle influence must be distinguished from ordinary unreachable paths.

## 5. Real-World Applications

Difference constraints, arbitrage-cycle analysis after a suitable cost transform, and Johnson vertex potentials.

## 6. Core Intuition

After k full passes, every optimum using at most k edges has been considered. A finite optimum needs at most V-1 edges; further improvement exposes a reachable negative cycle.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Understand adjacency lists, weighted paths, reachability and priority queues or relaxation as used below.

## 8. Step-by-Step Working Process

Initialize the source. For at most V-1 passes, scan vertices ascending and their input-order outgoing arcs, applying strict in-place relaxations; stop if unchanged. Seed targets of remaining relaxable reachable arcs. Traverse successors from those seeds and mark every reached vertex "-inf", clearing their parents.

**Correctness:** The DP recurrence is D_k(v)=min(D_(k-1)(v), min_(u→v)(D_(k-1)(u)+w)). In-place relaxation can discover longer paths earlier but never loses the paths guaranteed after each pass. Without a reachable negative cycle, a shortest simple path uses at most V-1 edges. Any remaining relaxable arc therefore lies downstream of such a cycle; successor closure labels exactly its unbounded destinations.

## 9. Pseudocode

```text
best[source]=0
repeat V-1 times:
    relax every reachable arc; stop if unchanged
seeds=targets of still-relaxable reachable arcs
for v reachable from seeds:
    best[v]="-inf"; parent[v]=absent
```

## 10. Dry Run

The 1→2→1 cycle costs -2. It is reachable from 0 and can reach 3, so 1,2,3 are affected. Vertex 0 remains finite; isolated 4 is unreachable.

## 11. Time Complexity

O(VE+V) worst case, including adjacency and successor propagation. Undirected input expands to 2E arcs.

## 12. Space Complexity

O(V+E), with O(V) distances, predecessor arrays, cycle flags and propagation queue.

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `bellman_ford(n, edges, source=None, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The additional potentials(n,edges) helper initializes every label to zero, representing a virtual super-source for canonical Johnson reuse; it uses the same relaxation core. The core loop is local to this canonical module; shared support only validates and reconstructs paths.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. The typed result uses bounded long long distances, with distinct sentinels for unreachable and negative-cycle values. Sentinel values are never used in arithmetic.

## 15. Input and Output Examples

Python executable input:
```json
{"n":5,"edges":[[0,1,2],[1,2,-3],[2,1,1],[2,3,2]],"source":0,"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
5 4 1 0 0 1 2 1 2 -3 2 1 1 2 3 2
```
Both output:
```json
{"distance":[0,"-inf","-inf","-inf",null],"parent":[null,null,null,null,null],"parent_edge":[null,null,null,null,null]}
```
V≤1000, E≤10000 and |w|≤10^6 bound in-place intermediate magnitudes by V*2E*10^6. No unreachable sentinel is added. path_to returns an empty path for null or "-inf" destinations.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Zero weights, equal-cost choices, unreachable regions and invalid signed bounds are explicit cases. Finite paths retain original edge IDs; affected or unreachable vertices have no predecessor.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7202 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Handles signed weights and explains exactly which destinations lack finite shortest paths.

## 18. Disadvantages and Limitations

O(VE) work can be expensive. The API reports influence but does not return a negative-cycle witness.

## 19. When to Use It

Use for signed single-source paths and negative-cycle influence; A12 references its dynamic-programming interpretation.

## 20. When Not to Use It

Use Dijkstra for large nonnegative instances and Floyd/Johnson when all source pairs are required.

## 21. Comparison With Related Algorithms

Floyd-Warshall reports cycle effects per pair. Johnson connects a super-source to detect a cycle anywhere and reuses this canonical implementation.

[dijkstra](../dijkstra/README.md), [floyd-warshall](../floyd-warshall/README.md), [johnson](../johnson/README.md)

## 22. Interview Questions

Why do unreachable negative cycles stay unmarked? Why is a successor traversal needed after detecting a relaxable edge?

## 23. Practice Problems

Build a graph with a disconnected negative cycle; compare every unaffected source row with Floyd-Warshall.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). For weighted-path theory see also [Princeton shortest paths](https://algs4.cs.princeton.edu/44sp/).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
