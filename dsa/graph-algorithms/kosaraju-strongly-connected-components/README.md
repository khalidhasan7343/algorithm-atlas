# Kosaraju's Strongly Connected Components

## 1. Algorithm Name

Kosaraju's Strongly Connected Components

## 2. Overview

Find strongly connected components with a finishing-order DFS and a second DFS on the transpose.

## 3. Problem Statement

Partition every directed vertex into maximal sets of mutual reachability. Return vertices sorted within each component, then components lexicographically sorted; traversal accidents do not define the public partition.

**Contract:** `kosaraju_scc(n, edges, directed=True)`. Directed unweighted pairs only; undirected mode is rejected. Empty input returns []; isolated vertices form singleton components. Both passes/frames are iterative and support V=1000 chains. Input edge IDs are zero-based positions. General caps V≤1000 and E≤10000; see the algorithm-specific numeric notes below and [shared conventions](../../../docs/graph-conventions.md). Invalid inputs raise ValueError in Python or invalid_argument in C++; CLIs exit 2.

## 4. Why Do We Need This Algorithm?

Directed reachability is asymmetric. Ordinary DFS forest roots do not identify which vertices can reach each other.

## 5. Real-World Applications

Cyclic dependency grouping, condensation DAG construction and mutually reachable state regions.

## 6. Core Intuition

Finishing order locates a source component of the condensation DAG. Reversing every arc makes it a sink, so a second search cannot escape into an unassigned component.

## 7. Prerequisites

Know vertices, directed arcs versus undirected edges, adjacency lists, connected components and basic asymptotic analysis. Understand adjacency lists, weighted paths, reachability and priority queues or relaxation as used below.

## 8. Step-by-Step Working Process

Run a full iterative DFS forest, recording vertices when their frames finish. Build transpose adjacency by reversing each input arc. Reset visited state, scan roots in reverse finishing order and collect each transpose-reachable unassigned set.

**Correctness:** Contract SCCs into a DAG. For every condensation arc A→B, the largest first-pass finish time of A exceeds B’s. Therefore the first unassigned vertex in reverse finishing order belongs to a source SCC among the remainder. In the transpose, that SCC has no outgoing arc to another unassigned component; the second DFS collects exactly it. Induction partitions all vertices.

## 9. Pseudocode

```text
finish=DFS_postorder(G)
transpose=reverse_all_arcs(G)
reset seen
for root in reverse(finish):
    if unseen(root): collect DFS(transpose,root) as one SCC
```

## 10. Dry Run

The first pass finishes [3,2,1,0]. In the transpose, starting from 0 reaches 1; the next unassigned root 2 reaches 3, giving two components.

## 11. Time Complexity

O(V+E) graph work, plus O(V log V) worst-case sorting for normalized public output.

## 12. Space Complexity

O(V+E) including adjacency, transpose, finish order, visited state and explicit DFS stacks.

## 13. Python Implementation

Use [`python/solution.py`](python/solution.py). `kosaraju_scc(n, edges, directed=True)` exposes the algorithm directly; `solve` is its executable entry point. Shared support validates inputs and handles JSON without performing the algorithm. Input sequences are not mutated. The core loop is local to this canonical module; shared support only validates and reconstructs paths.

## 14. C++ Implementation

Use [`cpp/solution.cpp`](cpp/solution.cpp), compiled with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/graph-example` (or C++20). The `atlas_graph` namespace contains the typed API; construct a validated Graph with make_graph before invoking graph functions. Define ALGORITHM_ATLAS_NO_MAIN when including the canonical source in a driver. Explicit (vertex,next-arc) frames preserve recursive return events without consuming the C++ call stack.

## 15. Input and Output Examples

Python executable input:
```json
{"n":4,"edges":[[0,1],[1,0],[1,2],[2,3],[3,2]],"directed":true}
```
C++ executable input (V E directed, optional source/goal/heuristic, then edge records):
```text
4 5 1 0 1 1 0 1 2 2 3 3 2
```
Both output:
```json
[[0,1],[2,3]]
```
Unweighted indices and discovery clocks are bounded by V≤1000; E≤10000. Self-loops and parallel arcs do not change the SCC partition. No weighted infinity arithmetic is involved.

## 16. Edge Cases

Empty and singleton graphs, isolated vertices, disconnected components, loops, duplicate/parallel edges, invalid references and declared dimension caps are tested. Tests compare normalized partitions with a transitive-closure mutual-reachability oracle, not merely agreement between SCC implementations.

See [independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py). Seed 7404 is fixed; bounded exhaustive references are distinct from the implementation. Tests check behavior, input preservation and executable error handling.

## 17. Advantages

Two clear passes with a direct condensation-DAG proof.

## 18. Disadvantages and Limitations

Requires the transpose and a second traversal; raw finish order alone is not the component partition. Normalized output sorting adds work beyond the linear core.

## 19. When to Use It

Use for directed cyclic regions and condensation preprocessing.

## 20. When Not to Use It

Use Union-Find or traversal for undirected connectivity; use topological sorting only after cycles are absent or SCCs condensed.

## 21. Comparison With Related Algorithms

Tarjan and Kosaraju return the same SCC partition through different invariants. A DFS forest is not an SCC decomposition. Bridges and articulation points use undirected low-link criteria with different meaning.

[tarjan-strongly-connected-components](../tarjan-strongly-connected-components/README.md), [depth-first-search](../depth-first-search/README.md), [topological-sorting](../topological-sorting/README.md)

## 22. Interview Questions

Why reverse finishing order? Why is reversing every arc necessary for the second pass?

## 23. Practice Problems

Build the SCC condensation DAG; compare both implementations with mutual transitive reachability; test isolated self-loops and parallel arcs.

## 24. References

[Princeton Algorithms, graph chapter](https://algs4.cs.princeton.edu/40graphs/) and [MIT 6.006 graph lecture notes](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/e59f8a55929028498953691891229a17_MIT6_006F11_lec14.pdf). [Princeton directed graphs](https://algs4.cs.princeton.edu/42digraph/) covers strong connectivity and two-pass DFS.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). Distributed under the [MIT License](../../../LICENSE).
