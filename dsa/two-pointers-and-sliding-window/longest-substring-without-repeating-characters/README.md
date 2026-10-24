# Longest Substring Without Repeating Characters

## 1. Algorithm Name

Longest Substring Without Repeating Characters

## 2. Overview

Track each byte’s last position to maintain a forward-only window containing no repeated symbol.

## 3. Problem Statement

Return the earliest longest half-open byte interval [start,end] with all distinct symbols, or [0,0] for empty input.

**API:** solve(text); C++ longest_distinct. Python bytes/C++ std::string, length≤10000, all 256 bytes supported. Unicode callers encode UTF-8 explicitly; indexes count bytes.

[Shared contracts](../../../docs/two-pointers-sliding-window-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

Restarting a distinctness check for every substring repeats work. The last duplicate position tells exactly how far the left boundary must advance.

## 5. Real-World Applications

Distinct-symbol span analysis in bounded byte streams, sequence-window exercises and learning variable-window invariants. This byte API does not claim linguistic Unicode-character behavior.

## 6. Core Intuition

When the next byte last appeared inside the active window, every valid suffix must start after that occurrence. If it appeared before the window, the boundary must remain where it is.

## 7. Prerequisites

Half-open intervals, byte indexing, fixed-alphabet lookup tables and monotone window boundaries. Read the [approved String byte conventions](../../../docs/string-conventions.md).

## 8. Step-by-Step Working Process

Validate bytes and length; initialize a 256-entry last-position table to -1. For each right index, set left=max(left,last[byte]+1), update last[byte], and compare the current interval length with the best. Replace best only for a strictly longer interval so the earliest equal-length answer remains.

**Correctness:** Before extension the active interval has unique bytes. The new byte can duplicate only its last occurrence; advancing beyond it removes that conflict, while max prevents reintroducing older conflicts by moving left backward. Thus each maintained interval is the longest unique suffix ending at the current right. Considering all right endpoints finds the global optimum. Right endpoints and left boundaries are nondecreasing, so keeping the first equal optimum implements earliest-start ties.

## 9. Pseudocode

```text
last[0..255]=-1; left=0; best=[0,0]
for right,byte in text:
    left=max(left,last[byte]+1)
    last[byte]=right
    if right+1-left>best.length: best=[left,right+1]
return best
```

## 10. Dry Run

For abba, after ab the best is [0,2]. The second b moves left to 2. The final a was previously at index 0, outside the active window; max keeps left=2 rather than incorrectly moving it backward to 1. ba ties the length two, so earliest ab remains [0,2].

## 11. Time Complexity

O(n+256) time including table initialization; for the fixed alphabet this is O(n+1). Each right index is processed once and left never retreats. No per-substring scan is used in production.

## 12. Space Complexity

O(256) auxiliary last-position entries and a two-index result, constant for the supported alphabet. No substring copies or returned text allocation are performed by the algorithm.

## 13. Python Implementation

Bytes iteration supplies integers 0..255. The module reuses approved String validation and hex transport, keeping cross-language byte semantics consistent without modifying prior source. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

The code reuses approved String byte conversion and validation. unsigned-char promotion indexes the fixed table safely even when char is signed. The input is a const string reference; indices fit the 10000-byte bound. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '6162636162636262' | .venv/bin/python dsa/two-pointers-and-sliding-window/longest-substring-without-repeating-characters/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/two-pointers-and-sliding-window/longest-substring-without-repeating-characters/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '6162636162636262' | /tmp/atlas-category-example
```

Both print:

```json
[0,3]
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Empty, repeated bytes, alternating sequences, a repeated symbol already outside the window, earliest ties, NUL/255, all-byte alphabets and UTF-8-encoded samples are tested. Python str/bytearray and overlong input are rejected. UTF-8 intervals may split code points; no normalization or grapheme guarantee is implied.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/two-pointers-sliding-window-checkpoints.md).

## 17. Advantages

A deterministic linear scan with constant alphabet storage and explicit earliest-range output.

## 18. Disadvantages and Limitations

The alphabet is bytes, not Unicode code points or graphemes. The API returns one optimal interval, not all optimal spans or a copied substring.

## 19. When to Use It

Choose for exact case-sensitive distinct-byte spans and reproducible byte offsets.

## 20. When Not to Use It

For linguistic text, define decoding/normalization and code-point/grapheme indexing before adapting the algorithm; do not silently relabel byte offsets.

## 21. Comparison With Related Algorithms

Independent brute-force expansion from each start uses a fresh seen-symbol set and can take quadratic work. This algorithm reuses last positions across all starts. Fixed-size Sliding Maximum maintains a different deque invariant.

## 22. Interview Questions

Why is max needed when updating left? Why can a repeated byte outside the window be ignored? Why do equal-length ties keep the earliest start? Can a UTF-8 byte interval split a character?

## 23. Practice Problems

Trace tmmzuxt and abba. Enumerate all strings over a three-byte alphabet through length six and compare a fresh-set oracle. Test all 256 symbols repeated twice and verify the earliest 256-byte span.

## 24. References

[UCSD sliding-window lesson](https://ucsdicpc.github.io/slides/two_pointers_lesson.pdf) and the repository’s [String byte contracts](../../../docs/string-conventions.md). The last-position invariant and earliest tie rule are derived here. The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
