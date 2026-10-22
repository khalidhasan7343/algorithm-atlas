# Kadane's Algorithm

## 1. Algorithm Name

Kadane's Algorithm

## 2. Overview

Find a maximum-sum contiguous nonempty interval in one linear pass. Kadane is a running-state dynamic program, distinct from the existing recursive Divide & Conquer maximum-subarray algorithm.

## 3. Problem Statement

Return (sum,start,end-exclusive), or None/null for empty input. Maximize sum, then minimize start, then end. Select a nonempty interval for every nonempty input, including all-negative arrays. Support at most 10000 native integers in [-10^9,10^9]. C++ returns optional<Subarray>; the CLI returns [decimal-sum-string,start,end] to match the existing Divide & Conquer output convention.

## 4. Why Do We Need This Algorithm?

Enumerating every interval repeats sums. A useful interval ending now either extends the best interval ending immediately before it or begins at the current value. Only one ending state is needed.

## 5. Real-World Applications

Maximum contiguous gain or deviation can model a best interval in an already ordered numeric series. Financial fees, required interval lengths, circularity and multiple intervals would require additional state or different contracts.

## 6. Core Intuition

Let E(i) be the best nonempty sum ending exactly at index i. E(i)=max(a[i],E(i-1)+a[i]). If the preceding sum is negative, dropping it improves the current result; if it is zero, keeping it preserves the earlier starting index.

## 7. Prerequisites

Arrays, contiguous half-open intervals, max and induction. Compare the [Divide & Conquer implementation](../../divide-and-conquer/maximum-subarray-divide-and-conquer/README.md), which solves left, right and crossing intervals recursively.

## 8. Step-by-Step Working Process

Initialize the best result as absent. For each index, start a new ending interval if this is the first element or the previous ending sum is negative; otherwise extend the previous interval. Record a better global candidate by lexicographic preference (-sum,start,end). The endpoint recurrence considers both exhaustive possibilities for an ending interval; induction proves the best sum, and keeping a zero-sum prefix proves the earliest-start tie. Comparing every endpoint with the global result proves the requested final interval and earliest-end tie.

Memoization of E(i) would use a cache and O(n) stack. Full tabulation stores every endpoint sum. Rolling tabulation retains current sum/start and one global interval, yielding constant auxiliary space.

## 9. Pseudocode

```text
best ← absent; current_sum ← 0; current_start ← 0
for i ← 0..n-1:
    if i=0 OR current_sum<0:
        current_sum ← a[i]; current_start ← i
    else: current_sum ← current_sum+a[i]
    candidate ← (current_sum,current_start,i+1)
    if candidate has better (-sum,start,end) than best: best ← candidate
return best
```

## 10. Dry Run

For [-2,1,-3,4,-1,2,1,-5,4]:

| i | a[i] | E(i) | ending start | global best (sum,start,end) |
| --- | --- | --- | --- | --- |
| 0 | -2 | -2 | 0 | (-2,0,1) |
| 1 | 1 | 1 | 1 | (1,1,2) |
| 2 | -3 | -2 | 1 | (1,1,2) |
| 3 | 4 | 4 | 3 | (4,3,4) |
| 4 | -1 | 3 | 3 | (4,3,4) |
| 5 | 2 | 5 | 3 | (5,3,6) |
| 6 | 1 | 6 | 3 | (6,3,7) |
| 7 | -5 | 1 | 3 | (6,3,7) |
| 8 | 4 | 5 | 3 | (6,3,7) |

Return sum 6 and interval [3,7), containing [4,-1,2,1].

## 11. Time Complexity

Validation and the DP each scan n values once, giving Θ(n+1) time including empty input. Every value order has the same asymptotic work. Each update uses constant fixed-width arithmetic under the shared finite numeric contract.

## 12. Space Complexity

O(1) auxiliary words and O(1) result, with no recursion stack. Input storage is O(n); standalone CLI token/vector allocation is separate from algorithm workspace. Full endpoint tabulation would use O(n), while the existing Divide & Conquer API uses O(log n) recursive frames.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `maximum_subarray(values)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `maximum_subarray(values)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **count followed by integer values**. Numeric tokens are ASCII signed decimal integers; counts must match exactly and trailing tokens are rejected. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' '9 -2 1 -3 4 -1 2 1 -5 4' | .venv/bin/python dsa/dynamic-programming/kadane/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/kadane/cpp/solution.cpp -o /tmp/atlas-kadane
printf '%s\n' '9 -2 1 -3 4 -1 2 1 -5 4' | /tmp/atlas-kadane
```

Both print:

```text
["6",3,7]
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/kadane --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Empty input has no interval and returns None/null. [-3,-1,-2] selects (-1,1,2), rather than an empty zero sum. [0,0,0] selects (0,0,1). [0,1] keeps the zero prefix for earlier start. [1,-1,1] retains (1,0,1), the earliest end among equal-sum/equal-start intervals. Exhaustive small ternary arrays and seeded large-magnitude arrays are checked by independent interval enumeration.

## 17. Advantages

Linear time, constant workspace, explicit nonempty semantics and deterministic ties. The direct recurrence is easy to compare with a slower exhaustive oracle.

## 18. Disadvantages and Limitations

The shared input cap limits sums to magnitude 10000·10^9=10^13, proving signed-64 additions safe. Python deliberately shares the same finite input domain, whereas the prior Divide & Conquer Python API supports arbitrary integers and its C++ API has wider exact totals. Agreement is asserted on their shared domain. This API does not support circular arrays, all optima, length constraints or streaming mutation.

## 19. When to Use It

Use when one maximum contiguous interval is needed from a finite integer array within the documented limits.

## 20. When Not to Use It

Use a different DP for multiple disjoint intervals or length constraints. Use the Divide & Conquer lesson to study its decomposition recurrence or its wider numeric contract. A maximum subsequence that may skip negatives is a different problem.

## 21. Comparison With Related Algorithms

| Method | Time | Auxiliary space | Technique |
| --- | --- | --- | --- |
| Kadane here | O(n) | O(1) | running endpoint DP |
| Existing Divide & Conquer | O(n log n) | O(log n) | left/right/crossing recursion |
| Enumerate intervals with incremental sums | O(n²) | O(1) | independent small oracle |
| Enumerate and recompute every sum | O(n³) | input-dependent slicing | simple test oracle |

## 22. Interview Questions

Why can a negative prefix be dropped? Why must a zero prefix be retained for the earliest-start tie? Why does initializing a global best to zero break all-negative arrays? How would a length restriction alter the state?

## 23. Practice Problems

Trace every tie case from section 16. Compare Kadane and the existing Divide & Conquer API on random shared-domain inputs. As a separate variant, require at least k elements and prove the extra state before implementing it.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
