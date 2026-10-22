# Binary Lifting

## 1. Algorithm Name

Binary Lifting

## 2. Overview

Precompute power-of-two ancestor jumps for k-th ancestor and LCA queries.

## 3. Problem Statement

Return an ancestor k edges above a valid vertex, or null if it does not exist; also answer LCA on the same validated static rooted tree.

**API:** `BinaryLifting(parents,root=None).kth_ancestor(v,k) / .lca(a,b)`. Single static rooted tree, n≤10000; k in [0,10^18]. k=0 returns the vertex itself, root has no positive-distance ancestor. solve operations are [0,v,k] or [1,a,b], at most 1000.

## 4. Why Do We Need This Algorithm?

Parent walking can cost n steps per query on a chain. Binary decomposition skips exponentially longer segments.

## 5. Real-World Applications

Repeated hierarchy queries, tree-distance services and ancestor-constrained search.

## 6. Core Intuition

`up[j][v]` is the ancestor 2^j edges above v. Decompose k into set bits and combine those jumps; LCA uses the same table to approach the meeting point from below.

## 7. Prerequisites

Understand rooted trees, explicit node IDs, parent arrays, depths and binary representations. See the [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Validate parents and compute depth iteratively. Store direct parents as row 0. Build each row from the preceding row, propagating absent ancestors. For k-th queries reject invalid k/vertices and return null when k exceeds depth. For LCA align depths and scan rows largest first, moving both only when their jump ancestors differ.

**Correctness and invariants:** Induct on j: composing two 2^(j-1) ancestors yields exactly the 2^j ancestor, or absence. Binary decomposition then advances exactly k edges. For LCA, equal-depth candidates remain strictly below their common ancestor whenever distinct jump ancestors allow a joint move. The largest-to-smallest scan ends at distinct children of their LCA, whose common parent is the answer.

## 9. Pseudocode

```text
up[0][v]=parent[v]
up[j][v]=up[j-1][up[j-1][v]] if intermediate exists
kth(v,k): return null if k>depth[v]; apply set-bit jumps
lca(a,b):
    align depth with kth
    if equal: return a
    for j descending: if up[j][a]!=up[j][b]: jump both
    return parent[a]
```

## 10. Dry Run

Row 0 sends 4→1 and row 1 sends 4→0. A two-edge ancestor is root 0; three exceeds depth 2 and returns null. Sibling LCA(3,4)=1.

## 11. Time Complexity

O(n log n) preprocessing; O(log n) k-th ancestor and LCA queries after O(1) bounds checks. Returning null for k>depth avoids iterating over 60 k bits or indexing beyond table height.

## 12. Space Complexity

O(n log n) for ancestor rows, plus O(n) validated tree/depth storage and O(q) output.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). The class copies validated parent relationships; preprocessing is explicit and the query logic is local to this canonical implementation. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. A validated RootedTree owns parent/depth/children vectors; construct it with rooted_tree before the typed index. No parent pointers into caller storage or recursive owning chains exist. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"parents":[null,0,0,1,1],"root":0,"operations":[[0,4,0],[0,4,2],[0,4,3],[1,3,4]]}
```
C++ text input:
```text
5 0 -1 0 0 1 1 4 0 4 0 0 4 2 0 4 3 1 3 4
```
Grammar: n root, n parent IDs, q, then q triples: 0 vertex k or 1 a b.

Both output:
```json
[4,0,null,1]
```
IDs and depths are bounded by n≤10000. Binary-lifting k values are bounded by 10^18 and checked against depth before table indexing; missing ancestors are null. No weighted arithmetic is performed.

## 16. Edge Cases

Large k, root k=0, missing ancestors, invalid negative/over-limit k, same-node LCA and relabeled parent arrays are tested. Both equal-depth jump ancestors are absent together, preventing invalid None/-1 table access.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. All incremental-parent trees through five vertices plus 140 seed-8202 randomly relabeled trees use independent ancestor-chain walking. Euler intervals are checked against explicit ancestor/subtree membership; 10000-node chains and stars test the iterative construction. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Fast repeated ancestor/LCA queries with an explicit recurrence and bounded table.

## 18. Disadvantages and Limitations

More memory than parent walking; parent mutations invalidate the whole table. This does not support dynamic reparenting or forests.

## 19. When to Use It

Use for many queries on a fixed tree, especially chains.

## 20. When Not to Use It

Use naive LCA for very few queries or another data structure for changing topology.

## 21. Comparison With Related Algorithms

The canonical simple LCA walks parents and is cross-checked independently. Euler Tour supports subtree intervals but has a different output contract.

[lowest-common-ancestor](../lowest-common-ancestor/README.md), [euler-tour](../euler-tour/README.md)

## 22. Interview Questions

Why is log n table height sufficient even when k is allowed up to 10^18? Why may jump targets of equal-depth nodes be compared safely?

## 23. Practice Problems

Trace k=13 as 8+4+1 jumps; test root and absent ancestors; compare all small-tree LCA pairs with parent walking.

## 24. References

[Competitive Programmer’s Handbook, author-hosted PDF](https://cses.fi/book/book.pdf), Tree Algorithms and Tree Queries chapters. The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
