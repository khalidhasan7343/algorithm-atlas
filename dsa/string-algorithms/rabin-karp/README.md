# Rabin–Karp

## 1. Algorithm Name

Rabin–Karp

## 2. Overview

Maintain a polynomial fingerprint of each text window, then verify every candidate byte by byte.

## 3. Problem Statement

Filter possible occurrences with a genuine constant-work rolling update while returning only exact matches.

**API:** `solve(text, pattern, base=257, modulus=1000000007); fingerprint(data, base, modulus). base is 1..1000000007; modulus is 2..1000000007. Python bool is rejected as a parameter.`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

A window fingerprint can be updated without rescanning the entire window. Verification preserves correctness even when distinct windows collide.

## 5. Real-World Applications

Educational signature scanning and rolling-fingerprint demonstrations; hash candidates also arise in duplicate-block detection, where verification policy must be explicit.

## 6. Core Intuition

Map byte b to b+1. For width m, the outgoing byte contributes (b+1)*base^(m-1). Subtract that contribution, multiply by base and append the incoming byte.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Validate bytes and parameters. Handle empty/too-long patterns. Compute high=base^(m-1) mod modulus and both initial hashes. At each alignment, compare every byte only when hashes agree. Roll to the next alignment with modular removal and insertion. Candidate equality never bypasses exact verification.

**Correctness:** Induction on the window start shows the rolling value equals the polynomial fingerprint of that window: removal cancels its highest term, multiplication shifts remaining powers and insertion supplies the constant term. Equal strings therefore always become candidates. Byte verification accepts exactly equal strings, so collisions cannot create false positives.

## 9. Pseudocode

```text
high = base^(m-1) mod modulus
target = hash(pattern); window = hash(text[0:m])
for start = 0 .. n-m:
    if window = target and every aligned byte agrees: append start
    if another window exists:
        window = ((window - (outgoing+1)*high)*base + incoming+1) mod modulus
```

## 10. Dry Run

For aaaaa / aaa, the initial and pattern hashes agree. Every later window is also aaa and is verified, reporting [0,1,2]. Deliberate collision: bytes 00 02 and 02 00 both hash to 0 with base=1, modulus=2; verification correctly reports no occurrence.

## 11. Time Complexity

Preprocessing O(m); rolling updates O(n). Total O(n+m+c*m+r), where c is the number of candidate windows. Under a suitable low-collision random-hash model and sparse true matches, expected work is O(n+m+r). These fixed public parameters provide no such adversarial guarantee: worst case is O(nm), including dense genuine matches. Python modular exponentiation is O(log m) multiplications, within preprocessing O(m) for nonempty m. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(1) matching state plus O(r) results, with an O(m) temporary initial window copy in Python/C++. fingerprint itself uses constant auxiliary arithmetic state. Integer arithmetic is bounded by validated parameters, not cryptographic precision.

## 13. Python Implementation

Python modulo normalizes the subtraction before the next iteration; arbitrary-precision arithmetic avoids machine overflow. fingerprint is exposed for independent collision tests. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

int64_t arithmetic is safe: base and modulus are at most 1000000007; reduced hash times base is at most 1000000013000000042 before adding at most 256, below INT64_MAX. The outgoing-byte product is at most 256*(modulus-1). Removal is reduced before multiplication. high is computed iteratively. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '6161616161 616161\n' | .venv/bin/python dsa/string-algorithms/rabin-karp/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/rabin-karp/cpp/solution.cpp -o /tmp/atlas-string-example
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

Constant-work rolling updates and exact answers even with deliberately poor parameters.

## 18. Disadvantages and Limitations

Fixed deterministic hashes are not cryptographic, and candidate verification can dominate on repetitive/adversarial data. No multi-pattern batching is provided. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose to study rolling fingerprints and their verification requirements.

## 20. When Not to Use It

Use KMP for a deterministic linear worst-case bound on exact single-pattern matching.

## 21. Comparison With Related Algorithms

Unlike a Monte Carlo fingerprint-only matcher, this implementation has no false positives. KMP avoids hash arithmetic and collisions; Naive checks every alignment directly.

## 22. Interview Questions

Why map each byte to b+1? Which term must be removed? Why can even a collision-free pattern hash still lead to O(nm) with many true occurrences?

## 23. Practice Problems

Verify a polynomial hash by hand. Use base=1 and modulus=2 to construct two unequal candidates. Compare all matches against slicing with deliberately weak parameters.

## 24. References

[Princeton substring-search chapter](https://algs4.cs.princeton.edu/53substring/). The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
