# Longest Common Subsequence (LCS)

## 1. Algorithm Name

Longest Common Subsequence (LCS)

## 2. Overview

Find the length of a longest order-preserving subsequence shared by two strings. Characters may be skipped, so this is different from a longest common substring.

## 3. Problem Statement

Return a length only, without reconstructing a sequence. Each string contains at most 1000 Unicode scalar values. Python strings containing lone surrogate code points are rejected; C++ accepts strict UTF-8 and decodes it before comparisons. No normalization, case folding, byte matching, or grapheme segmentation is performed. Empty strings are valid.

## 4. Why Do We Need This Algorithm?

Independent skips allow two sequences to share structure despite intervening insertions. Enumerating every subsequence is exponential; a pair of prefix lengths summarizes all relevant remaining choices.

## 5. Real-World Applications

LCS provides a sequence-similarity building block for comparing revisions or symbol sequences. Full diff tools add reconstruction, formatting and often different performance heuristics; this API returns only the mathematical length.

## 6. Core Intuition

Let D(i,j) be the LCS length of first[:i] and second[:j]. Matching final symbols can extend a common subsequence; otherwise one final symbol must be skipped from at least one side.

## 7. Prerequisites

Strings, prefix indexing, max, nested loops and induction on prefix size. See [Edit Distance](../edit-distance/README.md) for a related prefix-pair state with different transitions.

## 8. Step-by-Step Working Process

Base D(0,j)=D(i,0)=0. If a[i-1]=b[j-1], D(i,j)=D(i-1,j-1)+1. Otherwise D(i,j)=max(D(i-1,j),D(i,j-1)). For equal final symbols an optimum can match the final pair, with an optimal common prefix; for unequal symbols, a common subsequence cannot end at both unmatched positions. These exhaustive cases reduce prefix sizes, proving correctness by induction.

The implementation makes the shorter string the column dimension, then retains previous/current rows. Each current cell reads the previous diagonal, previous above, and current left. Memoization would cache the same (i,j) states with recursion; tabulation removes stack depth. Rolling rows save table storage but discard the path needed for reconstruction.

## 9. Pseudocode

```text
choose shorter string as b
previous[0..len(b)] ← 0
for symbol x in a:
    current[0] ← 0
    for j ← 1..len(b):
        if x = b[j-1]: current[j] ← previous[j-1]+1
        else: current[j] ← max(previous[j],current[j-1])
    previous ← current
return previous[len(b)]
```

## 10. Dry Run

For a="abc", b="ac":

| a prefix / b prefix | empty | a | ac |
| --- | --- | --- | --- |
| empty | 0 | 0 | 0 |
| a | 0 | 1 | 1 |
| ab | 0 | 1 | 1 |
| abc | 0 | 1 | 2 |

At (3,2), final c matches c, so the diagonal value 1 becomes 2. The subsequence "ac" is noncontiguous in "abc", which rules out a substring interpretation.

## 11. Time Complexity

Let n,m be scalar-value counts and B UTF-8 byte count in C++. Validation/decoding is O(n+m) or O(B). DP performs Θ(nm) cell updates; including empty cases and row initialization, total time is O(nm+n+m+1). All arrangements of the same lengths visit the same table cells. Values are at most min(n,m)≤1000, so fixed-word arithmetic is safe.

## 12. Space Complexity

DP workspace is O(min(n,m)+1) words, with O(1) result and no recursion. Python reuses the original immutable strings. C++ additionally stores both decoded scalar arrays, so its total auxiliary storage is O(n+m+1), not just the rolling-row bound. Full tabulation or memoization uses O(nm) cells.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `lcs_length(first, second)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `lcs_length(first, second)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **exactly two text lines**. Text is strict UTF-8 with no normalization; LF separates lines and CRLF is accepted. A final LF is optional when the last line is nonempty. Missing or extra lines are rejected. Embedded line breaks require the API instead of the CLI. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' 'abc
ac' | .venv/bin/python dsa/dynamic-programming/longest-common-subsequence/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/longest-common-subsequence/cpp/solution.cpp -o /tmp/atlas-longest-common-subsequence
printf '%s\n' 'abc
ac' | /tmp/atlas-longest-common-subsequence
```

Both print:

```text
2
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/longest-common-subsequence --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Either empty string gives zero. Repeated symbols are matched in order and at most once per input position. "a😀ব" and "😀ব" have length 2. Precomposed "é" and decomposed "é" do not match because normalization is outside the contract. Tests intersect independently enumerated subsequence sets for exhaustive binary words and seeded Unicode cases; malformed UTF-8 and length 1001 are rejected.

## 17. Advantages

Exact length, compact DP storage, explicit Unicode behavior, and no arbitrary tie-breaking exposed through the API.

## 18. Disadvantages and Limitations

Quadratic work can be expensive for long text; the 1000-scalar cap bounds it to one million DP cells. No actual common sequence or edit script is returned. Equal-length optimal subsequences can differ, so reconstruction would need an explicit deterministic policy.

## 19. When to Use It

Use for small exact sequence similarity when skips are allowed and the length itself answers the question.

## 20. When Not to Use It

Use a substring algorithm for contiguous matching, edit distance for substitution costs, or a specialized diff implementation for large documents and edit scripts.

## 21. Comparison With Related Algorithms

| Problem | Allows skips | Returned objective |
| --- | --- | --- |
| LCS | yes, either input | maximum matched length |
| Common substring | no gaps inside match | maximum contiguous length |
| Levenshtein | edits with costs | minimum edit count |
| Hirschberg LCS | yes | reconstruction with linear table workspace |

## 22. Interview Questions

Why are both prefix indices necessary? What distinguishes a substring recurrence? Why can rolling rows lose reconstruction information? How do code points differ from UTF-8 bytes and user-visible characters?

## 23. Practice Problems

Manually fill the table for repeated letters. Add reconstruction using a full table with a stated tie rule. Then investigate divide-and-conquer reconstruction and validate its output as a subsequence of both strings.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
