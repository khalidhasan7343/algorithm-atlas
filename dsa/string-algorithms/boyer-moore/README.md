# Boyer–Moore

## 1. Algorithm Name

Boyer–Moore

## 2. Overview

Compare from right to left, combining bad-character and strong good-suffix shifts.

## 3. Problem Statement

Find all exact occurrences using both canonical Boyer-Moore mismatch rules and a proper-border full-match shift.

**API:** `bad_character(pattern), good_suffix(pattern), and solve(text, pattern). good[0] is the full-match shift; good[j+1] handles a mismatch at j.`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

A mismatch can rule out several starts at once. The already matched suffix and the mismatching text byte supply separate safe shift constraints.

## 5. Real-World Applications

In-memory byte-signature search and text-search instruction where skipping on larger alphabets can save comparisons. No specific production deployment is claimed.

## 6. Core Intuition

Bad-character alignment places a prior occurrence of the mismatching byte under it, or moves beyond it. Good-suffix alignment preserves a possible occurrence of the suffix just matched while changing its preceding byte.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Build a 256-entry last-occurrence table. Build strong good-suffix shifts with border links, assigning mismatch entries during border fallback and filling remaining entries from proper prefix borders. Compare each alignment right to left. On mismatch at j, advance max(1,j-last[text[start+j]],good[j+1]); on full match, advance good[0].

**Correctness:** The bad-character shift excludes alignments unable to cover the mismatching text byte appropriately. The strong good-suffix shift excludes alignments incompatible with the matched suffix or repeating its known mismatching predecessor. Taking the maximum remains safe because each rule independently rules out all smaller shifts. The full-match border shift preserves the next possible overlap. All shifts are positive and each surviving alignment is tested exactly.

## 9. Pseudocode

```text
last = last_occurrence(pattern); good = strong_suffix_shifts(pattern)
start = 0
while start <= n-m:
    j = m-1
    while j>=0 and pattern[j]=text[start+j]: j-=1
    if j<0: report start; start += good[0]
    else: start += max(1, j-last[text[start+j]], good[j+1])
strong suffix preprocessing: follow border links right-to-left, assign shifts on mismatches; fill unassigned shifts with proper prefix borders
```

## 10. Dry Run

For aaa, last[a]=2 and good=[1,1,2,3]. At each complete match good[0]=1 retains the overlap. Searching aaaaa therefore reports [0,1,2]. If the final aligned text byte is b, bad-character gives 3 and skips the entire pattern width.

## 11. Time Complexity

Preprocessing O(m+256): border fallback reuses earlier suffix information, then a linear pass fills unset entries. The scan may skip m positions at a mismatch and often uses fewer comparisons on diverse text, but this all-occurrences variant has O(nm) worst-case time, plus O(r) output. Repeated a text/pattern rechecks every full match. No Galil rule or guaranteed linear worst-case claim is made. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(m+256) auxiliary tables and O(r) positions; no recursion or copied windows. The border work array is O(m) during preprocessing.

## 13. Python Implementation

good_suffix and bad_character are exposed for independent table tests. Negative bad-character proposals are harmless because max includes the positive good-suffix shift and 1. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

Byte-indexed last-occurrence storage prevents signed-char table indexing. m+1 shift and border slots include full-match and empty-suffix cases; control flow never dereferences border[m+1]. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '6161616161 616161\n' | .venv/bin/python dsa/string-algorithms/boyer-moore/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/boyer-moore/cpp/solution.cpp -o /tmp/atlas-string-example
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

Both mismatch rules can skip alignments, and full-match shifts preserve all overlaps.

## 18. Disadvantages and Limitations

Repeated full matches remain quadratic without Galil optimization. Tables are rebuilt for each solve call and require O(m+256) memory. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose when right-to-left skipping is desirable and the pattern/text alphabet makes long skips common.

## 20. When Not to Use It

Use KMP when adversarial repetitive input needs a simple deterministic linear bound.

## 21. Comparison With Related Algorithms

Horspool or a bad-character-only search is a different variant. This implementation includes strong good-suffix preprocessing and is tested against an independently enumerated shift oracle.

## 22. Interview Questions

Why does full-match shift use a proper border? Why can j-last[byte] be negative? What would a zero shift do? Which missing optimization prevents claiming a linear all-occurrences worst case?

## 23. Practice Problems

Calculate both tables for ababa. Enumerate safe suffix shifts by brute force. Compare shift counts for a repeated alphabet and uniformly diverse bytes.

## 24. References

[Boyer and Moore, A Fast String Searching Algorithm (1977)](https://www.cs.utexas.edu/~moore/publications/fstrpos.pdf). The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
