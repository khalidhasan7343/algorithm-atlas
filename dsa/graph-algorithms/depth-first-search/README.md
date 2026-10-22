# Depth-First Search

## 1. Algorithm Name

Depth-First Search

## 2. Overview

Explore an entire graph forest with an explicit stack that retains each vertex’s next adjacency position.

## 3. Problem Statement

Return discovery and finishing orders, predecessor vertices/edge IDs and forest-root labels for every vertex.

**Contract:** `dfs(n, edges, directed=True)`. Directed or undirected unweighted pairs; the complete forest has no source argument. Component labels are DFS roots, not SCC identifiers. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

Finishing order and ancestor relationships expose structure that a breadth-first order does not retain. Explicit frames also avoid recursion-depth failures.

## 5. Real-World Applications

Dependency analysis, traversal preprocessing and the foundation for SCC or low-link algorithms.

## 6. Core Intuition

A suspended frame represents a recursive call. Advance its iterator before descending, and finish a vertex only when all its arcs have been considered.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Review queues, stacks and priority queues as used below.

## 8. Step-by-Step Working Process

Scan roots in increasing vertex order. For an unseen root, mark and discover it. Keep (vertex, next-neighbor) frames. Discover unseen neighbors and push frames; pop exhausted frames into finish order.

**Correctness:** At every step, active frames form a tree path and each scanned arc is processed exactly once. An unseen neighbor is permanently discovered before its frame is pushed, preventing duplicate visits. Exhaustion establishes finishing after every DFS descendant. Ascending root scans cover isolated and disconnected vertices.

## 9. Pseudocode

```text
for root in 0..V-1:
    if unseen(root):
        discover(root); push frame(root)
        while frames:
            if top exhausted: finish(top); pop
            else:
                v = next neighbor(top)
                if unseen(v): set parent; discover(v); push frame(v)
```

## 10. Dry Run

Frames descend 0→1→2, then finish 2,1,0. Root 3 is isolated and finishes last. The direct arc 0→2 is scanned after 2 has already finished.

## 11. Time Complexity

O(V+E) for adjacency construction and traversal.

## 12. Space Complexity

O(V+E) including graph and results; explicit frames occupy O(V).

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `dfs(n, edges, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The implementation uses only the Python standard library.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. Adjacency and explicit containers mirror the documented algorithm; integer tokens and bounds are checked before use.

## 15. Input and Output Examples

Python executable input:
```json
{"n":4,"edges":[[0,1],[0,2],[1,2]],"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
4 3 1 0 1 0 2 1 2
```
Both output:
```json
{"order":[0,1,2,3],"finish":[2,1,0,3],"parent":[null,0,1,null],"parent_edge":[null,0,2,null],"component":[0,0,0,3]}
```
This unweighted algorithm uses bounded indices, indegrees or hop counts; values fit signed 64-bit integers. No infinity arithmetic is performed.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Self-loops never create a new traversal discovery; duplicate arcs retain their original identities. Output ordering follows the explicit rules above.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7101 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Linear traversal with no language recursion limit, preserving recursive-style finishing semantics.

## 18. Disadvantages and Limitations

A DFS forest label is not a directed reachability equivalence class. This API does not classify edges or report cycles.

## 19. When to Use It

Use for finishing order, graph coverage and as a starting point for structural analysis.

## 20. When Not to Use It

Use BFS for minimum hop counts and SCC algorithms for directed mutual reachability.

## 21. Comparison With Related Algorithms

BFS prioritizes depth layers. Tarjan augments DFS with discovery/low-link values and stack membership; Kosaraju uses two passes.

[breadth-first-search](../breadth-first-search/README.md), [tarjan-strongly-connected-components](../tarjan-strongly-connected-components/README.md), [kosaraju-strongly-connected-components](../kosaraju-strongly-connected-components/README.md)

## 22. Interview Questions

Why must a frame remember the next neighbor? How can finishing order differ from discovery order?

## 23. Practice Problems

Verify that every DFS tree child finishes before its parent; compare directed forest labels with true SCCs.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). These primary teaching sources establish the graph vocabulary and traversal foundations; the exact bounded API and tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
