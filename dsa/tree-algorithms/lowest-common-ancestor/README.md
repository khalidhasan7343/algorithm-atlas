# Lowest Common Ancestor

## 1. Algorithm Name

Lowest Common Ancestor

## 2. Overview

Find the deepest common ancestor by aligning depths and walking parents together.

## 3. Problem Statement

Preprocess one connected rooted tree and answer LCA queries on explicit vertex IDs. Queried IDs must exist; duplicate payload values, if stored by an application, do not affect identity.

**API:** `LCA(parents, root=None).query(a,b); solve(parents,root,queries)`. One rooted connected tree with n≤10000. Exactly root has parent None/-1. Empty construction is valid, but any query on it is rejected. Query pairs and indices are validated; q≤1000 in solve.

## 4. Why Do We Need This Algorithm?

The root is always a common ancestor, but queries require the deepest one. Repeated queries benefit from validated parent/depth preprocessing even before jump-table optimization.

## 5. Real-World Applications

Hierarchy comparisons, routing through a rooted organizational tree and tree-distance calculations.

## 6. Core Intuition

Removing the deeper vertex’s excess depth brings both candidates to one level. Moving them upward together then meets first at their deepest shared ancestor.

## 7. Prerequisites

Understand rooted trees, explicit node IDs, parent arrays, depths and binary representations. See the [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Validate a single parent-array tree with root parent absent. Build children and depths iteratively. For a query, validate both IDs, align depths, then advance both parents until the IDs match.

**Correctness and invariants:** Depth alignment cannot skip the LCA because all skipped ancestors lie strictly below the other vertex’s depth. Once equal-depth candidates differ, their LCA is strictly above both, so advancing together preserves the answer. The first equal candidate is deepest. Identical nodes return immediately; an ancestor-descendant pair meets during alignment.

## 9. Pseudocode

```text
while depth[a]>depth[b]: a=parent[a]
while depth[b]>depth[a]: b=parent[b]
while a!=b: a=parent[a]; b=parent[b]
return a
```

## 10. Dry Run

Nodes 3 and 4 are siblings under 1, so LCA=1. Align 3 with 2, then move both to 0. A root query returns 0, and identical node 1 returns itself.

## 11. Time Complexity

O(n) preprocessing and O(h) per query, h the maximum depth/height. The executable with q queries costs O(n+qh); no O(log n) query claim is made for this simple implementation.

## 12. Space Complexity

O(n) parent/depth/children storage, O(1) additional space per query, plus O(q) returned answers.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). The class copies validated parent relationships; preprocessing is explicit and the query logic is local to this canonical implementation. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. A validated RootedTree owns parent/depth/children vectors; construct it with rooted_tree before the typed index. No parent pointers into caller storage or recursive owning chains exist. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"parents":[null,0,0,1,1],"root":0,"queries":[[3,4],[3,2],[0,4],[1,1]]}
```
C++ text input:
```text
5 0 -1 0 0 1 1 4 3 4 3 2 0 4 1 1
```
Grammar: n root, n parent IDs (-1 absent), q, then q pairs a b.

Both output:
```json
[1,0,0,1]
```
IDs and depths are bounded by n≤10000. Binary-lifting k values are bounded by 10^18 and checked against depth before table indexing; missing ancestors are null. No weighted arithmetic is performed.

## 16. Edge Cases

Root queries, equal nodes, ancestor-descendant pairs, relabeled roots, chains and stars are covered. Missing or invalid queried IDs raise errors rather than being mistaken for payload values.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. All incremental-parent trees through five vertices plus 140 seed-8202 randomly relabeled trees use independent ancestor-chain walking. Euler intervals are checked against explicit ancestor/subtree membership; 10000-node chains and stars test the iterative construction. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Small, directly verifiable query procedure and linear preprocessing.

## 18. Disadvantages and Limitations

A chain requires linear query work. The static index must be rebuilt if the parent relation changes. Forest/cross-component semantics are not supported.

## 19. When to Use It

Use for occasional LCA queries or as an independent baseline for optimized techniques.

## 20. When Not to Use It

Use Binary Lifting for many queries on deep trees; use a dynamic-tree structure if relationships change.

## 21. Comparison With Related Algorithms

Binary Lifting adds O(n log n) preprocessing/storage to reduce queries to O(log n). Euler intervals identify ancestry but the one-entry Euler output here does not by itself implement an LCA RMQ index.

[binary-lifting](../binary-lifting/README.md), [euler-tour](../euler-tour/README.md)

## 22. Interview Questions

Why must depths be aligned first? Why is an absent query node an error rather than the root?

## 23. Practice Problems

Derive distance(a,b)=depth[a]+depth[b]-2*depth[LCA(a,b)]; compare every query with jump tables.

## 24. References

[Competitive Programmer’s Handbook, author-hosted PDF](https://cses.fi/book/book.pdf), Tree Algorithms and Tree Queries chapters. The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
