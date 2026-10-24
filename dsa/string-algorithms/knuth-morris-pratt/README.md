# Knuth–Morris–Pratt (KMP)

## 1. Algorithm Name

Knuth–Morris–Pratt (KMP)

## 2. Overview

Reuse proper-prefix/suffix lengths to match without moving the text cursor backward.

## 3. Problem Statement

Return every exact occurrence while avoiding repeated comparisons across failed alignments.

**API:** `prefix_function(pattern) returns proper-border lengths; solve(text, pattern) returns start positions.`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

A long partial match already contains useful information about the next possible alignment. Prefix preprocessing makes that information explicit.

## 5. Real-World Applications

Deterministic scanning of repetitive byte streams, sequence motif lookup and repeated-prefix analysis; this API scans a bounded in-memory byte string.

## 6. Core Intuition

When j bytes match and the next byte fails, only a proper border of the matched pattern prefix can remain matched. LPS[j-1] is the longest such border.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Compute lps[i], the longest proper prefix of pattern[0:i+1] equal to its suffix, by following earlier lps links on mismatch. During search, j counts matched bytes. Follow failure links until the next byte agrees or j=0, then extend. On a full match report its start and set j=lps[m-1] so overlaps remain possible.

**Correctness:** At each text position j describes the longest pattern prefix matching the suffix of processed text. Any longer candidate excluded by a failure link contradicts the definition of the longest proper border. Extending preserves this invariant; reaching m proves exactly an occurrence. Falling back after a report retains every possible overlapping occurrence.

## 9. Pseudocode

```text
lps = prefix_function(pattern)
if m = 0: return all boundaries
j = 0
for i = 0 .. n-1:
    while j > 0 and text[i] != pattern[j]: j = lps[j-1]
    if text[i] = pattern[j]: j += 1
    if j = m: append i-m+1; j = lps[m-1]
```

## 10. Dry Run

For aaa, LPS is [0,1,2]. In aaaaa, j first reaches 3 at i=2 and reports 0. Reset to 2, extend at i=3 and report 1; repeat at i=4 and report 2. The text cursor never retreats.

## 11. Time Complexity

LPS preprocessing O(m); scan O(n); reporting O(r), for O(n+m+r) total. Each successful comparison increases j by at most one and each fallback decreases it, giving an amortized linear number of fallbacks. Empty pattern needs O(n) output. Best/average/worst upper bounds are linear in text plus preprocessing and output; no random-input assumption is needed. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(m) auxiliary LPS storage plus O(r) results; prefix_function returns its own O(m) array. No recursion or copied text windows.

## 13. Python Implementation

prefix_function exposes the independently tested border array. Search uses the same table, including full-match fallback. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

The LPS array is vector<int>; signed positions and lengths remain within the validated 10000-byte bound. No byte ordering or locale operation is used. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '6161616161 616161\n' | .venv/bin/python dsa/string-algorithms/knuth-morris-pratt/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/knuth-morris-pratt/cpp/solution.cpp -o /tmp/atlas-string-example
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

Deterministic linear comparisons, overlaps and reusable prefix information.

## 18. Disadvantages and Limitations

The convenience solve API rebuilds the table each call and stores O(m) metadata. It does not expose incremental streaming state. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose for adversarial repeated prefixes and predictable worst-case scanning.

## 20. When Not to Use It

For many queries on one fixed text consider a suffix index; for many simultaneous patterns consider Aho-Corasick.

## 21. Comparison With Related Algorithms

Naive matching may repeat O(m) work per alignment. Boyer-Moore skips based on right-to-left mismatches and has a different worst-case bound in this repository.

## 22. Interview Questions

Why must a proper border be used after a full match? Why can fallback follow multiple links? Prove the amortized bound without assuming random bytes.

## 23. Practice Problems

Compute LPS for aabaaab: [0,1,0,1,2,2,3]. Trace ababac in ababababac. Design a reusable preprocessed-pattern API without changing matching semantics.

## 24. References

[Princeton substring-search chapter](https://algs4.cs.princeton.edu/53substring/) (its DFA presentation is an alternative to the border-table implementation here). The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
