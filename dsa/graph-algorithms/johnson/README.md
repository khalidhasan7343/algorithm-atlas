# Johnson's Algorithm

## 1. Algorithm Name

Johnson's Algorithm

## 2. Overview

Compute directed all-pairs shortest paths by Bellman-Ford potentials, nonnegative reweighting and repeated canonical Dijkstra runs.

## 3. Problem Statement

Return a full matrix with null unreachable pairs, or null for the entire result if any negative cycle exists anywhere in the graph.

**Contract:** `johnson(n, edges, directed=True)`. Directed weighted triples only, V≤100 and E≤10000, weights in [-10^6,10^6]. Undirected mode is rejected; empty input returns []. Any negative cycle causes whole-result null, unlike Floyd’s per-pair tagging. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

Sparse graphs with negative edges cannot run Dijkstra directly. A potential transform removes negative weights without changing relative costs of routes with fixed endpoints.

## 5. Real-World Applications

Sparse signed route tables, difference-constraint networks and repeated path queries.

## 6. Core Intuition

Add a virtual super-source with zero arcs to all vertices. Its shortest distances h satisfy h(v)≤h(u)+w(u,v), so w′=w+h(u)-h(v)≥0. Path reweighting telescopes to one endpoint correction.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Understand adjacency lists, weighted paths, reachability and priority queues or relaxation as used below.

## 8. Step-by-Step Working Process

Validate directed signed edges. Call canonical Bellman-Ford potentials with all original vertex labels initialized to zero, exactly representing the virtual super-source’s first relaxations. Reject any detected negative cycle. Build reweighted edges, run canonical Dijkstra from each original source, and convert finite labels back with d=d′-h(source)+h(target).

**Correctness:** The virtual super-source reaches every vertex, so Bellman-Ford detects even disconnected negative cycles. Without one, its edge inequalities prove every reweighted arc nonnegative. Summing potentials along a path cancels internal terms: cost′(path)=cost(path)+h(source)-h(target). Thus minimizing reweighted cost minimizes original cost for fixed endpoints; Dijkstra is valid and the final correction recovers the original optimum. Unreachable pairs stay unreachable.

## 9. Pseudocode

```text
h=BellmanFord(virtual zero-cost super-source)
if any negative cycle: return null
wprime(u,v)=w(u,v)+h[u]-h[v]
for source in original vertices:
    row=Dijkstra(reweighted_graph,source)
    for reachable v: answer[source][v]=row[v]-h[source]+h[v]
```

## 10. Dry Run

Virtual-source potentials are [0,-2,0]. Reweighted edges have costs 0,1,4. Dijkstra from 0 finds transformed distances [0,0,1]; endpoint correction yields [0,-2,1].

## 11. Time Complexity

O(VE + V*(V+E+(E+1) log(E+1))) for the actual lazy binary-heap Dijkstra, including O(V²) result initialization. The direct multigraph heap bound is log E rather than silently assuming a simple graph.

## 12. Space Complexity

O(V²+V+E) including all-pairs output, reweighted graph, Bellman-Ford arrays and one Dijkstra heap at a time.

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `johnson(n, edges, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The canonical import helper loads Bellman-Ford potentials and Dijkstra; this module implements the reweighting and endpoint-correction procedure directly.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. The canonical Bellman-Ford and Dijkstra sources are included with executable mains disabled. No relaxation or priority-queue shortest-path implementation is duplicated here.

## 15. Input and Output Examples

Python executable input:
```json
{"n":3,"edges":[[0,1,-2],[1,2,3],[0,2,4]],"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
3 3 1 0 1 -2 1 2 3 0 2 4
```
Both output:
```json
[[0,-2,1],[null,0,3],[null,null,0]]
```
Potential magnitudes are bounded by 99*10^6; reweighted costs remain below 2*100*10^6 and fit canonical Dijkstra’s [0,10^12] contract. Finite reweighted sums and endpoint corrections fit signed 64-bit integers. Initializing all labels to zero avoids allocating E+V virtual edges, retaining support for the full E=10000 limit. Unreachable infinity is never corrected arithmetically.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Independent tests enumerate small paths and negative cycles, include a disconnected negative cycle and exercise E=10000 without extra super-source allocation.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7202 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Signed sparse all-pairs paths with genuine canonical code reuse and global negative-cycle rejection.

## 18. Disadvantages and Limitations

Requires no negative cycle; returns no partially finite matrix or route reconstruction. The educational V cap is 100, and repeated heap runs may lose to Floyd on dense small inputs.

## 19. When to Use It

Use for sparse directed all-pairs paths with negative edges and no negative cycles.

## 20. When Not to Use It

Use Floyd-Warshall for per-pair negative-cycle influence or dense small instances; use a single-source algorithm when only one source is queried.

## 21. Comparison With Related Algorithms

Floyd and Johnson agree on cycle-free matrices. Johnson invokes the existing Bellman-Ford and Dijkstra modules rather than copies; all remain canonical Graph topics with DP/Greedy conceptual references.

[bellman-ford](../bellman-ford/README.md), [dijkstra](../dijkstra/README.md), [floyd-warshall](../floyd-warshall/README.md)

## 22. Interview Questions

Why does reweighting preserve route comparisons? Why must a super-source reach every vertex? Why may a distance sentinel not receive the potential correction?

## 23. Practice Problems

Derive potentials by hand for the example; add a disconnected negative cycle; compare every finite pair with independently enumerated paths and Floyd-Warshall.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). [Johnson, 1977 original all-pairs shortest-path paper](https://doi.org/10.1145/321992.321993) establishes the potential-reweighting method.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
