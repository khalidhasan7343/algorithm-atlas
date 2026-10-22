# Prim's Minimum Spanning Tree

## 1. Algorithm Name

Prim's Minimum Spanning Tree

## 2. Overview

Grow one tree per connected component with a heap of outgoing candidate edges.

## 3. Problem Statement

Return a minimum spanning forest: total weight and original input edge IDs. Each original undirected component is spanned; isolated vertices need no selected edges.

**Contract:** `prim(n, edges, directed=False)`. Undirected weighted triples only, with weights in [-10^6,10^6]. Directed mode is rejected. Empty graphs return weight 0 and no edges; disconnected graphs return a forest. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

A route shortest-path tree need not minimize the sum of construction costs. An MST minimizes the edge weight needed to connect each component.

## 5. Real-World Applications

Low-cost network construction, clustering by merging components, and infrastructure planning within disconnected regions.

## 6. Core Intuition

The cheapest edge crossing from the grown tree to an unseen vertex is safe.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Understand adjacency lists, weighted paths, reachability and priority queues or relaxation as used below.

## 8. Step-by-Step Working Process

Scan component roots ascending. Mark an unseen root, push its outgoing edges, and repeatedly pop the smallest (weight,edge ID,from,to). Skip already seen targets. Accept a new target once and add its outgoing candidates.

**Correctness:** Cut property: among edges crossing any cut, a minimum-weight edge belongs to some minimum spanning tree. Exchange it for a crossing edge in an optimum if needed without increasing weight. Each accepted edge is cheapest across the current grown-tree cut; selecting an unseen target prevents cycles. Repeating within every original component yields a spanning forest of minimum total weight, even with negative or duplicate weights.

## 9. Pseudocode

```text
for unseen root in ascending vertices:
    mark(root); heap=outgoing(root)
    while heap:
        w,id,u,v=pop_min()
        if seen(v): continue
        mark(v); accept(id); total+=w
        push edges from v to unseen targets
```

## 10. Dry Run

Root 0 offers edges 2(cost 2) and 0(cost 3). Accept 2 to reach vertex 2, then edge 1(cost -1) reaches 1. The stale edge to 1 is skipped. Root 3 contributes no edge.

## 11. Time Complexity

O(V+E log(E+1)) with a lazy edge heap. Original parallel edges remain distinct, so log E is the direct heap bound.

## 12. Space Complexity

O(V+E) including adjacency validation, selected IDs, visited flags and candidate heap.

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `prim(n, edges, directed=False)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The core loop is local to this canonical module; shared support only validates and reconstructs paths.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. The heap orders (weight,edge ID,from,to), and stale edges to already seen targets are discarded.

## 15. Input and Output Examples

Python executable input:
```json
{"n":4,"edges":[[0,1,3],[1,2,-1],[0,2,2]],"directed":false}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
4 3 0 0 1 3 1 2 -1 0 2 2
```
Both output:
```json
{"weight":1,"edges":[2,1]}
```
With V≤1000, a forest selects at most 999 edges of magnitude≤10^6, so its total fits signed 64-bit integers. Self-loops are never selected; parallel edges keep separate IDs. The returned selection order follows the documented tie rules, not a claim of a unique optimum.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Zero weights, equal-cost choices, unreachable regions and invalid signed bounds are explicit cases. Finite paths retain original edge IDs; affected or unreachable vertices have no predecessor.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7303 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Local tree growth with efficient adjacency access and explicit disconnected restarts.

## 18. Disadvantages and Limitations

A minimum forest can be nonunique; equal total weights alone are insufficient to validate arbitrary selected edges. This API is for undirected graphs, not directed arborescences.

## 19. When to Use It

Use for minimum-cost undirected component connectivity. A11 links this canonical Graph implementation as a Greedy application.

## 20. When Not to Use It

Use shortest-path algorithms when source-to-target route costs are the objective, or a directed arborescence algorithm for directed connectivity.

## 21. Comparison With Related Algorithms

Prim and Kruskal must agree on total forest weight, while selected IDs may differ across tied optima. Tests enumerate bounded edge subsets, check spanning connectivity and verify the forest size implies acyclicity.

[kruskal](../kruskal/README.md), [union-find](../union-find/README.md), [dijkstra](../dijkstra/README.md)

## 22. Interview Questions

Why can an MST contain negative edges? How does the cut exchange proof handle equal weights? Why is a disconnected result a forest?

## 23. Practice Problems

Enumerate all minimum forests of a tiny multigraph; compare both algorithms; add a negative self-loop and verify it is ignored.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). [Princeton minimum spanning trees](https://algs4.cs.princeton.edu/43mst/) explains cut safety, negative weights and minimum spanning forests.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
