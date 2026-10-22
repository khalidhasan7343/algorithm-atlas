# Longest Increasing Subsequence (LIS)

## 1. Algorithm Name

Longest Increasing Subsequence (LIS)

## 2. Overview

Compute the length of a strictly increasing subsequence using O(n²) dynamic programming. Positions remain ordered, but selected positions need not be adjacent.

## 3. Problem Statement

Return a length only. Input contains n≤1000 native integers, each in [-10^9,10^9]. Empty input gives 0. Strictly increasing means each selected value is less than the next; equal values do not extend a sequence. Negative values are fully supported.

## 4. Why Do We Need This Algorithm?

A subsequence ending at one position can be shorter overall yet remain a useful predecessor for another value. Storing the best result ending at every position captures this dependency without enumerating all subsets.

## 5. Real-World Applications

LIS models the longest increasing pattern within an ordered sequence of measurements or rankings. It identifies an ordered trend, not a contiguous run or a statistical significance claim.

## 6. Core Intuition

Let L(i) be the longest valid subsequence ending exactly at position i. Its predecessor, if any, is an earlier position j with a[j]<a[i]. A singleton at i is always valid.

## 7. Prerequisites

Arrays, positional subsequences, strict comparisons, max and induction. [LCS](../longest-common-subsequence/README.md) compares two sequences; LIS constrains values within one sequence.

## 8. Step-by-Step Working Process

Initialize L(i)=1. Scan i from left to right and examine every j<i. If a[j]<a[i], try L(j)+1. Thus L(i)=1+max(L(j)) over feasible predecessors, or 1 if none exist. Every non-singleton increasing subsequence has a feasible final predecessor; taking its best prefix cannot worsen it. Every transition appends a larger value at a later position. Induction proves each L(i), then max_i L(i) is optimal.

Memoization would recursively evaluate predecessor states; iterative tabulation computes them in index order. The implemented table retains all endpoint values because any earlier endpoint can matter later. Two rolling scalars cannot represent them. A different tails-state formulation offers O(n log n) time but is not the implementation here.

## 9. Pseudocode

```text
L[0..n-1] ← 1
for i ← 0..n-1:
    for j ← 0..i-1:
        if a[j] < a[i]: L[i] ← max(L[i],L[j]+1)
return max(L), or 0 when n=0
```

## 10. Dry Run

For [3,1,2,2,4]:

| Position i | 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- | --- |
| Value | 3 | 1 | 2 | 2 | 4 |
| L(i) | 1 | 1 | 2 | 2 | 3 |

The second 2 cannot extend the first 2. Position 4 can extend either length-2 endpoint, yielding length 3, for example [1,2,4].

## 11. Time Complexity

For n values, every pair j<i is compared, exactly n(n-1)/2 comparisons regardless of value ordering. Hence Θ(n²) time for n≥2 and Θ(n+1) for base-sized inputs, including validation/output handling. No O(n log n) claim is made for this code.

## 12. Space Complexity

O(n) auxiliary table words, O(1) result and no recursive stack. The input costs O(n). The O(n log n) tails alternative still uses O(n) worst-case workspace. Returning selected indices requires predecessor information, which this length-only API omits.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `lis_length(values)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `lis_length(values)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **count followed by integer values**. Numeric tokens are ASCII signed decimal integers; counts must match exactly and trailing tokens are rejected. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' '8 10 9 2 5 3 7 101 18' | .venv/bin/python dsa/dynamic-programming/longest-increasing-subsequence/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/longest-increasing-subsequence/cpp/solution.cpp -o /tmp/atlas-longest-increasing-subsequence
printf '%s\n' '8 10 9 2 5 3 7 101 18' | /tmp/atlas-longest-increasing-subsequence
```

Both print:

```text
4
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/longest-increasing-subsequence --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Empty input gives 0; a singleton gives 1. All equal values give 1; strictly descending nonempty input gives 1. [-3,-2,-1] gives 3. Bounds ±10^9 are compared directly and never subtracted, avoiding arithmetic overflow. Independent exhaustive positional-subset tests cover duplicates and negatives.

## 17. Advantages

The endpoint state and proof are straightforward. No binary-search boundary convention is hidden in the implementation, making strictness easy to inspect.

## 18. Disadvantages and Limitations

Quadratic runtime and the 1000-element cap limit practical size. The API does not reconstruct a witness, count optimal subsequences, or solve the non-decreasing variant. DP lengths are at most 1000 and fit signed-64 safely.

## 19. When to Use It

Use for teaching, short inputs, or extensions where endpoint-specific DP states are useful.

## 20. When Not to Use It

Use a correctly specified tails/binary-search algorithm for large length-only inputs. Use a contiguous-run scan if skipped positions are disallowed.

## 21. Comparison With Related Algorithms

| Method | Time | Increasing rule |
| --- | --- | --- |
| Implemented endpoint DP | O(n²) | a[j]<a[i] |
| Tails and lower-bound | O(n log n) | strictly increasing |
| Tails and upper-bound | O(n log n) | non-decreasing |
| Enumerate subsets | O(n·2^n) | direct validation |

## 22. Interview Questions

Why store the optimum ending at each position rather than only the global optimum? How does strictness change duplicate behavior? Why is sorting the input not a valid LIS implementation? What information supports reconstruction?

## 23. Practice Problems

Trace both strictly increasing and non-decreasing answers for repeated values. Add predecessor-index reconstruction. Implement the tails alternative separately and compare both against exhaustive subsets for small arrays.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
