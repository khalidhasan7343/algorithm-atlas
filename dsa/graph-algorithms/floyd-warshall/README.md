# Floyd-Warshall

## 1. Algorithm Name

Floyd-Warshall

## 2. Overview

Compute all-pairs shortest paths using the dynamic-programming intermediate-vertex recurrence.

## 3. Problem Statement

Return a distance matrix with zero-length diagonal paths, null unreachable pairs and "-inf" pairs connected through any negative cycle.

**Contract:** `floyd_warshall(n, edges, directed=True)`. Directed or undirected weighted triples in [-10^6,10^6]; V≤100, E≤10000. The result is a matrix, without predecessor reconstruction. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

A complete route table needs more than one source’s predecessor tree. Intermediate-vertex DP also exposes negative-cycle reachability.

## 5. Real-World Applications

Dense small-network route tables, signed dependency costs and all-pairs reachability analysis.

## 6. Core Intuition

Allow intermediate vertices in prefix order. A shortest path either avoids the new vertex k or splits into an i→k and k→j path.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Understand adjacency lists, weighted paths, reachability and priority queues or relaxation as used below.

## 8. Step-by-Step Working Process

Initialize diagonal zero, unreachable pairs absent, and take minimum parallel-arc weights. For each k, relax all pairs with both subpaths present. Clamp internal negative candidates at -10^12. Find negative diagonal vertices, snapshot pair influence and tag all pairs reaching through one.

**Correctness:** For graphs without negative cycles, D_k(i,j)=min(D_(k-1)(i,j),D_(k-1)(i,k)+D_(k-1)(k,j)); induction on permitted intermediates proves all finite distances. Negative cycles appear as negative diagonal entries. A pair has unbounded cost exactly when it can enter and leave such a cycle. Every unaffected finite optimum has magnitude at most 99*10^6, so the lower clamp cannot change it; affected pairs are tagged after numeric DP.

## 9. Pseudocode

```text
D[i][i]=0; D[u][v]=min(input weights)
for k in 0..V-1:
    for i,j with D[i][k],D[k][j] present:
        D[i][j]=min(D[i][j], max(-10^12,D[i][k]+D[k][j]))
negative={k | D[k][k]<0}
mark (i,j) "-inf" if some negative k has i→k and k→j
```

## 10. Dry Run

The direct 0→2 entry is absent initially. Allowing intermediate 1 changes it to 2+(-1)=1. Reverse paths remain unreachable and every diagonal stays zero.

## 11. Time Complexity

O(V³), including the bounded negative-cycle influence classification.

## 12. Space Complexity

O(V²) including the matrix and influence/result snapshot; adjacency/input validation adds O(V+E).

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `floyd_warshall(n, edges, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The core loop is local to this canonical module; shared support only validates and reconstructs paths.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. The typed result uses bounded long long distances, with distinct sentinels for unreachable and negative-cycle values. Sentinel values are never used in arithmetic.

## 15. Input and Output Examples

Python executable input:
```json
{"n":3,"edges":[[0,1,2],[1,2,-1]],"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
3 2 1 0 1 2 1 2 -1
```
Both output:
```json
[[0,2,1],[null,0,-1],[null,null,0]]
```
The internal clamp -10^12 prevents exponential magnitude growth in negative-cycle cases. Adding two bounded entries stays safely within signed 64-bit limits. Reachability is tested before addition. Negative self-loops override diagonal zero and generate affected pairs.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Zero weights, equal-cost choices, unreachable regions and invalid signed bounds are explicit cases. Finite paths retain original edge IDs; affected or unreachable vertices have no predecessor.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7202 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Compact all-pairs DP with direct signed-edge and negative-cycle semantics.

## 18. Disadvantages and Limitations

Cubic work and quadratic memory; this educational API caps V at 100 and does not reconstruct paths.

## 19. When to Use It

Use for small dense all-pairs problems; A12 references the same canonical DP recurrence.

## 20. When Not to Use It

Use Johnson for sparse signed graphs without negative cycles or a single-source algorithm for one query source.

## 21. Comparison With Related Algorithms

Bellman-Ford gives one row and source-local cycle effects. Johnson rejects any negative cycle instead of returning a partially finite matrix.

[bellman-ford](../bellman-ford/README.md), [johnson](../johnson/README.md), [dijkstra](../dijkstra/README.md)

## 22. Interview Questions

Why must k be the outer loop? Why is setting every pair to "-inf" after finding one negative cycle incorrect?

## 23. Practice Problems

Add a disconnected negative cycle and identify only affected pairs; compare cycle-free results with Johnson.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). For weighted-path theory see also [Princeton shortest paths](https://algs4.cs.princeton.edu/44sp/).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
