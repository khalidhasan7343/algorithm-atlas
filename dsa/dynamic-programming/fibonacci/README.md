# Fibonacci

## 1. Algorithm Name

Fibonacci

## 2. Overview

Compute the Fibonacci sequence using two rolling states. This is a space-optimized bottom-up dynamic program, with no recursive calls.

## 3. Problem Statement

For an integer index n, return F(n), where F(0)=0, F(1)=1, and F(n)=F(n-1)+F(n-2) for n≥2. The shared API supports 0≤n≤92. Negative/noninteger indices are invalid; n>92 raises overflow even in Python so the languages agree.

## 4. Why Do We Need This Algorithm?

A naive recursive expansion recalculates the same indices. Saving previous answers reduces exponential repeated work to a linear pass. This small example makes the difference between a recurrence and its evaluation strategy visible.

## 5. Real-World Applications

Fibonacci counts ways to tile a length-(n-1) board with unit squares and dominoes for n≥1. It also models step-counting recurrences and supplies a compact example when teaching dependency graphs.

## 6. Core Intuition

Only the two preceding values affect the next value. A full table is useful for explanation, but it is unnecessary when the API returns a single number. Base states must be handled before advancing the window.

## 7. Prerequisites

Integer addition, loops, simultaneous assignment, and induction. Familiarity with [recursion](../../recursion-and-backtracking/README.md) helps explain repeated recursive subproblems.

## 8. Step-by-Step Working Process

Return zero for n=0. Start previous=F(0), current=F(1). For i=2..n, compute next=previous+current, then advance both states. Before iteration i, the states are F(i-2),F(i-1); the recurrence makes the new pair F(i-1),F(i). Induction proves current=F(n) at termination. No unnecessary F(93) is computed when n=92.

Memoization caches recursive calls using O(n) storage and stack. Full tabulation stores F(0..n). The implemented rolling tabulation keeps only the live dependency window.

## 9. Pseudocode

```text
if n = 0: return 0
previous ← 0; current ← 1
for i ← 2 through n:
    next ← previous + current
    previous ← current
    current ← next
return current
```

## 10. Dry Run

For n=6, the conceptual DP table is:

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F(i) | 0 | 1 | 1 | 2 | 3 | 5 | 8 |

At i=4, (previous,current)=(1,2), so next=3. The final pair is (5,8); return 8. n=0 takes its direct base-case return.

## 11. Time Complexity

With n the index, the generalized operation count is Θ(n) for n≥2 and Θ(1) for n=0,1; input order does not affect it. The implementation caps n at 92, making each addition a bounded-word operation. Removing the numeric cap would require bit-complexity accounting, not merely a claim of O(n) machine time.

## 12. Space Complexity

O(1) auxiliary integer words, O(1) output words and no recursion stack. CLI input token storage is separate from algorithm workspace. Full tabulation/memoization use O(n) words; rolling states are the implemented space optimization.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `fibonacci(n)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `fibonacci(n)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **one index n**. Numeric tokens are ASCII signed decimal integers; counts must match exactly and trailing tokens are rejected. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' '10' | .venv/bin/python dsa/dynamic-programming/fibonacci/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/fibonacci/cpp/solution.cpp -o /tmp/atlas-fibonacci
printf '%s\n' '10' | /tmp/atlas-fibonacci
```

Both print:

```text
55
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/fibonacci --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

F(0)=0 and F(1)=1. F(92)=7540113804746346429 fits signed 64-bit; F(93)=12200160415121876738 does not. Both APIs reject negative indices and reject 93 before arithmetic. Tests cover every allowed index using an independent binomial-sum identity for tilings.

## 17. Advantages

The implementation exposes the recurrence directly, avoids stack depth, and has a fixed memory footprint. Every supported result is exact in both languages.

## 18. Disadvantages and Limitations

The shared API intentionally does not provide arbitrary-precision Fibonacci. Fixed-width C++ overflow must never be treated as wraparound. Two rolling states do not retain all preceding sequence values.

## 19. When to Use It

Use for an exact small-index result and to learn how tabulation eliminates overlapping recursive work.

## 20. When Not to Use It

Use arbitrary-precision fast doubling for very large exact indices, or modular arithmetic when only a remainder is required. Those are separate contracts.

## 21. Comparison With Related Algorithms

| Approach | Work | Auxiliary storage |
| --- | --- | --- |
| Naive recursion | exponential | O(n) frames |
| Memoization | O(n) | O(n) table/frames |
| Full tabulation | O(n) | O(n) table |
| Implemented rolling DP | O(n) | O(1) words |
| Fast doubling | O(log n) arithmetic operations | numeric-dependent |

## 22. Interview Questions

Why do two states suffice? What invariant proves the update? Why can computing one extra state overflow although the requested answer fits? How do arithmetic-operation and bit complexity differ?

## 23. Practice Problems

First print all values through n using a table. Next memoize the recursive version and count calls. Finally implement modular fast doubling as a separately tested variant and compare its state dependencies.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
