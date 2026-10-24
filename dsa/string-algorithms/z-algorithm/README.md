# Z-Algorithm

## 1. Algorithm Name

Z-Algorithm

## 2. Overview

Compute the length of the prefix matching each nonzero byte position using a reusable rightmost Z-box.

## 3. Problem Statement

Expose the Z-array with Z[0]=0 and return all exact pattern occurrences.

**API:** `z_array(text) returns Z with Z[0]=0; solve(text, pattern) returns start positions.`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

Prefix comparisons performed earlier can seed later comparisons, avoiding quadratic rescanning of repeated prefixes.

## 5. Real-World Applications

Prefix-period analysis, exact motif scanning and prefix-based string exercises using a deterministic linear-time primitive.

## 6. Core Intuition

Inside a known prefix-equal box [left,right), the mirrored Z value is valid until the box boundary. Only bytes beyond that boundary require new comparisons.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Initialize zero Z values and an empty half-open box. At i inside the box, copy min(right-i,Z[i-left]); otherwise start at zero. Extend while bytes agree. If the new match extends farther, replace the box. For matching, compute Z over integer bytes of pattern, sentinel 256 and text; report text positions with Z at least m.

**Correctness:** The box certifies prefix equality on its entire range. Mirrored values within it are therefore valid, and truncation prevents assuming equality outside it. Explicit extension makes the resulting length maximal. A text position has Z≥m exactly when all m pattern bytes agree. Sentinel 256 is outside 0..255, so no input byte can masquerade as the separator.

## 9. Pseudocode

```text
Z[0] = 0; left = right = 0
for i = 1 .. N-1:
    if i < right: Z[i] = min(right-i, Z[i-left])
    while i+Z[i] < N and values[Z[i]] = values[i+Z[i]]: Z[i] += 1
    if i+Z[i] > right: left=i; right=i+Z[i]
matching: compute Z(pattern + [256] + text), retain text entries with Z>=m
```

## 10. Dry Run

For aaaaa the Z-array is [0,4,3,2,1]. The box becomes [1,5) at i=1; positions 2 through 4 reuse the known prefix equality up to the end. Matching aaa in aaaaa reports starts 0,1,2.

## 11. Time Complexity

z_array takes O(N) time, where N is its input length: successful fresh extensions advance right, while each position contributes at most one failing comparison. Matching builds N=m+1+n symbols and takes O(n+m+r), including construction and results. Empty pattern emits n+1 boundaries. No average-case assumption is used. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(N) Z values. Matching also materializes O(n+m) integer symbols and returns O(r) positions. Auxiliary space is O(n+m), unlike KMP’s O(m) pattern table.

## 13. Python Implementation

The internal _z works over either byte sequences or integer symbols. The public z_array validates bytes; solve alone supplies the collision-safe integer sentinel. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

z_values operates over vector<int> so the sentinel can be 256. Input char values are converted through unsigned char before being promoted. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '6161616161 616161\n' | .venv/bin/python dsa/string-algorithms/z-algorithm/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/z-algorithm/cpp/solution.cpp -o /tmp/atlas-string-example
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

One deterministic linear primitive supports both prefix analysis and exact matching; separator collisions are impossible.

## 18. Disadvantages and Limitations

Matching constructs the entire combined sequence and cannot directly stream incoming text. Z[0]=0 is a convention and differs from presentations using N. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose when the prefix-match array itself is useful, or to compare prefix-based matching with KMP.

## 20. When Not to Use It

Use KMP to avoid an O(n) combined-sequence allocation during a single-pattern scan.

## 21. Comparison With Related Algorithms

KMP stores border lengths of prefixes; Z stores prefix-match lengths starting at each position. Both use amortized linear reuse, but their arrays have different meanings.

## 22. Interview Questions

Why must a copied Z value be capped at right-i? What happens at i=right? Why is choosing a literal dollar sign as separator unsafe for arbitrary bytes?

## 23. Practice Problems

Derive Z for abacaba. Verify each value by direct expansion. Test a pattern containing every byte so that no byte-valued separator is available.

## 24. References

[Carnegie Mellon string-matching notes](https://www.cs.cmu.edu/~ckingsf/class/02714-f13/Lec02-zalg.pdf). The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
