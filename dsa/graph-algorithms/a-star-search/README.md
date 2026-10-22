# A* Search

## 1. Algorithm Name

A* Search

## 2. Overview

Search for one goal by ordering tentative routes by g+h, reopening vertices whenever their known route improves.

## 3. Problem Statement

Return the goal cost, vertex path and original edge IDs, or cost null and empty paths if unreachable. Optimality is guaranteed for nonnegative weights and an admissible heuristic; arbitrary heuristics can give a suboptimal result.

**Contract:** `a_star(n, edges, source=None, goal=None, heuristic=None, directed=True)`. Directed or undirected weighted triples, weights in [0,10^6]. Exactly V integer heuristic entries in [0,10^9] are required, with h(goal)=0. Both source and goal are None only for V=0; the empty result is unreachable. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

A goal-distance estimate can focus exploration. The implementation must distinguish safe heuristic assumptions from unverified caller guesses.

## 5. Real-World Applications

Grid or state-space pathfinding with a known lower-bound estimate, such as Manhattan distance under compatible movement costs.

## 6. Core Intuition

g(v) is the best discovered source cost; h(v) estimates remaining cost; f(v)=g(v)+h(v) orders the heap. Keep no permanent closed set, because an inconsistent admissible estimate can reveal a cheaper route after a vertex was expanded.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Understand adjacency lists, weighted paths, reachability and priority queues or relaxation as used below.

## 8. Step-by-Step Working Process

Validate all edges and heuristic entries. Push (h(source),0,source). Pop by (f,g,vertex), discarding stale g labels. On a goal pop, reconstruct its predecessor path. Otherwise relax strict improvements and push the target again even if it was previously expanded.

**Correctness:** Admissible means h(v) never exceeds true remaining goal cost; consistent means h(u)≤w(u,v)+h(v) for every arc and is a stronger condition here. Before an optimal goal cost is known, a frontier label on an optimal route has f at most that optimum. Reopening preserves that frontier after better routes appear, so a popped goal with h(goal)=0 cannot have a larger cost. If h overestimates, that inequality fails and early termination can be suboptimal. The code validates dimensions and numeric bounds, while admissibility remains a caller guarantee.

## 9. Pseudocode

```text
g[source]=0; heap.push((h[source],0,source))
while heap:
    f,cost,u=pop_min()
    if cost != g[u]: continue
    if u==goal: return reconstructed route
    for u→v of cost w:
        if cost+w < g[v]:
            update g[v],parent[v]; push(g[v]+h[v],g[v],v)
return unreachable
```

## 10. Dry Run

Vertex 1 first expands at g=3 and offers goal cost 5. Vertex 2 at g=1 then improves 1 to g=2. Reopening 1 improves the goal to 4. h(2)=3 is admissible but inconsistent across 2→1, so permanently closing 1 would be wrong.

## 11. Time Complexity

Let R be successful label improvements and A the outgoing arcs scanned over all expansions. Time is O(V+E+A+(R+1) log(R+1)); memory for heap labels is O(R). With consistent h, each vertex expands at most once and this becomes the lazy Dijkstra O(V+E+(E+1) log(E+1)) bound. Inconsistent heuristics can cause many reopenings; no general Dijkstra-like bound is claimed.

## 12. Space Complexity

O(V+E+R) for adjacency, distances, predecessors and pending labels. Reopening can increase heap space beyond a single expansion per vertex.

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `a_star(n, edges, source=None, goal=None, heuristic=None, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The core loop is local to this canonical module; shared support only validates and reconstructs paths.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. The typed result uses bounded long long distances, with distinct sentinels for unreachable and negative-cycle values. Sentinel values are never used in arithmetic.

## 15. Input and Output Examples

Python executable input:
```json
{"n":4,"edges":[[0,1,3],[0,2,1],[2,1,1],[1,3,2],[2,3,100]],"source":0,"goal":3,"heuristic":[0,0,3,0],"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
4 5 1 0 3 0 0 3 0 0 1 3 0 2 1 2 1 1 1 3 2 2 3 100
```
Both output:
```json
{"cost":4,"path":[0,2,1,3],"edges":[1,2,3]}
```
V≤1000, E≤10000; finite simple paths have cost≤999*10^6. Adding h≤10^9 remains within signed 64-bit limits. Start=goal returns cost 0 after full validation. The overestimate example 0→1=1,1→2=1,0→2=5 with h=[0,100,0] returns 5 despite the true optimum 2; tests explicitly retain this documented limitation.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Tests enumerate simple paths for true goal costs and generate admissible heuristics from those independent distances. They cover unreachable goals, start=goal, empty graphs, zero cycles and reopening.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7505 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Goal-directed exploration, explicit paths and support for admissible inconsistent estimates through reopening.

## 18. Disadvantages and Limitations

The API cannot certify admissibility from caller intent. Poor estimates can increase work; overestimates can sacrifice optimality. Negative edges are rejected.

## 19. When to Use It

Use for one goal with a defensible lower-bound heuristic.

## 20. When Not to Use It

Use Dijkstra when no heuristic is available or all destination distances are needed; use Bellman-Ford for signed costs.

## 21. Comparison With Related Algorithms

Zero-heuristic A* agrees with Dijkstra on the goal cost. A consistent heuristic avoids reopening; an admissible inconsistent heuristic needs the supported improvement behavior.

[dijkstra](../dijkstra/README.md), [breadth-first-search](../breadth-first-search/README.md), [bellman-ford](../bellman-ford/README.md)

## 22. Interview Questions

Why does a permanent closed set fail with inconsistency? Why require h(goal)=0? Which optimality step uses admissibility?

## 23. Practice Problems

Derive an admissible grid heuristic; run the reopening example; deliberately overestimate and compare against the independent path oracle.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). [Hart, Nilsson and Raphael, 1968 original A* paper](https://doi.org/10.1109/TSSC.1968.300136) introduces heuristic shortest-path search.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
