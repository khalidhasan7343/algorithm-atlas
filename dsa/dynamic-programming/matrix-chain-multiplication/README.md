# Matrix Chain Multiplication

## 1. Algorithm Name

Matrix Chain Multiplication

## 2. Overview

Find the minimum scalar multiplication count among all parenthesizations of a compatible chain. The algorithm optimizes multiplication order; it does not multiply matrix entries or reorder the matrices.

## 3. Problem Statement

A dimension list [d0,d1,...,dn] represents n matrices Ai of shape di×d(i+1), using zero-based i. Shared adjacent dimensions guarantee compatibility by construction. Return minimum scalar cost only. [] denotes an empty chain and returns 0; length-one dimension lists are invalid; two dimensions describe one matrix and return 0. Allow at most 100 matrices, with each dimension an integer in 1..100000.

## 4. Why Do We Need This Algorithm?

Associativity preserves the matrix product but intermediate shapes can change arithmetic work dramatically. Choosing a cheap-looking adjacent multiplication greedily can force costly later products.

## 5. Real-World Applications

The model supports planning dense matrix product expressions when scalar operation count is a useful cost proxy. Real linear-algebra engines also account for memory, sparsity and hardware; those are outside this scalar model.

## 6. Core Intuition

Let C(i,j) be the least cost to multiply matrices i through j. Any final multiplication splits the chain at some k into contiguous left and right products. Their resulting outer shapes depend only on interval endpoints.

## 7. Prerequisites

Matrix dimension compatibility, associative multiplication, intervals, minima and induction on interval length. [Strassen](../../divide-and-conquer/strassen-matrix-multiplication/README.md) is a different topic: it changes multiplication arithmetic, not chain parenthesization.

## 8. Step-by-Step Working Process

Base C(i,i)=0, since a single matrix needs no multiplication. For i<j, C(i,j)=min over i≤k<j of C(i,k)+C(k+1,j)+d_i·d_(k+1)·d_(j+1). Evaluate intervals by increasing length so every child interval is complete. Any parenthesization has exactly one final split; replacing either subtree with a lower-cost subtree preserves shape and lowers cost. Conversely each split combines valid subproducts. These exhaustive final splits and induction prove the optimum.

Memoization caches intervals recursively. Tabulation visits all intervals explicitly. Unlike a prefix-only recurrence, interval states need many shorter lengths, so two rolling rows do not retain all dependencies.

## 9. Pseudocode

```text
C[i,i] ← 0
for length ← 2..n:
    for i ← 0..n-length:
        j ← i+length-1
        C[i,j] ← infinity
        for k ← i..j-1:
            candidate ← C[i,k]+C[k+1,j]+d[i]*d[k+1]*d[j+1]
            C[i,j] ← min(C[i,j],candidate)
return C[0,n-1], or 0 for no/single matrix
```

## 10. Dry Run

Dimensions [10,30,5,60] describe A0:10×30, A1:30×5, A2:5×60.

| i / j | 0 | 1 | 2 |
| --- | --- | --- | --- |
| 0 | 0 | 1500 | 4500 |
| 1 | — | 0 | 9000 |
| 2 | — | — | 0 |

Split k=0 costs 0+9000+10·30·60=27000. Split k=1 costs 1500+0+10·5·60=4500. Thus (A0A1)A2 is optimal, with scalar cost 4500.

## 11. Time Complexity

For n matrices, O(n²) intervals each try O(n) splits, giving Θ(n³) work for n≥2. The exact split count is n(n-1)(n+1)/6. Input validation is O(n+1). Matrix values do not affect this dimension-only cost model, and no probabilistic average case is needed.

## 12. Space Complexity

O(n²) auxiliary integer cells, O(1) scalar output, and no recursive stack. Input dimensions use O(n). Triangular storage could reduce a constant factor; returning parenthesization would require a split table or recomputation.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `matrix_chain_cost(dimensions)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `matrix_chain_cost(dimensions)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **dimension count followed by dimensions**. Numeric tokens are ASCII signed decimal integers; counts must match exactly and trailing tokens are rejected. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' '4 10 30 5 60' | .venv/bin/python dsa/dynamic-programming/matrix-chain-multiplication/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/matrix-chain-multiplication/cpp/solution.cpp -o /tmp/atlas-matrix-chain-multiplication
printf '%s\n' '4 10 30 5 60' | /tmp/atlas-matrix-chain-multiplication
```

Both print:

```text
4500
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/matrix-chain-multiplication --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Empty [] and one matrix cost zero. A lone dimension does not describe a matrix and is rejected. Zero/negative, noninteger and oversized dimensions are rejected. Independently enumerated full binary parenthesizations verify small random chains, including equal dimensions. Separate boundary tests use 100 matrices of 100000×100000, with exact cost 99·10^15.

## 17. Advantages

Considers every valid multiplication grouping without enumerating exponentially many trees. Shared dimension encoding prevents inconsistent adjacent shapes.

## 18. Disadvantages and Limitations

Cubic runtime motivates the 100-matrix cap. Each scalar product cost is at most 10^15; a candidate tree has at most 99 products, so every intermediate addition is at most 99·10^15 and fits signed 64-bit. Python shares these bounds. Incompatible matrix-pair lists are not accepted: callers must supply the shared dimension-vector representation. No actual product or parenthesization is returned.

## 19. When to Use It

Use when matrix order is fixed, shapes are compatible, and classical scalar multiplication count is the target objective.

## 20. When Not to Use It

Use a different planner for sparse matrices, memory limits, parallel scheduling or hardware-calibrated costs. Do not use this function to multiply matrix values.

## 21. Comparison With Related Algorithms

| Approach | Work in matrix count | Output/role |
| --- | --- | --- |
| Enumerate parenthesizations | Catalan growth | independent small oracle |
| Interval memoization | O(n³) | same optimal scalar cost |
| Implemented tabulation | O(n³) | no recursion |
| Strassen | dimension-dependent arithmetic | computes a matrix product |

## 22. Interview Questions

Why are interval endpoints enough state? Why must subchains remain contiguous? What shape results from an interval regardless of its internal grouping? Why do the numeric caps prevent overflow in every candidate, not just the final minimum?

## 23. Practice Problems

Enumerate both groupings for three matrices. Add a split table and deterministic parenthesization output. Then change the cost model to account for peak intermediate storage and explain why one scalar state may no longer suffice.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
