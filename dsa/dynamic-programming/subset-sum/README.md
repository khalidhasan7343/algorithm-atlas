# Subset Sum (Dynamic Programming)

## 1. Algorithm Name

Subset Sum (Dynamic Programming)

## 2. Overview

Decide whether a positional subset sums exactly to a nonnegative target. Boolean tabulation uses each input element at most once and returns existence only.

## 3. Problem Statement

Accept n≤1000 integers in 0..10^9 and target T in 0..10000, with n(T+1)≤2000000. Negative values and targets are rejected. The empty subset is allowed, so target zero always succeeds after validation. Duplicates represent different selectable positions. Return bool, not selected indices or the number of solutions.

## 4. Why Do We Need This Algorithm?

Enumerating every subset is exponential in n. For a modest integral target, many different partial subsets share the same sum, so a Boolean reachability state can merge them.

## 5. Real-World Applications

Small exact budget selection and integer reconciliation can use this model when choices are independent and nonnegative. Signed accounting balances require another state domain, such as the separate backtracking implementation.

## 6. Core Intuition

Let R(i,t) mean that some subset of the first i positions sums to t. Either the newest position is omitted or it is used once with a previously reachable remainder.

## 7. Prerequisites

Subsets, Boolean OR, integer indexing and descending loops. Compare [0/1 Knapsack](../zero-one-knapsack/README.md) and the distinct [signed backtracking variant](../../recursion-and-backtracking/subset-sum-backtracking/README.md).

## 8. Step-by-Step Working Process

Base R(0,0)=true and R(0,t>0)=false. For value v, R(i,t)=R(i-1,t) OR R(i-1,t-v) when t≥v; otherwise retain omission. Update t downward so the remainder belongs to the previous item layer. Zero values read the same cell once and do not change existence. Any valid subset either contains the newest position or does not, and both transitions construct valid subsets, proving correctness by induction over items.

Memoization could cache (i,t) with recursive inclusion/exclusion. Tabulation retains only the previous item layer. A descending one-dimensional row is the implemented space optimization; ascending updates would permit repeatedly using a position.

## 9. Pseudocode

```text
reachable[0] ← true; reachable[1..T] ← false
for value in values:
    for t ← T down through value:
        reachable[t] ← reachable[t] OR reachable[t-value]
return reachable[T]
```

## 10. Dry Run

For values [2,3,2] and T=4:

| Processed values / total | 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- | --- |
| none | true | false | false | false | false |
| first 2 | true | false | true | false | false |
| plus 3 | true | false | true | true | false |
| second 2 | true | false | true | true | true |

The final 4 uses both distinct 2 positions. With just [2], total 4 remains false; descending traversal prevents accidental unlimited reuse.

## 11. Time Complexity

Validation takes O(n), initialization O(T+1), and updates at most O(n(T+1)). Worst total time is O(nT+n+T+1). Values larger than T perform no updates, giving O(n+T+1) in that case. This bound is pseudo-polynomial in numeric target. No input-order average is assumed.

## 12. Space Complexity

O(T+1) Boolean cells and O(1) output, no recursive stack. Python stores Boolean references; C++ vector<bool> packs bits. Both are O(T) logical state storage. A full item/target table would require O(nT), while a separately designed bitset implementation could batch word operations.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `subset_sum(values, target)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `subset_sum(values, target)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **target, count, then integer values**. Numeric tokens are ASCII signed decimal integers; counts must match exactly and trailing tokens are rejected. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' '9 6 3 34 4 12 5 2' | .venv/bin/python dsa/dynamic-programming/subset-sum/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/subset-sum/cpp/solution.cpp -o /tmp/atlas-subset-sum
printf '%s\n' '9 6 3 34 4 12 5 2' | /tmp/atlas-subset-sum
```

Both print:

```text
true
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/subset-sum --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Empty input succeeds only for target zero. Zeros do not create additional reachable totals. Duplicates can be used once per position. A negative number is rejected even when target is zero, because validation precedes the base result. Exhaustive binary selection vectors independently verify small arrays and targets.

## 17. Advantages

The once-only rule is explicit in update order. Work depends on the target rather than all possible positional subsets, and no witness ordering policy is needed.

## 18. Disadvantages and Limitations

Only nonnegative values are supported. Resource caps are enforced before allocation. Values are compared against the target, not summed into potentially overflowing totals, so values up to 10^9 remain safe; table indices are at most 10000. The API cannot supply a subset witness or count solutions.

## 19. When to Use It

Use for Boolean existence when the target is modest and nonnegative, even if n is too large for exhaustive subsets.

## 20. When Not to Use It

Use the existing signed backtracking topic for small signed instances, meet-in-the-middle for small n and huge values, or a signed-offset DP with a separately justified range. Do not silently discard negative values.

## 21. Comparison With Related Algorithms

| Method | Numeric assumptions | Main cost |
| --- | --- | --- |
| This DP | nonnegative, modest target | O(nT) worst |
| Backtracking | signed values supported | exponential search |
| Meet-in-the-middle | large target, small n | O(2^(n/2)) subsets |
| 0/1 Knapsack | weights plus values | maximization instead of existence |

## 22. Interview Questions

Why must total decrease? What does target zero mean? Why do duplicate values remain separate choices? Why is O(nT) not polynomial in the binary input length?

## 23. Practice Problems

Find a counterexample to ascending updates. Add an index witness with validated reconstruction. Then design a signed-offset variant and derive its resource bound before implementing it.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
