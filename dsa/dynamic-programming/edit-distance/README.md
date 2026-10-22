# Edit Distance (Levenshtein Distance)

## 1. Algorithm Name

Edit Distance (Levenshtein Distance)

## 2. Overview

Compute the minimum number of unit-cost insertions, deletions and substitutions required to transform one string into another. Transposition is not an allowed operation.

## 3. Problem Statement

Return a nonnegative distance only. Insertion, deletion and substitution each cost 1; leaving equal symbols matched costs 0. Inputs each contain at most 1000 Unicode scalar values. C++ decodes strict UTF-8; Python rejects surrogate code points. Normalization, case folding and grapheme segmentation are outside the contract.

## 4. Why Do We Need This Algorithm?

Position-by-position mismatch counts cannot account for inserted or deleted symbols. A pair of prefixes captures how much of each string has been transformed and lets the algorithm choose among alignment possibilities.

## 5. Real-World Applications

Edit distance is a basic similarity measure for typo matching and small symbolic-sequence comparisons. Practical spell checkers often use weighted edits, language models or pruning beyond this unit-cost educational API.

## 6. Core Intuition

Let D(i,j) be the minimum cost to transform first[:i] into second[:j]. The final operation either deletes a source symbol, inserts a target symbol, or matches/substitutes the final pair.

## 7. Prerequisites

Prefix indices, minimum, nested loops and induction. [LCS](../longest-common-subsequence/README.md) uses similar states but maximizes matching length rather than minimizing edit cost.

## 8. Step-by-Step Working Process

Base D(i,0)=i and D(0,j)=j: deleting or inserting all symbols is necessary. Transition D(i,j)=min(D(i-1,j)+1, D(i,j-1)+1, D(i-1,j-1)+[a[i-1]≠b[j-1]]). Any optimal alignment has one of these final steps. Removing it leaves an optimal smaller-prefix problem; conversely each transition constructs a valid alignment. Induction on i+j proves the minimum.

Tabulation starts with row 0 as 0,1,..,m and sets the first cell of row i to i. Previous/current rows suffice because only above, left and diagonal are read. Unit symmetric costs allow swapping inputs to minimize row width. Memoization computes the same states recursively, but adds cache and stack overhead.

## 9. Pseudocode

```text
previous ← [0,1,...,m]
for i ← 1..n:
    current[0] ← i
    for j ← 1..m:
        current[j] ← min(previous[j]+1, current[j-1]+1,
                         previous[j-1] + (a[i-1] ≠ b[j-1]))
    previous ← current
return previous[m]
```

## 10. Dry Run

For "cat" → "cut":

| source prefix / target prefix | empty | c | cu | cut |
| --- | --- | --- | --- | --- |
| empty | 0 | 1 | 2 | 3 |
| c | 1 | 0 | 1 | 2 |
| ca | 2 | 1 | 1 | 2 |
| cat | 3 | 2 | 2 | 1 |

The optimum substitutes a→u once. For "kitten"→"sitting", substitute k→s, substitute e→i, then insert g, giving distance 3.

## 11. Time Complexity

With n,m scalar counts, total time is O(nm+n+m+1), including validation and initialization. C++ decoding costs O(B) for B UTF-8 bytes, at most four per scalar. The table cell count is independent of string contents, so fixed nonempty lengths give Θ(nm) DP work. Distances never exceed max(n,m)≤1000.

## 12. Space Complexity

O(min(n,m)+1) DP words and O(1) result, without recursive frames. C++ also stores O(n+m) decoded scalars, so total auxiliary storage there is O(n+m+1). Python uses original strings. A full matrix or memoization uses O(nm) cells; reconstruction requires more information than the returned distance.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `edit_distance(first, second)`. It uses native integers and validates the shared numeric/resource domain before allocating the DP table. Native integer inputs exclude bool and floating point. Invalid domains raise ValueError; the documented arithmetic overflow raises OverflowError. The function does not mutate its arguments and import performs no I/O.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `edit_distance(first, second)` in namespace `atlas_dp`; define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. The shared [header](../common.hpp) supplies validation and CLI helpers, not algorithm logic. C++17 and C++20 use standard containers, 64-bit signed integers and exceptions: invalid_argument for invalid/resource domains, overflow_error for the documented arithmetic overflow. API arguments are read only.

## 15. Input and Output Examples

From the repository root, the CLI grammar is **exactly two text lines**. Text is strict UTF-8 with no normalization; LF separates lines and CRLF is accepted. A final LF is optional when the last line is nonempty. Missing or extra lines are rejected. Embedded line breaks require the API instead of the CLI. Successful stdout is one JSON value followed by a newline. Errors write a diagnostic to stderr, return exit code 2, and leave stdout empty.

```sh
printf '%s\n' 'kitten
sitting' | .venv/bin/python dsa/dynamic-programming/edit-distance/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/dynamic-programming/edit-distance/cpp/solution.cpp -o /tmp/atlas-edit-distance
printf '%s\n' 'kitten
sitting' | /tmp/atlas-edit-distance
```

Both print:

```text
3
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/dynamic-programming/edit-distance --require-cpp` to execute Python and both C++ standards. The [tests](tests/cases.py) provide independent expectations, rather than relying only on language agreement.

## 16. Edge Cases

Empty-to-empty is zero. Empty-to-length-m is m; identical strings give zero. Repeated symbols are processed by position. "é" and "é" have distance 2 under the scalar contract, with no normalization. Transposing "ab" to "ba" costs 2. Independent tests enumerate all monotone paired-position alignments rather than reusing the DP recurrence.

## 17. Advantages

The state captures all three operations, boundary rows have an explicit interpretation, and the output is exact. Rolling rows reduce table storage.

## 18. Disadvantages and Limitations

The implementation visits a quadratic state space and caps each string at 1000 scalars. It returns no edit script and does not implement weighted, affine-gap, transposition, or grapheme-aware distances. Invalid UTF-8 is rejected before table allocation.

## 19. When to Use It

Use for exact unit-cost distance on short strings when insertion/deletion shifts must be considered.

## 20. When Not to Use It

Use a different contract for weighted spelling errors, adjacent transpositions, normalization-sensitive matching, large alignments or threshold-only approximate search.

## 21. Comparison With Related Algorithms

| Measure | Operations | Typical result |
| --- | --- | --- |
| Levenshtein here | insert/delete/substitute | minimum unit cost |
| Hamming | substitutions on equal lengths | positional mismatches |
| LCS | paired matches and skips | maximum matched length |
| Damerau-Levenshtein | includes transpositions | different edit model |

## 22. Interview Questions

Why do the empty-prefix boundary values increase? What does each neighboring cell mean? Why is swapping strings safe with these costs but not arbitrary asymmetric costs? How could an edit script be reconstructed?

## 23. Practice Problems

Fill a table for repeated characters. Add explicit costs and revisit whether swapping is valid. Separately reconstruct a deterministic edit script and verify that applying it yields the target string.

## 24. References

[MIT 6.006 dynamic programming lecture notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-notes/) provides background on states, evaluation order, and correctness. The recurrences and contracts here are explained independently; no lecture code is copied. The project-specific resource and output contracts are specified in this lesson and its source.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
