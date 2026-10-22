# Rod Cutting

## 1. Algorithm Name

Rod Cutting

## 2. Overview

Maximize revenue by partitioning an integral rod into priced lengths. This exact-fill unbounded DP supports missing prices and negative prices without inventing free disposal.

## 3. Problem Statement

prices[i] prices a piece of length i+1; None/null marks an unavailable length. Entries beyond the table are unavailable too. A cut length may be used repeatedly. Return maximum total revenue for pieces exactly summing to length L, or None/null if impossible. L is in 0..10000, k≤1000, k(L+1)≤2000000; available prices are integers in [-10^9,10^9].

## 4. Why Do We Need This Algorithm?

The price of the intact rod need not dominate smaller pieces. Greedy unit price can leave an unfillable remainder, so the remaining length must be part of the state.

## 5. Real-World Applications

Small one-dimensional material splitting with integral lengths can use this model if cut waste and cutting fees are absent. Industrial cutting stock usually adds inventory, kerf, or multiple requested lengths and needs a richer model.

## 6. Core Intuition

Let R(t) be the best revenue from exactly t units. Guess the first available piece, then solve its remaining length. The remainder is independent because the price table allows unlimited copies.

## 7. Prerequisites

Unbounded choice, optional values to represent impossibility, and induction on remaining length. [Coin Change](../coin-change/README.md) uses a related exact-total state with different objectives.

## 8. Step-by-Step Working Process

R(0)=0; positive lengths start unreachable. For every t increasing, compute R(t)=max(p_c+R(t-c)) over available c≤t with reachable remainder. A feasible partition has some first piece c, and replacing its remainder by a better feasible remainder cannot hurt revenue. Conversely every transition constructs a valid exact partition. Induction proves optimality and preserves impossibility when no transition exists.

Memoization uses the same remaining-length state and O(L) frames in the worst case. Bottom-up tabulation avoids the stack. A single length array suffices; arbitrary available lengths mean two rolling scalars do not suffice.

## 9. Pseudocode

```text
R[0] ← 0; R[1..L] ← unreachable
for t ← 1..L:
    for available length c ≤ t:
        if R[t-c] reachable:
            R[t] ← max_reachable(R[t], price[c]+R[t-c])
return R[L]
```

## 10. Dry Run

For prices [2,5,7,8] and rod length 4:

| t | 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- | --- |
| R(t) | 0 | 2 | 5 | 7 | 10 |
| one optimal first piece | — | 1 | 2 | 1 | 2 |

At t=4, candidates are 2+7=9, 5+5=10, 7+2=9, and 8+0=8. The optimum cuts 2+2. With prices [1,1,1,10], leaving the length-4 rod whole is optimal instead.

## 11. Time Complexity

Let k be price-table length and L rod length. Validation costs O(k); initialization O(L+1); recurrence worst work O(kL), giving O(kL+k+L+1). The Python loop checks all k prices per t; C++ stops once cut length exceeds t. No data-distribution average is assumed. L is numeric, so the method is pseudo-polynomial.

## 12. Space Complexity

O(L+1) auxiliary optional integer cells, O(1) result and no recursion stack. Input storage is O(k). A full piece-count table is unnecessary; returning actual cuts would need predecessor lengths. With a bounded maximum available cut, a rolling window is possible, but the implemented array is clearer.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `rod_cutting(prices, length)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `rod_cutting(prices, length)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **rod length, price count k, then p1..pk; x denotes unavailable**. Numeric tokens are ASCII signed decimal integers; counts must match exactly and trailing tokens are rejected. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' '4 4 2 5 7 8' | .venv/bin/python dsa/dynamic-programming/rod-cutting/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/rod-cutting/cpp/solution.cpp -o /tmp/atlas-rod-cutting
printf '%s\n' '4 4 2 5 7 8' | /tmp/atlas-rod-cutting
```

Both print:

```text
10
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/rod-cutting --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Length zero returns 0, even for an empty price table. Empty prices cannot fill positive length. [None,5] fills length 4 for 10 but cannot fill length 3. Price [-2] at length 3 returns -6, because exact fill is mandatory. None is distinct from the valid price zero. Independent exhaustive ordered compositions check small random inputs.

## 17. Advantages

Missing lengths and negative prices have explicit semantics. The recurrence directly models whether the whole rod or several pieces yield the best revenue.

## 18. Disadvantages and Limitations

At most L pieces are used, so revenue magnitude is at most 10000·10^9=10^13; signed-64 arithmetic is safe. Dense table/work caps are enforced. The contract excludes discarded leftovers, cut fees, kerf, fractional lengths, limited stock and reconstruction.

## 19. When to Use It

Use when the full rod must be consumed, all allowed piece lengths have independent prices, and unlimited repeated lengths are acceptable.

## 20. When Not to Use It

Use cutting-stock or other optimization formulations when inventory, waste, multiple rods, or setup costs couple choices. Do not silently return zero for a negative-price exact-fill problem.

## 21. Comparison With Related Algorithms

| Formulation | Goal | Use of a length |
| --- | --- | --- |
| Rod cutting | maximize exact-fill revenue | unlimited |
| 0/1 knapsack | maximize value within capacity | once per position |
| Minimum coins | minimize exact-fill piece count | unlimited |
| Greedy unit price | locally best ratio | not generally correct |

## 22. Interview Questions

Why must unreachable be separate from zero? When can negative prices produce a negative optimum? How would a fixed fee for each actual cut change the recurrence? Why is a once-only capacity update inappropriate?

## 23. Practice Problems

Trace sparse prices that make odd lengths impossible. Add predecessor cut lengths and a deterministic tie policy. Separately model a fee paid for each cut, taking care not to charge for an uncut whole rod.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
