# Union-Find / Disjoint Set Union

## 1. Algorithm Name

Union-Find / Disjoint Set Union

## 2. Overview

Maintain a partition under merges using parent trees, path compression and union by size.

## 3. Problem Statement

Support find, union, connected, component_size, groups and a component count over a fixed universe. The executable unions every supplied undirected pair.

**Contract:** `UnionFind(n); solve(n, edges, directed=False)`. Undirected unweighted pairs for solve. Class methods take vertices, not directed graph arcs. Universe size is fixed; edge deletion is unsupported. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

Repeated connectivity queries should not rebuild reachability after every added edge. A compact partition supports incremental connectivity efficiently.

## 5. Real-World Applications

Kruskal cycle prevention, account merging and connected components in incrementally added undirected edges.

## 6. Core Intuition

Each tree root names one set. Attach the smaller tree to the larger and shorten every visited parent chain during find.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Review queues, stacks and priority queues as used below.

## 8. Step-by-Step Working Process

Initialize singleton roots and sizes. Find each argument’s root with a first upward walk, then compress the walked path. If roots differ, attach by size; smaller root wins equal-size ties. Update size and count only for a successful merge.

**Correctness:** Initially each tree is a singleton set. Compression changes a parent only to an existing root, preserving membership. A successful union joins exactly two disjoint root trees, so connectivity becomes their set union and count falls by one. Repeated unions and self-unions preserve the partition.

## 9. Pseudocode

```text
find(v):
    root = climb to root(v)
    compress each visited parent to root
    return root
union(a,b):
    a=find(a); b=find(b)
    if a==b: return false
    attach smaller tree root to larger; update size and count
```

## 10. Dry Run

Union 0–1 reduces count 5→4, union 1–2 reduces 4→3. Edge 0–2 already lies in one set and 3–3 is a no-op. Isolated 4 remains its own group.

## 11. Time Complexity

A sequence of m operations costs O((V+m) α(V)) amortized with compression and size weighting. groups additionally sorts component lists: O(V α(V)+V log V) upper bound.

## 12. Space Complexity

O(V) for parents, sizes and materialized groups; the executable’s validated edge input adds O(E).

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `UnionFind(n); solve(n, edges, directed=False)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The implementation uses only the Python standard library.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. Adjacency and explicit containers mirror the documented algorithm; integer tokens and bounds are checked before use.

## 15. Input and Output Examples

Python executable input:
```json
{"n":5,"edges":[[0,1],[1,2],[0,2],[3,3]],"directed":false}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
5 4 0 0 1 1 2 0 2 3 3
```
Both output:
```json
{"groups":[[0,1,2],[3],[4]],"count":3}
```
This unweighted algorithm uses bounded indices, indegrees or hop counts; values fit signed 64-bit integers. No infinity arithmetic is performed.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Self-loops never create a new traversal discovery; duplicate arcs retain their original identities. Output ordering follows the explicit rules above.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7101 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Very fast repeated merges/queries and a small reusable canonical implementation.

## 18. Disadvantages and Limitations

Cannot split sets or handle general directed reachability. A representative is an implementation choice, not necessarily a semantic label.

## 19. When to Use It

Use for monotone undirected connectivity and Kruskal.

## 20. When Not to Use It

Use DFS/BFS for one static traversal or a specialized dynamic structure when edges are removed.

## 21. Comparison With Related Algorithms

A static traversal computes a partition in O(V+E); Union-Find supports interleaved merges and queries. Kruskal reuses this exact canonical class.

[kruskal](../kruskal/README.md), [depth-first-search](../depth-first-search/README.md)

## 22. Interview Questions

Why is only a root’s size meaningful? Why does path compression preserve connectivity?

## 23. Practice Problems

Track the component count after each edge insertion; compare partitions against transitive closure; implement rollback as a separate exercise.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). These primary teaching sources establish the graph vocabulary and traversal foundations; the exact bounded API and tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
