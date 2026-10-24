# Manacher’s Algorithm

## 1. Algorithm Name

Manacher’s Algorithm

## 2. Overview

Compute maximal odd and even palindrome radii using mirrored information inside the rightmost palindrome.

## 3. Problem Statement

Return both radius arrays and the earliest longest half-open byte-palindrome range.

**API:** `radii(text) returns (odd,even) in Python and [odd,even] in C++; solve(text) returns [odd,even,[start,end]].`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

Expanding independently around every center repeats comparisons on repetitive data. Mirroring inside a known palindrome reuses those comparisons.

## 5. Real-World Applications

Palindrome feature extraction in byte sequences, repeated-symmetry exercises and efficient longest-palindromic-substring queries for an in-memory string.

## 6. Core Intuition

Centers reflected inside a palindrome have symmetric known radii until the containing boundary. Start with that certified radius and extend only beyond it.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Run separate passes for odd and even centers. Maintain inclusive left/right bounds of the rightmost known palindrome. Seed from the reflected center, clipped at right; expand exact equal bytes and update bounds. odd[i] includes the center, even[i] counts pairs centered immediately before i. Scan both arrays and choose greatest length, breaking ties toward the smaller start.

**Correctness:** Reflection certifies all seeded equal pairs within the current palindrome. Clipping avoids assuming equality past its boundary; expansion establishes maximality at the new center. Thus each radius describes exactly the maximal palindrome of its parity. Every palindrome has one of these centers, so selecting the greatest derived length is optimal; the explicit smaller-start comparison makes ties deterministic.

## 9. Pseudocode

```text
for each parity:
    left=0; right=-1
    for center i:
        radius = minimum mirrored radius clipped at right, or parity base
        while outside pair exists and bytes agree: radius += 1
        store radius; update rightmost palindrome if extended
best=[0,0]
for every odd/even radius: consider its interval, prefer longer then earlier
```

## 10. Dry Run

For abba, odd=[1,1,1,1] and even=[0,0,2,0]. The even center before index 2 expands over bb then aa, yielding [0,4]. In babad, bab and aba have equal length; earliest start selects [0,3].

## 11. Time Complexity

Both radius passes take O(n); each extension outside the certified right boundary advances it, and each center has at most one final failed comparison. Longest-range selection is another O(n) pass. Best/average/worst time is O(n); empty input is constant. This does not enumerate all palindromic substrings. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(n) for the two returned radius arrays and O(1) scanning state; longest range adds two integers. No transformed string, sentinel, recursion or quadratic palindrome table.

## 13. Python Implementation

radii returns the two arrays. solve derives intervals [i-odd[i]+1,i+odd[i]) and [i-even[i],i+even[i]) and applies explicit tie rules. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

Signed int center arithmetic makes left-bound tests safe. Reflected indices are read only when i is inside the current valid right boundary; input lengths are checked before conversion. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '61626261\n' | .venv/bin/python dsa/string-algorithms/manacher/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/manacher/cpp/solution.cpp -o /tmp/atlas-string-example
printf '61626261\n' | /tmp/atlas-string-example
```

C++20 works with `-std=c++20`. Both print:

```json
[[1,1,1,1],[0,0,2,0],[0,4]]
```

Each token is hex bytes; - means empty. See the shared contract for exact argument count and the special multi-pattern grammar.

## 16. Edge Cases

Empty text and pattern, one byte, longer patterns, repeated bytes, overlaps, all 256 symbols, NUL/separator-like bytes, case sensitivity and UTF-8 byte offsets are covered by [independent oracles](../string_oracles.py). Invalid types, lengths, missing/extra tokens and malformed hex are rejected; CLI errors exit 2 with error: on stderr.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use seed 90901 (multi-pattern seed 90904), bounded exhaustive binary cases and deterministic random cases. Matching references use slicing; preprocessing and advanced structures receive separate independent checks. Actual executed counts and outcomes belong to [checkpoints](../../../docs/string-algorithms-checkpoints.md), not an assumed CI run.

## 17. Advantages

Linear radius computation for both parities, deterministic ties and no separator collisions.

## 18. Disadvantages and Limitations

Radii count equal bytes, not Unicode code points or grapheme clusters. Returning all palindrome intervals would require output-sensitive additional space/time and is not this API. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose when all center radii or a longest exact byte palindrome are required.

## 20. When Not to Use It

Use explicit Unicode decoding and a revised contract for linguistic palindrome tasks; use a simpler expansion oracle for tiny test inputs.

## 21. Comparison With Related Algorithms

Independent center expansion is O(n²) worst case; exhaustive substring checking is slower still. Manacher avoids redundant comparisons via symmetry rather than substring hashing.

## 22. Interview Questions

Why does even-center reflection add one? What do radius zero and radius one mean for each parity? How is a longest tie decided? Can UTF-8 encoding change palindrome structure?

## 23. Practice Problems

Trace both arrays for aaaa and abba. Compare against exhaustive enumeration for binary strings through length six. Derive a palindrome-count formula from the radii without listing substrings.

## 24. References

[Manacher, A New Linear-Time On-Line Algorithm for Finding the Smallest Initial Palindrome of a String (1975)](https://doi.org/10.1145/321892.321896). The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
