# Breadth-First Search

## 1. Algorithm Name

Breadth-First Search

## 2. Overview

Explore vertices in increasing number of edges from a source using a FIFO queue.

## 3. Problem Statement

Return the reachable discovery order, minimum hop counts and first-discovery predecessor edges. Vertices outside the source component retain null distances.

**Contract:** `bfs(n, edges, source=None, directed=True)`. Directed or undirected unweighted pairs. The source is mandatory for nonempty graphs. Only its reachable component appears in order. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

A stack can find a path without finding a shortest path. Queue layers guarantee a minimum-hop route when every edge has equal cost.

## 5. Real-World Applications

Network broadcast hops, shortest moves in an unweighted maze, and degrees of separation.

## 6. Core Intuition

Every vertex at depth k leaves the queue before a vertex at depth k+1. Discover a vertex only once, when its first shortest predecessor is processed.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Review queues, stacks and priority queues as used below.

## 8. Step-by-Step Working Process

Set the source distance to zero and enqueue it. Pop the front, append it to order, and scan adjacency in input order. Discover each unseen neighbor with distance[u]+1, parent u and its original edge ID.

**Correctness:** Induct on queue layers. The source is optimal at zero. Any shorter path to a newly discovered depth-k vertex would have a depth-(k-2) predecessor processed earlier, contradicting first discovery. The saved edge therefore extends a shortest path. Each reachable vertex enters the queue once.

## 9. Pseudocode

```text
distance[source] = 0; queue.push(source)
while queue not empty:
    u = queue.pop_front(); order.append(u)
    for (v, edge_id) in adjacency[u]:
        if distance[v] is absent:
            distance[v] = distance[u] + 1
            parent[v] = (u, edge_id); queue.push(v)
```

## 10. Dry Run

Queue [0] becomes [1,2]. Processing 1 discovers 3; processing 2 leaves that predecessor unchanged. Vertex 4 remains unreachable.

## 11. Time Complexity

O(V+E) including adjacency construction and output initialization; each directed arc is scanned once.

## 12. Space Complexity

O(V+E) including input adjacency and returned arrays; the queue itself uses O(V).

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `bfs(n, edges, source=None, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The implementation uses only the Python standard library.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. Adjacency and explicit containers mirror the documented algorithm; integer tokens and bounds are checked before use.

## 15. Input and Output Examples

Python executable input:
```json
{"n":5,"edges":[[0,1],[0,2],[1,3],[2,3]],"source":0,"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
5 4 1 0 0 1 0 2 1 3 2 3
```
Both output:
```json
{"order":[0,1,2,3],"distance":[0,1,1,2,null],"parent":[null,0,0,1,null],"parent_edge":[null,0,1,2,null]}
```
This unweighted algorithm uses bounded indices, indegrees or hop counts; values fit signed 64-bit integers. No infinity arithmetic is performed.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Self-loops never create a new traversal discovery; duplicate arcs retain their original identities. Output ordering follows the explicit rules above.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7101 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Linear work, simple shortest-hop proof and explicit path reconstruction.

## 18. Disadvantages and Limitations

Hop counts do not minimize arbitrary weighted costs. The stored predecessor represents one shortest path, not all ties.

## 19. When to Use It

Use for unweighted shortest paths or reachable coverage from one root.

## 20. When Not to Use It

Use Dijkstra for nonnegative unequal weights; use DFS when finishing order is needed.

## 21. Comparison With Related Algorithms

DFS explores deeply without a hop-optimal guarantee. Dijkstra generalizes queue ordering to nonnegative weighted distances.

[depth-first-search](../depth-first-search/README.md), [dijkstra](../dijkstra/README.md)

## 22. Interview Questions

Why mark on enqueue rather than dequeue? Why does input adjacency order change parents but not distances?

## 23. Practice Problems

Recover a maze route; compare distances with Dijkstra on unit weights; modify the queue initialization for multiple sources.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). These primary teaching sources establish the graph vocabulary and traversal foundations; the exact bounded API and tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
