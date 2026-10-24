# Naive Pattern Matching

## 1. Algorithm Name

Naive Pattern Matching

## 2. Overview

Try every legal alignment and compare the pattern bytes from left to right.

## 3. Problem Statement

Find every exact occurrence without preprocessing or probabilistic assumptions.

**API:** `solve(text, pattern) returns the ascending list of start positions.`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

A direct method is easy to audit and supplies a useful baseline for optimized matchers.

## 5. Real-World Applications

Small configuration searches, short binary signatures, and independent reference checks where simplicity matters more than long repetitive inputs.

## 6. Core Intuition

An occurrence begins at an alignment precisely when all m corresponding bytes agree. Testing each alignment cannot miss an overlap.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Validate both byte strings. For each start from 0 through n-m, advance j while aligned bytes agree. Append start only if j reaches m. An empty pattern succeeds immediately at every boundary. If m>n there is no legal alignment.

**Correctness:** Before comparison j, the first j aligned bytes agree. A mismatch rules out exactly this alignment; completing m comparisons proves an occurrence. Every possible start is considered once, so the ascending result contains all and only occurrences.

## 9. Pseudocode

```text
for start = 0 .. n-m:
    j = 0
    while j < m and text[start+j] = pattern[j]: j += 1
    if j = m: append start
```

## 10. Dry Run

Text aaaaa and pattern aaa: starts 0, 1 and 2 each compare three equal bytes, giving [0,1,2]. There is no start 3 because only two text bytes remain.

## 11. Time Complexity

No preprocessing. O((n-m+1)m) comparisons when 1≤m≤n, hence O(nm) worst case. Early mismatches cost O(n) for fixed nonempty m≤n; m>n takes O(1) after validation. Empty pattern costs O(n) to emit n+1 results. Output adds O(r), where r is the number of occurrences. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(1) auxiliary matching state and O(r) returned positions; input storage is external. The implementation uses no substring copies.

## 13. Python Implementation

A while loop compares byte integers directly, rather than delegating matching to find or a regular-expression library. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

Signed int loop bounds are safe after the 10000-byte checks; comparing char values for equality is independent of signed-char ordering. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '6161616161 616161\n' | .venv/bin/python dsa/string-algorithms/naive-pattern-matching/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/naive-pattern-matching/cpp/solution.cpp -o /tmp/atlas-string-example
printf '6161616161 616161\n' | /tmp/atlas-string-example
```

C++20 works with `-std=c++20`. Both print:

```json
[0,1,2]
```

Each token is hex bytes; - means empty. See the shared contract for exact argument count and the special multi-pattern grammar.

## 16. Edge Cases

Empty text and pattern, one byte, longer patterns, repeated bytes, overlaps, all 256 symbols, NUL/separator-like bytes, case sensitivity and UTF-8 byte offsets are covered by [independent oracles](../string_oracles.py). Invalid types, lengths, missing/extra tokens and malformed hex are rejected; CLI errors exit 2 with error: on stderr.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use seed 90901 (multi-pattern seed 90904), bounded exhaustive binary cases and deterministic random cases. Matching references use slicing; preprocessing and advanced structures receive separate independent checks. Actual executed counts and outcomes belong to [checkpoints](../../../docs/string-algorithms-checkpoints.md), not an assumed CI run.

## 17. Advantages

Transparent correctness and minimal working memory; every alignment and overlap is explicit.

## 18. Disadvantages and Limitations

Repetitive near-matches repeat the same comparisons. There is no preprocessing cache or skip heuristic. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose for short strings, pedagogical traces or an independent oracle.

## 20. When Not to Use It

Use KMP when long repetitive strings require a deterministic linear scan.

## 21. Comparison With Related Algorithms

KMP spends O(m) preprocessing and auxiliary memory to avoid repeated work; Rabin-Karp filters alignments using a hash but must verify candidates.

## 22. Interview Questions

Why is n-m an inclusive upper bound? Why does an empty pattern have n+1 occurrences? Construct an input causing m comparisons at nearly every alignment.

## 23. Practice Problems

Trace aba in ababa. Enumerate all binary texts of length four and compare against slicing. Count comparisons on a repeated a string ending in b.

## 24. References

[Princeton substring-search chapter](https://algs4.cs.princeton.edu/53substring/). The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
