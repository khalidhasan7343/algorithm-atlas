# Palindrome Partitioning (Minimum Cuts)

## 1. Algorithm Name

Palindrome Partitioning (Minimum Cuts)

## 2. Overview

Compute the minimum number of cuts needed to split a string into palindromic pieces. This optimization contract resolves the catalog objective explicitly; it does not enumerate all partitions.

## 3. Problem Statement

For a string of at most 1000 Unicode scalar values, return minimum cuts between adjacent positions so every piece is a nonempty palindrome. Empty text returns 0 cuts by convention. Python rejects surrogate code points; C++ decodes strict UTF-8. Symbol equality uses scalar values without normalization, case folding or grapheme segmentation.

## 4. Why Do We Need This Algorithm?

Choosing the longest palindromic prefix greedily need not leave the easiest suffix. A prefix optimum must consider every possible final palindromic piece. Preprocessing palindrome membership avoids rescanning substrings inside that DP.

## 5. Real-World Applications

Palindrome segmentation is a useful model for partitioning a symbolic sequence under a local segment constraint. It also teaches how an interval preprocessing table can support a separate prefix optimization.

## 6. Core Intuition

First mark P(l,r), whether text[l..r] is a palindrome. Then let Q(e) be the minimum number of palindromic pieces covering the prefix text[:e]. Guess where the last piece starts.

## 7. Prerequisites

String indexing, inclusive intervals, minimum, induction and partition boundaries. [LCS](../longest-common-subsequence/README.md) is a subsequence problem; palindrome pieces here must be contiguous.

## 8. Step-by-Step Working Process

P(l,r) is true exactly when the endpoint symbols agree and either r-l<2 or P(l+1,r-1) is true. Process l decreasing so inner intervals are already known. This criterion is correct by removing matching endpoints.

Set Q(0)=0. For e>0, Q(e)=min(Q(s)+1) over 0≤s<e where P(s,e-1). A final piece has one such start s, and optimal replacement of its prefix proves optimal substructure. Every transition forms a valid partition; induction over e proves the minimum. Return Q(n)-1 for n>0 and zero for n=0. Single symbols ensure reachability. Memoization could cache the same interval/prefix states; bottom-up tables avoid stack depth. A separate center-expansion formulation can reduce storage, but this implementation retains the full palindrome table.

## 9. Pseudocode

```text
for l ← n-1 down through 0:
    for r ← l..n-1:
        P[l,r] ← text[l]=text[r] AND (r-l<2 OR P[l+1,r-1])
Q[0] ← 0; Q[1..n] ← infinity
for e ← 1..n:
    for s ← 0..e-1:
        if P[s,e-1]: Q[e] ← min(Q[e],Q[s]+1)
return 0 if n=0 else Q[n]-1
```

## 10. Dry Run

For "aab", the palindrome table and prefix costs are:

| l / r | 0 (a) | 1 (a) | 2 (b) |
| --- | --- | --- | --- |
| 0 | true | true | false |
| 1 | — | true | false |
| 2 | — | — | true |

| Prefix length e | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Minimum pieces Q(e) | 0 | 1 | 1 | 2 |
| Minimum cuts | 0 | 0 | 0 | 1 |

For e=3, final piece "b" follows the optimal prefix piece "aa", giving two pieces and one cut: aa|b.

## 11. Time Complexity

With n scalars, both palindrome preprocessing and prefix optimization visit Θ(n²) candidate cells for nonempty n. Total time is Θ(n²+n+1), including validation and base cases. C++ strict UTF-8 decoding adds O(B), with B≤4n. Character arrangement changes which minima update, not the quadratic loop counts.

## 12. Space Complexity

O(n²+n+1) auxiliary storage: palindrome membership plus prefix piece counts. C++ also stores n decoded scalars; Python uses the original string. No recursive stack and only O(1) result. Center expansion with a carefully ordered prefix DP is a different O(n)-space approach; two rolling palindrome rows alone do not supply every later prefix query.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `minimum_palindrome_cuts(text)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `minimum_palindrome_cuts(text)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **exactly one text line; LF alone denotes the empty string**. Text is strict UTF-8 with no normalization; LF separates lines and CRLF is accepted. A final LF is optional when the last line is nonempty. Missing or extra lines are rejected. Embedded line breaks require the API instead of the CLI. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' 'aab' | .venv/bin/python dsa/dynamic-programming/palindrome-partitioning/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/palindrome-partitioning/cpp/solution.cpp -o /tmp/atlas-palindrome-partitioning
printf '%s\n' 'aab' | /tmp/atlas-palindrome-partitioning
```

Both print:

```text
1
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/palindrome-partitioning --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Empty text returns 0. Any singleton or whole-string palindrome returns 0. All distinct symbols need n-1 cuts. Repeated symbols, odd/even palindromes and Unicode symbols are supported. "😀ব😀" is one palindrome. Exhaustive cut masks with direct reversal checks provide independent expected values, including all binary words through length 7.

## 17. Advantages

Palindrome checks become O(1) during prefix optimization. The objective and empty convention are explicit, and no exponential result collection is built.

## 18. Disadvantages and Limitations

The 1000-scalar limit bounds the quadratic table. Result and piece counts are at most 1000, so signed-64 arithmetic is safe. No actual partition, deterministic witness tie policy, all-partition enumeration or grapheme-aware segmentation is provided.

## 19. When to Use It

Use when the question asks for the minimum number of cuts and quadratic storage is affordable.

## 20. When Not to Use It

Use a separate backtracking enumeration contract for all valid partitions. Use longest-palindromic-substring algorithms when only one segment is sought; they do not solve this minimum-cut objective.

## 21. Comparison With Related Algorithms

| Problem/method | Goal | Cost distinction |
| --- | --- | --- |
| Implemented two-stage DP | minimum cuts | O(n²) time/space |
| Enumerate cut masks | all feasible splits | exponential |
| Longest palindromic substring | longest single segment | different objective |
| Center-expansion cut DP | minimum cuts | can reduce space with different evaluation order |

## 22. Interview Questions

Why do pieces and cuts differ by one? Why is empty text handled separately? Why does the interval table run left endpoints backward? Can greedily taking the longest prefix be justified?

## 23. Practice Problems

Enumerate every cut mask for a short word and compare minimum cuts. Add a deterministic partition witness with a stated tie rule. Then design a linear-space center-expansion approach and verify it against the exhaustive oracle.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
