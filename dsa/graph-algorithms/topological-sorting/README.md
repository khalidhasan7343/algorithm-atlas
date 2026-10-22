# Topological Sorting

## 1. Algorithm Name

Topological Sorting

## 2. Overview

Produce the lexicographically smallest topological order using Kahn’s indegree algorithm and a min-heap.

## 3. Problem Statement

For a directed graph, return an order placing every edge’s source before its target; return null if any directed cycle prevents a complete order.

**Contract:** `topological_sort(n, edges, directed=True)`. Directed unweighted pairs only. Undirected mode is rejected. Empty graphs return []; any self-loop or longer directed cycle returns null. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

Dependencies require a linear execution order. A partial prefix must not be mistaken for a valid full order when a separate cyclic component exists.

## 5. Real-World Applications

Build scheduling, course prerequisite plans and DAG dynamic-programming evaluation.

## 6. Core Intuition

An indegree-zero vertex has no remaining prerequisite. Remove the smallest such vertex, then expose newly ready vertices.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Review queues, stacks and priority queues as used below.

## 8. Step-by-Step Working Process

Count indegree for every input arc, including duplicates. Heapify all zero-indegree vertices. Pop the smallest vertex, decrement each outgoing arc’s target indegree and insert newly zero targets. Accept only if all V vertices were removed.

**Correctness:** The heap contains exactly the remaining indegree-zero vertices. Removing one respects all incoming dependencies; induction proves the output prefix valid. A nonempty remainder with no ready vertex has a cycle by following predecessors. Choosing the smallest legal next vertex at every position gives the lexicographically smallest valid ordering.

## 9. Pseudocode

```text
degree[v] = number of incoming arcs
ready = min_heap(vertices of degree zero)
while ready:
    u=pop_min(); order.append(u)
    for each arc u→v:
        degree[v]-=1
        if degree[v]==0: ready.push(v)
return order if len(order)==V else null
```

## 10. Dry Run

Initially ready={0,1,3}. Pop 0, then 1; vertex 2 becomes ready and is smaller than 3, so the final order is [0,1,2,3].

## 11. Time Complexity

O(E+V log V), since each arc decrements once and each vertex enters/leaves the heap once.

## 12. Space Complexity

O(V+E) including adjacency, indegrees, heap and order.

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `topological_sort(n, edges, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The implementation uses only the Python standard library.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. Adjacency and explicit containers mirror the documented algorithm; integer tokens and bounds are checked before use.

## 15. Input and Output Examples

Python executable input:
```json
{"n":4,"edges":[[0,2],[1,2]],"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
4 2 1 0 2 1 2
```
Both output:
```json
[0,1,2,3]
```
This unweighted algorithm uses bounded indices, indegrees or hop counts; values fit signed 64-bit integers. No infinity arithmetic is performed.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Self-loops never create a new traversal discovery; duplicate arcs retain their original identities. Output ordering follows the explicit rules above.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7101 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Deterministic minimal order and explicit failure for cycles anywhere in the graph.

## 18. Disadvantages and Limitations

Requires a directed acyclic graph for success; a null result does not include a cycle witness. Heap tie-breaking costs more than FIFO Kahn sorting.

## 19. When to Use It

Use when dependencies need a reproducible order or DAG processing sequence.

## 20. When Not to Use It

Use SCC decomposition to inspect cyclic dependencies or DFS finishing order when a minimal order is unnecessary.

## 21. Comparison With Related Algorithms

DFS reverse finishing yields an order only with cycle detection. FIFO Kahn is O(V+E) but lacks this API’s smallest-ready guarantee.

[depth-first-search](../depth-first-search/README.md), [kosaraju-strongly-connected-components](../kosaraju-strongly-connected-components/README.md)

## 22. Interview Questions

Why can a disconnected cyclic component invalidate an otherwise valid prefix? How must parallel arcs affect indegrees?

## 23. Practice Problems

Enumerate every valid ordering of a small DAG; compare with the smallest returned order; add one edge that creates a cycle.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). These primary teaching sources establish the graph vocabulary and traversal foundations; the exact bounded API and tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
