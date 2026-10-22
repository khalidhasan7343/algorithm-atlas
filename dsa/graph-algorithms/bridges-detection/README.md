# Bridges Detection

## 1. Algorithm Name

Bridges Detection

## 2. Overview

Find undirected edges whose removal increases the number of connected components.

## 3. Problem Statement

Return original edge IDs of all bridges, sorted ascending. Process every disconnected component and preserve parallel-edge identities.

**Contract:** `bridges(n, edges, directed=False)`. Undirected unweighted pairs only. Directed mode is rejected. V≤1000, E≤10000. Empty graphs and isolated vertices have no critical edge/vertex. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

Local degree alone does not reveal network vulnerability. Cycles provide alternate routes; DFS low links summarize whether a subtree can escape without its parent connection.

## 5. Real-World Applications

Network resilience audits, critical road links and cut-vertex decomposition.

## 6. Core Intuition

For a DFS tree child v of u, low[v] is the earliest discovery reachable from v’s subtree using tree descent and at most one non-parent edge. The tree edge is a bridge exactly when low[v]>discovery[u].

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Understand adjacency lists, weighted paths, reachability and priority queues or relaxation as used below.

## 8. Step-by-Step Working Process

Run an iterative DFS forest with discovery, low, parent vertex, exact parent edge ID and child counts. Skip the reverse of the exact parent edge only. Lower low[u] using visited neighbor discovery indices. On child return, propagate low to the parent and apply the strict bridge test.

**Correctness:** Low links summarize whether a subtree can reach an ancestor without the exact parent edge. A second parallel edge is such an alternate route and must not be skipped. If low[v]>discovery[u], removing the tree edge leaves the subtree disconnected; otherwise an ancestor escape plus tree edges preserves connection. Non-tree edges lie on an alternate route and cannot be bridges. The same reasoning applies component by component.

## 9. Pseudocode

```text
discover u: discovery[u]=low[u]=clock++
for arc (u,v,id):
    if id==parent_edge[u]: continue
    if unseen(v): DFS(v); propagate low[v]; test child return
    else: low[u]=min(low[u],discovery[v])
bridge(parent_edge[v]) iff low[v]>discovery[parent[v]]
```

## 10. Dry Run

Edges 0 and 1 are parallel, so neither is a bridge. Edge 2 is the only route to vertex 2; its self-loop supplies no escape. Removing vertex 1 separates 0 from 2. Isolated vertex 3 does not change either classification.

## 11. Time Complexity

O(V+E) DFS work; sorting returned edge IDs adds O(B log B) for B bridges.

## 12. Space Complexity

O(V+E) including adjacency, low-link arrays and O(V) explicit frames.

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `bridges(n, edges, directed=False)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The core loop is local to this canonical module; shared support only validates and reconstructs paths.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. Explicit return frames apply low-link tests after a child has exhausted its adjacency; no recursive call stack is used.

## 15. Input and Output Examples

Python executable input:
```json
{"n":4,"edges":[[0,1],[0,1],[1,2],[2,2]],"directed":false}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
4 4 0 0 1 0 1 1 2 2 2
```
Both output:
```json
[2]
```
All arithmetic is on discovery indices and child counts bounded by V. Every undirected arc retains its input edge ID. Self-loops never become DFS tree edges or false bridges; parallel arcs lower low links correctly.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Independent references remove each edge or vertex and recompute connected-component count by closure. In particular, deleting an isolated vertex decreases the count and does not make it an articulation point.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7404 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Linear structural analysis with explicit multigraph support and no recursion limit.

## 18. Disadvantages and Limitations

These are undirected cut criteria; directed strong bridges or strong articulation points require a different algorithm.

## 19. When to Use It

Use to identify single-link or single-vertex failures in undirected networks.

## 20. When Not to Use It

Use SCC for directed mutual reachability or max-flow/cut algorithms for weighted multi-edge cuts.

## 21. Comparison With Related Algorithms

Bridge inequality is strict (>); non-root articulation inequality is non-strict (>=). A cycle through the parent can protect an edge without protecting the parent vertex itself.

[articulation-points](../articulation-points/README.md), [depth-first-search](../depth-first-search/README.md), [union-find](../union-find/README.md)

## 22. Interview Questions

Why skip a parent edge ID rather than every edge to the parent vertex? Why is the root articulation condition different?

## 23. Practice Problems

Compare every result against deletion and component recounting; add a parallel edge to a bridge; draw a graph with an articulation point but no bridges.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). [Princeton graph algorithms](https://algs4.cs.princeton.edu/40graphs/) provides traversal foundations; the multigraph contract and removal oracle are specified here.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
