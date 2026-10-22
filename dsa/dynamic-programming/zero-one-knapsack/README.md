# 0/1 Knapsack

## 1. Algorithm Name

0/1 Knapsack

## 2. Overview

Select a subset of indivisible items to maximize total value within a capacity. A descending one-dimensional table enforces at most one use per input position.

## 3. Problem Statement

Return maximum value only, with empty selection allowed. weights and values have equal lengths n≤1000; capacity C is in 0..10000 and n(C+1)≤2000000. Weights are integers in 0..10^9; values are in [-10^9,10^9]. Negative values are valid and may be omitted. Duplicate weights represent distinct items. Zero weights are valid.

## 4. Why Do We Need This Algorithm?

A locally attractive item can block a better combination, so value/weight sorting is not a correctness argument for indivisible choices. A capacity state remembers the information needed to combine choices globally.

## 5. Real-World Applications

Budgeted project selection and small integral cargo planning fit this model when each choice is independent and binary. Additional dependencies or multiple constraints require a richer state.

## 6. Core Intuition

Let D(i,c) be the best value using the first i items and weight at most c. Either omit item i or include it once. The previous item layer, not the current layer, must supply the included remainder.

## 7. Prerequisites

Arrays, subsets, max, descending loops, and induction over items. Compare [Subset Sum](../subset-sum/README.md) for a Boolean version of similar capacity states.

## 8. Step-by-Step Working Process

Base D(0,c)=0. For item (w,v), D(i,c)=max(D(i-1,c),D(i-1,c-w)+v) when w≤c; otherwise copy the omission state. Update c from C down to w. For w>0, smaller cells still belong to the previous layer. For w=0, each cell is read and written once, so a positive zero-weight value is added once, including at capacity zero. An optimal subset either contains the current item or does not; the two exhaustive cases and induction prove optimality.

Memoization uses states (i,c) and a recursion stack. Tabulation visits items in increasing order. Rolling a single capacity row saves the item dimension; ascending capacities would instead allow repeated use.

## 9. Pseudocode

```text
best[0..C] ← 0
for each (weight,value):
    for c ← C down through weight:
        best[c] ← max(best[c], best[c-weight]+value)
return best[C]
```

## 10. Dry Run

Items (2,3),(3,4),(4,5), capacity 5:

| Processed items / capacity | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- | --- |
| none | 0 | 0 | 0 | 0 | 0 | 0 |
| (2,3) | 0 | 0 | 3 | 3 | 3 | 3 |
| plus (3,4) | 0 | 0 | 3 | 4 | 4 | 7 |
| plus (4,5) | 0 | 0 | 3 | 4 | 5 | 7 |

The optimum 7 includes the first two items. The API returns 7, not their indices.

## 11. Time Complexity

Validation costs O(n); table initialization costs Θ(C+1). The recurrence work is at most O(n(C+1)), with no input-order benefit in the worst case. Items heavier than C perform no updates, so the best case is O(n+C+1). This is pseudo-polynomial in numeric capacity, not polynomial in its bit length.

## 12. Space Complexity

O(C+1) auxiliary words and O(1) scalar output; no recursive frames. The input occupies O(n). A full predecessor/item table would cost O(n(C+1)) and is unnecessary for a value-only answer. Reconstructing a selection needs additional bookkeeping or recomputation.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `knapsack(weights, values, capacity)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `knapsack(weights, values, capacity)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **capacity, item count, then weight/value pairs**. Numeric tokens are ASCII signed decimal integers; counts must match exactly and trailing tokens are rejected. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' '5 3 2 3 3 4 4 5' | .venv/bin/python dsa/dynamic-programming/zero-one-knapsack/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/zero-one-knapsack/cpp/solution.cpp -o /tmp/atlas-zero-one-knapsack
printf '%s\n' '5 3 2 3 3 4 4 5' | /tmp/atlas-zero-one-knapsack
```

Both print:

```text
7
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/zero-one-knapsack --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Empty input returns 0 for any allowed capacity. Capacity zero still admits positive zero-weight items. Negative-valued items are skipped naturally. A single item of weight 1 and value 5 at capacity 2 returns 5, guarding against the unbounded-update defect. Exhaustive positional-subset oracles check randomized small instances.

## 17. Advantages

Handles duplicate weights and zero weights without special optimization rules. Negative values have a clear omission interpretation. The table is compact compared with storing every item layer.

## 18. Disadvantages and Limitations

Capacity and work limits are part of the API and are checked before allocation. Values sum to at most 1000·10^9=10^12, so signed-64 additions are safe. This API does not return chosen items or solve fractional/unbounded/multidimensional variants.

## 19. When to Use It

Use when choices are binary, weights are nonnegative integers, and the capacity state is affordable.

## 20. When Not to Use It

Use fractional knapsack only when items are divisible. For huge capacities with small total value, consider value-indexed DP; for small n, meet-in-the-middle may be preferable.

## 21. Comparison With Related Algorithms

| Method | Choice model | Key difference |
| --- | --- | --- |
| This 0/1 DP | each position once | descending capacities |
| Unbounded DP | unlimited copies | ascending capacities |
| Fractional greedy | divisible items | ratio ordering can be valid |
| Exhaustive subsets | binary | exponential in n |

## 22. Interview Questions

Why does descending order matter? What changes for weight zero? Why is initialization with zero correct when values can be negative? Can the final row reconstruct every chosen item?

## 23. Practice Problems

Trace a zero-weight example by hand. Add a deterministic selected-index output with a full predecessor table. Then compare capacity-indexed and value-indexed formulations on the same exhaustive small oracle.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
