# Euler Tour

## 1. Algorithm Name

Euler Tour

## 2. Overview

Flatten one rooted tree into a single-entry DFS preorder and half-open subtree intervals.

## 3. Problem Statement

Return order, tin and tout such that each vertex occurs once, enters at tin[v], and owns the contiguous slice order[tin[v]:tout[v]]. This is a tree DFS encoding, not an Eulerian path through graph edges.

**API:** `euler_tour(parents,root=None)`. One connected rooted tree, n≤10000. Root parent is absent, all other parents valid. Empty input returns three empty arrays; no forests or graph Eulerian-walk behavior is implied.

## 4. Why Do We Need This Algorithm?

Subtree queries become contiguous range queries after flattening. The representation must state whether vertices appear once, twice or on every return visit.

## 5. Real-World Applications

Subtree aggregation through Fenwick/Segment Trees, ancestry checks and rooted-tree preprocessing.

## 6. Core Intuition

DFS fully completes a node’s descendants before moving to a later sibling. Entry indexes and the first position after completion therefore bracket its subtree.

## 7. Prerequisites

Understand rooted trees, explicit node IDs, parent arrays, depths and binary representations. See the [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Validate parent relationships and build children in ascending vertex-ID order. Use explicit entry/exit events. On entry assign tin to the next output position and append the vertex; save an exit event below its children. On exit assign tout to the current output length.

**Correctness and invariants:** Each valid vertex has one parent, so it receives exactly one entry event. The exit event is below every child subtree event, and stack order processes children ascending. Thus all and only descendants lie between entry and exit offsets. Induction proves the interval property and deterministic preorder; tin[u]≤tin[v]<tout[u] characterizes ancestry.

## 9. Pseudocode

```text
push(root,entry) if present
while events:
    u,event=pop()
    if exit: tout[u]=len(order)
    else:
        tin[u]=len(order); order.append(u)
        push(u,exit)
        push children in reverse ascending-ID order
```

## 10. Dry Run

Enter 0 at 0 and 1 at 1; nodes 3 and 4 fill positions 2 and 3. Exit 1 at offset 4, so its subtree is [1,3,4]. Node 2 then enters at 4; root exits at 5.

## 11. Time Complexity

O(n) validation and event processing; every node has one entry and one exit.

## 12. Space Complexity

O(n) owned validation arrays, events and returned order/tin/tout. Explicit events avoid recursion depth limits on chains.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). The function uses an explicit event stack and returns ordinary JSON-compatible arrays; it never mutates the parent sequence. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. Owned vectors and explicit entry/exit events avoid both recursive traversal and recursive node destruction. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"parents":[null,0,0,1,1],"root":0}
```
C++ text input:
```text
5 0 -1 0 0 1 1
```
Grammar: n root, followed by n parent IDs; no query count.

Both output:
```json
{"order":[0,1,3,4,2],"tin":[0,1,4,2,3],"tout":[5,4,5,3,4]}
```
IDs and depths are bounded by n≤10000. Binary-lifting k values are bounded by 10^18 and checked against depth before table indexing; missing ancestors are null. No weighted arithmetic is performed.

## 16. Edge Cases

Chains produce nested intervals; stars produce adjacent one-element leaf intervals. Duplicate application values do not alter IDs. Child order follows IDs rather than arbitrary insertion order.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. All incremental-parent trees through five vertices plus 140 seed-8202 randomly relabeled trees use independent ancestor-chain walking. Euler intervals are checked against explicit ancestor/subtree membership; 10000-node chains and stars test the iterative construction. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Simple subtree-range encoding, constant-time ancestry checks and safe iterative depth handling.

## 18. Disadvantages and Limitations

This one-entry representation cannot be passed directly to the standard repeated-visit Euler/RMQ LCA algorithm. Topology changes require rebuilding intervals.

## 19. When to Use It

Use before subtree sums or ancestry predicates on a static rooted tree.

## 20. When Not to Use It

Use an actual graph Eulerian algorithm for edge-covering walks, or a repeated-visit tour if an LCA RMQ proof requires that representation.

## 21. Comparison With Related Algorithms

LCA and Binary Lifting answer ancestor meeting queries directly. Fenwick/Segment Tree can aggregate values placed in this preorder; tree Euler Tour remains a distinct canonical topic from graph traversal.

[binary-lifting](../binary-lifting/README.md), [fenwick-tree](../fenwick-tree/README.md), [segment-tree](../segment-tree/README.md)

## 22. Interview Questions

Why is tout exclusive? Why does each subtree remain contiguous? How does a one-entry tour differ from a 2n-1 visit sequence?

## 23. Practice Problems

Enumerate each subtree explicitly and compare its interval; map node weights into preorder and answer subtree sums with a range structure.

## 24. References

[Competitive Programmer’s Handbook, author-hosted PDF](https://cses.fi/book/book.pdf), Tree Algorithms and Tree Queries chapters. The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
