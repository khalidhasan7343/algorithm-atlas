# Coin Change

## 1. Algorithm Name

Coin Change

## 2. Overview

The catalog names two formulations: minimum number of coins and number of unordered combinations. Both are implemented as separately named APIs on the same unbounded-denomination contract; the CLI returns [minimum,combinations].

## 3. Problem Statement

Coins are positive integers in 1..10^9, with at most 1000 supplied entries. Duplicate denominations are collapsed and input order is irrelevant. Amount A is in 0..10000; supplied_count·(A+1)≤2000000. Any denomination may be used repeatedly. Minimum returns None/null when unreachable; counting returns zero. Amount zero has minimum zero and exactly one combination, the empty multiset.

## 4. Why Do We Need This Algorithm?

Greedy largest-first fails for denominations such as 1,3,4 at amount 6: 4+1+1 uses three coins, while 3+3 uses two. Counting also requires a state order that avoids treating reordered copies as different combinations.

## 5. Real-World Applications

Minimum coins models exact change with unlimited inventory. Combination counts measure distinct denomination allocations for a small integral total. Real limited inventories need another formulation.

## 6. Core Intuition

Minimum state M(a) asks for the fewest coins totaling a. Its last coin can be any feasible denomination. Counting state W(k,a) asks for combinations using only the first k distinct denominations, so coin order cannot create duplicate counts.

## 7. Prerequisites

Minimization, integer arrays, reachable/unreachable sentinels and nested loops. [0/1 Knapsack](../zero-one-knapsack/README.md) clarifies why once-only choices use a different update direction.

## 8. Step-by-Step Working Process

M(0)=0; unreachable positive amounts start at A+1. For a>0, M(a)=min(1+M(a-c)) over c≤a, with unreachable states ignored by the sentinel. Removing the last coin yields a smaller amount; induction proves the minimum.

For counting, W(0,0)=1 and W(0,a>0)=0. W(k,a)=W(k-1,a)+W(k,a-c_k) when a≥c_k. The first term excludes the denomination; removing one copy from the second case is a bijection to the smaller amount. These cases are disjoint. Use denominations outside, amounts increasing inside. Memoization could cache these same states; tabulation avoids recursive depth. One amount row suffices for each API.

## 9. Pseudocode

```text
M ← [0, infinity, ..., infinity]
for a ← 1..A:
    for c in distinct coins with c ≤ a: M[a] ← min(M[a], 1+M[a-c])
W ← [1,0,...,0]
for c in distinct coins:
    for a ← c..A: W[a] ← checked_add(W[a],W[a-c])
return M[A] (or null), W[A]
```

## 10. Dry Run

For coins 1,3,4 and A=6:

| Amount | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| minimum | 0 | 1 | 2 | 1 | 1 | 2 | 2 |
| ways after coin 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| ways after coin 3 | 1 | 1 | 1 | 2 | 2 | 2 | 3 |
| ways after coin 4 | 1 | 1 | 1 | 2 | 3 | 3 | 4 |

Amount 6 combinations are six 1s, three 1s plus 3, two 3s, and two 1s plus 4. Reordering the same coins does not add combinations.

## 11. Time Complexity

Let n be supplied count and k distinct count. Sorting/deduplication costs O(n log(n+1)); DP worst time is O(kA+A+1) for each API. Minimum visits all coin checks for every positive amount. Counting skips denominations larger than A, so may take O(A+k) recurrence work in that case. Numeric A makes the bound pseudo-polynomial.

## 12. Space Complexity

O(A+k+1) auxiliary words including deduplicated denominations, with scalar output and no recursion. A two-dimensional count table uses O(kA) storage; the implemented increasing update saves the denomination dimension. Returning both answers in the CLI evaluates the two APIs separately.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `minimum_coins(coins, amount) / count_combinations(coins, amount)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `minimum_coins(coins, amount) / count_combinations(coins, amount)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **amount, denomination count, then denominations**. Numeric tokens are ASCII signed decimal integers; counts must match exactly and trailing tokens are rejected. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' '6 3 1 3 4' | .venv/bin/python dsa/dynamic-programming/coin-change/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/coin-change/cpp/solution.cpp -o /tmp/atlas-coin-change
printf '%s\n' '6 3 1 3 4' | /tmp/atlas-coin-change
```

Both print:

```text
[2,4]
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/coin-change --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

No denominations at amount zero gives [0,1]; at a positive amount it gives [null,0]. [2] cannot make 3. [1,2,2] counts like [1,2]. Zero/negative denominations are rejected, preventing nonterminating or undefined unlimited-copy interpretations. Tests enumerate multiplicities independently, rather than repeating either DP.

## 17. Advantages

The two objectives have explicit names and outputs. Duplicate normalization prevents accidental double counting. Checked additions give exact results or an explicit error.

## 18. Disadvantages and Limitations

Minimum values are at most A. Combination counts grow rapidly: both languages raise on any counting-table addition above 2^63-1, even if that intermediate amount is not the final request. Python deliberately shares this limit. No modular, arbitrary-precision, bounded-inventory, or ordered-permutation mode is implied.

## 19. When to Use It

Use when coins are reusable and the requested total satisfies the table budget. Choose the API by whether the question asks for optimal size or number of allocations.

## 20. When Not to Use It

Use a different DP for limited coin inventories or ordered sequences. Avoid a dense amount table for huge totals with sparse reachability.

## 21. Comparison With Related Algorithms

| Objective | State/evaluation order | Result at unreachable positive total |
| --- | --- | --- |
| Minimum coins | amount outside | null |
| Unordered combinations | denomination outside | 0 |
| Ordered permutations | amount outside, count sums | 0, but a different question |
| Greedy change | descending denomination | not generally optimal |

## 22. Interview Questions

Why is there one empty combination? How does exchanging the counting loops change the problem? Why must denomination zero be rejected? Can duplicates be treated as distinct coin types without changing meaning?

## 23. Practice Problems

Compare greedy and minimum DP on 1,3,4. Enumerate multiplicity vectors for a small total and match the count. As a separate variant, add finite denomination inventories and explain the additional state.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
