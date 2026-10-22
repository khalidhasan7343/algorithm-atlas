# Segment Tree

## 1. Algorithm Name

Segment Tree

## 2. Overview

Maintain range sums in a genuine complete binary segment hierarchy with point replacement.

## 3. Problem Statement

Store a mutable array and answer sums over half-open ranges [left,right). Expose set(index,value) and range_sum(left,right). Empty ranges return zero.

**API:** `SegmentTree(values).set(i,value) / .range_sum(l,r)`. n≤10000, values in [-10^9,10^9]; zero-based indices and half-open ranges. Replacement values must remain within the value bound; no lazy propagation or range update is implemented. Invalid operations reject before changing stored state. solve permits at most 1000 operations.

## 4. Why Do We Need This Algorithm?

Repeated full-array summation costs O(n) per query. A tree of reusable aggregates limits each update/query to logarithmically many blocks.

## 5. Real-World Applications

Dynamic frequency tables, running financial aggregates within stated numeric limits, and subtree sums after Euler flattening.

## 6. Core Intuition

Each parent stores the sum of two disjoint child intervals. A half-open query decomposes into O(log n) canonical intervals from both ends.

## 7. Prerequisites

Understand rooted trees, explicit node IDs, parent arrays, depths and binary representations. See the [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Choose the smallest power-of-two base at least n, place values in leaves and zero-pad the rest. Build parents bottom-up. Point set replaces a leaf and recomputes its ancestors. Range queries use two leaf pointers; consume a right-facing left boundary and a left-facing right boundary before moving both to parents.

**Correctness and invariants:** Initially each leaf represents exactly one value or a zero-padding position; bottom-up sums establish the interval invariant. A point replacement changes exactly its ancestor intervals. During a query the two pointers delimit the unaccounted range; selected boundary nodes are disjoint and removing them leaves exactly the parent-level remainder. Termination sums precisely the requested interval.

## 9. Pseudocode

```text
build parent[u]=parent[2u]+parent[2u+1] bottom-up
set(i,value): replace leaf; recompute ancestors
l+=base; r+=base; total=0
while l<r:
    if l is right child: total+=tree[l]; l++
    if r is right boundary: --r; total+=tree[r]
    l//=2; r//=2
```

## 10. Dry Run

The initial sum of positions [1,4) is -1+3+2=4. Replacing -1 by 4 (Fenwick delta +5) changes the whole-array sum from 6 to 11. Any [i,i) sum is zero.

## 11. Time Complexity

O(n) construction and O(log(n+1)) update/query time; empty-range queries are valid. The executable adds O(q) output cost.

## 12. Space Complexity

O(n) storage for fewer than 4*max(1,n) complete-tree slots. O(1) auxiliary query/update state.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). The class copies values, uses plain integer arrays and performs genuine leaf/ancestor tree updates and canonical-interval queries. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. Owned vectors store a power-of-two complete segment hierarchy, with no recursively owned nodes. There are no iterators/pointers invalidated by updates. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"values":[2,-1,3,2],"operations":[[1,1,4],[0,1,4],[1,0,4],[1,2,2]]}
```
C++ text input:
```text
4 2 -1 3 2 4 1 1 4 0 1 4 1 0 4 1 2 2
```
Grammar: n, n values, q; operations 0 index replacement or 1 left right. Update acknowledgements are null.

Both output:
```json
[4,null,11,0]
```
All points stay within ±10^9, so every aggregate and range sum has magnitude at most 10000*10^9=10^13. Signed C++ 64-bit arithmetic is safe, including delta validation before mutation. Empty arrays support only the [0,0) query (and prefix end 0 for Fenwick).

## 16. Edge Cases

Negative values, duplicates, empty arrays/ranges, first/last indices and inclusive/exclusive boundary errors are tested. Resource/type failures and updates that would exceed the point bound preserve previous sums.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. 84 seed-8303 array streams execute 35 assignment rounds with random range, prefix and full-range checks after every mutation. Naive Python sums supply expected values. Bounded 10000-element tests reach sums ±10^13 and verify rejected updates preserve state. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Explicit binary aggregate hierarchy, useful as a foundation for other associative operations.

## 18. Disadvantages and Limitations

More storage than Fenwick; only sum with point assignment is supported. Lazy propagation is a separate extension, not a placeholder feature here.

## 19. When to Use It

Use for many point changes and range sums on an indexed array or static Euler order.

## 20. When Not to Use It

Use direct sums for tiny/one-shot inputs; use a fully implemented lazy structure for range updates rather than assuming this API supports them.

## 21. Comparison With Related Algorithms

Fenwick add and Segment set have different mutation contracts. Tests convert the same assignment stream into equivalent deltas and compare both against a naive array after each change.

[fenwick-tree](../fenwick-tree/README.md), [euler-tour](../euler-tour/README.md)

## 22. Interview Questions

Why is the external interval half-open? Which blocks contain a changed point? How do the numeric bounds prevent overflow?

## 23. Practice Problems

Flatten a rooted tree and answer subtree sums; compare every prefix after random assignments; test updates across both numeric extremes.

## 24. References

[Competitive Programmer’s Handbook, Range Queries chapter](https://cses.fi/book/book.pdf). The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
