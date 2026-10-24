# XOR Tricks for Unique Elements

## 1. Algorithm Name

XOR Tricks for Unique Elements

## 2. Overview

Cancel exact pairs in a fixed-width XOR accumulation to recover one singleton.

## 3. Problem Statement

Given exactly one value occurring once and every other distinct value occurring twice, return the singleton. The default API rejects unsupported occurrence counts.

**API:** solve(values) is checked; xor_candidate(values) is the O(n)/O(1) core under caller-guaranteed pair assumptions. Input is a list/tuple of signed 32-bit integers, nonempty odd length≤10000; result is a signed 32-bit integer.

Read [fixed-width contracts](../../../docs/bit-conventions.md) for decimal grammar, two’s-complement interpretation, errors and resource limits.

## 4. Why Do We Need This Algorithm?

Pair cancellation replaces sorting or a frequency lookup for the actual computation. A separate checked wrapper makes the assumption visible instead of pretending that XOR proves it.

## 5. Real-World Applications

Small audit/reconciliation demonstrations in which every ordinary record identifier is known to occur twice and one is unmatched. Arbitrary corrupted or repeated identifiers do not meet that model.

## 6. Core Intuition

For every bit, XOR is addition modulo two. Therefore x XOR x=0, x XOR 0=x, and associativity/commutativity let all exact pairs cancel regardless of ordering.

## 7. Prerequisites

Understand binary place values, arrays, loops and asymptotic analysis. Bitwise XOR/AND act independently on each bit. Two’s-complement words are a mathematical interpretation of unsigned values here; C++17 signed representation is not assumed. See [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Validate sequence type, fixed-width range, odd length and size. solve additionally builds a frequency map, requiring one count of one and all other counts of two. The candidate function masks each value to 32 bits and XORs every word into a zero accumulator. Decode the final word by subtracting 2^32 if its high bit is set.

**Correctness:** After processing a prefix the accumulator equals the XOR of that prefix’s 32-bit words. Extending by one word preserves this invariant. At termination every pair contributes zero, leaving exactly the singleton word. The signed decode is inverse to modulo-2^32 input conversion on the supported range. Multiplicity validation is a separate proof obligation; XOR parity cannot distinguish a triple from a singleton.

## 9. Pseudocode

```text
solve(values):
    validate exactly one singleton and all other counts exactly two
    return xor_candidate(values)
xor_candidate(values):
    validate numeric domain, nonempty odd length and size
    word=0
    for value in values: word = word XOR (value modulo 2^32)
    return word if word<2^31 else word-2^32
```

## 10. Dry Run

Input [5,2,5,-7,2] uses -7=0xfffffff9. Accumulation is 0x00000005, 0x00000007, 0x00000002, 0xfffffffb, 0xfffffff9. Decode the last word as -7. Input [1,1,1] also XORs to 1, but solve rejects its triple count.

## 11. Time Complexity

The candidate performs one numeric-validation pass and one XOR pass: O(n) best/average/worst time for a valid-size sequence. The default solve adds expected O(n) hash-frequency validation; generic hash worst case is O(n²). Fixed 32-bit operations are O(1). No sorting is used and no count-table key is returned instead of the XOR result.

## 12. Space Complexity

Candidate auxiliary storage is O(1) for the accumulator and loop state, excluding caller input. Checked solve uses O(d) frequency entries for d distinct values and returns one scalar; do not attribute the core’s constant-space bound to that wrapper.

## 13. Python Implementation

The candidate uses value & 0xffffffff before XOR, so negative unbounded Python integers become finite words. Shared validation rejects bool as well as floats, str and out-of-range integers. No Counter computes the production answer. Read [`python/solution.py`](python/solution.py). Importing it performs no demonstration.

## 14. C++ Implementation

Inputs and returned signed values use int64_t, validated to the signed-32 range. static_cast<uint32_t> gives modulo-2^32 words. Decoding widens the word first and subtracts 4294967296LL when needed, avoiding implementation-defined out-of-range signed casts. No negation of INT32_MIN is needed. Read [`cpp/solution.cpp`](cpp/solution.cpp), namespace atlas_bit. Define ALGORITHM_ATLAS_NO_MAIN when including it in an API driver. C++17 and C++20 use the same standard-library implementation.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '5 2 5 -7 2' | .venv/bin/python dsa/bit-manipulation/xor-unique-elements/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/bit-manipulation/xor-unique-elements/cpp/solution.cpp -o /tmp/atlas-bit-example
printf '%s\n' '5 2 5 -7 2' | /tmp/atlas-bit-example
```

Both output:

```json
-7
```

Replace -std=c++17 with -std=c++20 for that build. Tokens are signed decimal values without a count prefix. CLI errors exit 2 with error: on stderr, without partial output.

## 16. Edge Cases

A single negative, zero, INT32_MIN or INT32_MAX is valid. Pairs may include zero or either boundary. Empty/even arrays, two or three singletons, triple/fourfold counts, invalid types and width overflow are rejected by solve. Candidate APIs intentionally cannot establish arbitrary multiplicities.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use [independent oracles](../bit_oracles.py), deterministic random cases and numeric boundaries. Exact vector counts, seeds and executed outcomes are recorded in [checkpoints](../../../docs/bit-manipulation-checkpoints.md).

## 17. Advantages

A deterministic linear, order-independent computation with constant working space under a precise multiplicity promise.

## 18. Disadvantages and Limitations

XOR loses frequency information; even parity is not the same as “occurs exactly twice.” The checked wrapper uses additional map memory and hash costs. Values wider than 32 bits are outside this lesson’s cross-language contract.

## 19. When to Use It

Use the candidate for trusted pair-structured inputs and solve when the occurrence promise must be checked.

## 20. When Not to Use It

Do not use parity cancellation as validation for arbitrary multiplicities; use frequency counting or a domain-specific invariant instead.

## 21. Comparison With Related Algorithms

Frequency counting supports arbitrary counts with O(d) memory; sorting can expose runs in O(n log n) time. Two Non-Repeating adds a differing-bit partition because one XOR cannot separate two singleton words.

## 22. Interview Questions

Why does reordering not matter? What does [1,1,1] prove about validation? Why must Python negatives be masked? Which space bound belongs to solve rather than xor_candidate?

## 23. Practice Problems

Trace [0,-1,-1]. Construct different invalid inputs with the same XOR. Test every singleton/pair combination over five small signed values. Explain the signed decode of 0x80000000.

## 24. References

[C++17 working draft N4659](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/n4659.pdf), integral conversion and unsigned arithmetic rules; [Python integer bitwise semantics](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types); [Sean Eron Anderson’s Bit Twiddling Hacks](https://graphics.stanford.edu/~seander/bithacks.html). The exact API and validation policy are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
