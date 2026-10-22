# Fenwick Tree / Binary Indexed Tree

## 1. Algorithm Name

Fenwick Tree / Binary Indexed Tree

## 2. Overview

Maintain prefix sums using one-based low-bit blocks and logarithmic point additions.

## 3. Problem Statement

Store a mutable array and answer sums over half-open ranges [left,right). Also expose exclusive-end prefix_sum(end) and add(index,delta). Empty ranges return zero.

**API:** `FenwickTree(values).add(i,delta) / .prefix_sum(end) / .range_sum(l,r)`. n≤10000, values in [-10^9,10^9]; zero-based indices and half-open ranges. Deltas lie in [-2*10^9,2*10^9], and the resulting point value must remain within the value bound. Invalid operations reject before changing stored state. solve permits at most 1000 operations.

## 4. Why Do We Need This Algorithm?

Repeated full-array summation costs O(n) per query. A tree of reusable aggregates limits each update/query to logarithmically many blocks.

## 5. Real-World Applications

Dynamic frequency tables, running financial aggregates within stated numeric limits, and subtree sums after Euler flattening.

## 6. Core Intuition

Internal cell i covers the suffix block [i-lowbit(i),i) in external zero-based coordinates. Clearing the lowest set bit moves to the preceding disjoint prefix block.

## 7. Prerequisites

Understand rooted trees, explicit node IDs, parent arrays, depths and binary representations. See the [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Copy validated values and construct low-bit blocks in O(n) by forwarding each completed block to i+lowbit(i). For add, validate index/delta/result before mutation, then climb those parent indices. Prefix queries repeatedly clear low bits; range queries subtract two prefixes.

**Correctness and invariants:** Induct on increasing build indices: each forwarded block is complete and belongs to its parent block. A point belongs exactly to cells reached by adding lowbit, so add updates all and only containing aggregates. Prefix clearing partitions [0,end) into disjoint stored blocks; subtracting two prefixes yields [left,right).

## 9. Pseudocode

```text
build: bit[i]+=value[i-1]; bit[i+lowbit(i)]+=bit[i] if parent exists
add(index,delta): for i=index+1 while i<=n: bit[i]+=delta; i+=lowbit(i)
prefix(end): total=0; while end: total+=bit[end]; end-=lowbit(end)
range(l,r)=prefix(r)-prefix(l)
```

## 10. Dry Run

The initial sum of positions [1,4) is -1+3+2=4. Replacing -1 by 4 (Fenwick delta +5) changes the whole-array sum from 6 to 11. Any [i,i) sum is zero.

## 11. Time Complexity

O(n) construction and O(log(n+1)) update/query time; empty-range queries are valid. The executable adds O(q) output cost.

## 12. Space Complexity

O(n) storage for point values and n+1 Fenwick cells. O(1) auxiliary query/update state.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). The class copies values, uses plain integer arrays and performs genuine low-bit parent jumps. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. Owned vectors store one-based Fenwick blocks; unsigned lowbit arithmetic is defined modulo the index type. There are no iterators/pointers invalidated by updates. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"values":[2,-1,3,2],"operations":[[1,0],[2,1,4],[0,1,5],[1,4],[2,2,2]]}
```
C++ text input:
```text
4 2 -1 3 2 5 1 0 2 1 4 0 1 5 1 4 2 2 2
```
Grammar: n, n values, q; operations 0 index delta, 1 end, or 2 left right. Update acknowledgements are null.

Both output:
```json
[0,4,null,11,0]
```
All points stay within ±10^9, so every aggregate and range sum has magnitude at most 10000*10^9=10^13. Signed C++ 64-bit arithmetic is safe, including delta validation before mutation. Empty arrays support only the [0,0) query (and prefix end 0 for Fenwick).

## 16. Edge Cases

Negative values, duplicates, empty arrays/ranges, first/last indices and inclusive/exclusive boundary errors are tested. Resource/type failures and updates that would exceed the point bound preserve previous sums.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. 84 seed-8303 array streams execute 35 assignment rounds with random range, prefix and full-range checks after every mutation. Naive Python sums supply expected values. Bounded 10000-element tests reach sums ±10^13 and verify rejected updates preserve state. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Compact blocks and simple prefix/range-sum logic.

## 18. Disadvantages and Limitations

Range subtraction uses an invertible sum operation; this API is not a general arbitrary monoid or range-update structure.

## 19. When to Use It

Use for many point changes and range sums on an indexed array or static Euler order.

## 20. When Not to Use It

Use direct sums for tiny/one-shot inputs; use a fully implemented lazy structure for range updates rather than assuming this API supports them.

## 21. Comparison With Related Algorithms

Fenwick add and Segment set have different mutation contracts. Tests convert the same assignment stream into equivalent deltas and compare both against a naive array after each change.

[segment-tree](../segment-tree/README.md), [euler-tour](../euler-tour/README.md)

## 22. Interview Questions

Why is the external interval half-open? Which blocks contain a changed point? How do the numeric bounds prevent overflow?

## 23. Practice Problems

Flatten a rooted tree and answer subtree sums; compare every prefix after random assignments; test updates across both numeric extremes.

## 24. References

[Competitive Programmer’s Handbook, Range Queries chapter](https://cses.fi/book/book.pdf). The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
