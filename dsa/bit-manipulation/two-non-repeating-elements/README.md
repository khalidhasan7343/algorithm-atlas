# Finding Two Non-Repeating Elements

## 1. Algorithm Name

Finding Two Non-Repeating Elements

## 2. Overview

Use one differing bit of the total XOR to place two singleton words into separate cancellation groups.

## 3. Problem Statement

Return the two distinct values occurring once when all other distinct values occur exactly twice. Reject unsupported multiplicity patterns at the default API.

**API:** solve(values) validates exact counts; partition_candidates(values) exposes the assumption-based O(n)/O(1) core. Input is even-length signed-32 values, 2≤n≤10000. Output is a two-element list/vector in signed numeric ascending order.

Read [fixed-width contracts](../../../docs/bit-conventions.md) for decimal grammar, two’s-complement interpretation, errors and resource limits.

## 4. Why Do We Need This Algorithm?

A total XOR reveals only a XOR b, not a and b individually. One set bit of that difference supplies a partition that separates them without sorting the input.

## 5. Real-World Applications

Two unmatched-identifier demonstrations in a record collection with an established exact-pair invariant. This is not a generic missing-data or arbitrary-frequency detector.

## 6. Core Intuition

Distinct words a and b differ in at least one bit. Since identical pairs choose the same partition, their contributions cancel within that partition, leaving one singleton in each group.

## 7. Prerequisites

Understand binary place values, arrays, loops and asymptotic analysis. Bitwise XOR/AND act independently on each bit. Two’s-complement words are a mathematical interpretation of unsigned values here; C++17 signed representation is not assumed. See [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Validate numeric domain, even length and size; solve also validates exactly two singleton counts and otherwise exact pairs. XOR all unsigned words. Reject total zero, which is incompatible with two distinct singletons. Isolate its least significant one as total & ((0-total) modulo 2^32). XOR values into two groups according to that bit. Decode each group word and order the two signed results.

**Correctness:** The total equals a XOR b after pair cancellation, hence is nonzero. Its isolated bit belongs to exactly one singleton. Both copies of every paired value have identical bit tests, so cancel together. Each group therefore retains exactly one singleton word. Signed decoding recovers the input values, and ordering changes presentation without changing the pair. A nonzero total alone does not establish the multiplicity promise.

## 9. Pseudocode

```text
solve(values): validate two singletons and exact pairs; return partition_candidates(values)
partition_candidates(values):
    validate numeric domain and positive even length
    total = XOR of all unsigned 32-bit words
    require total != 0
    bit = total AND ((0-total) modulo 2^32)
    first=second=0
    for word in values:
        if word AND bit: first XOR=word
        else: second XOR=word
    decode both words; return in signed ascending order
```

## 10. Dry Run

Input [4,1,2,1,2,-7] cancels 1 and 2 pairs, leaving total=4 XOR 0xfffffff9=0xfffffffd. Low bit is 1. The set-bit group reduces to -7 and the other to 4, so result is [-7,4]. For [INT32_MIN,0], total=0x80000000 and the isolated bit is the most significant bit itself.

## 11. Time Complexity

The candidate performs validation and two complete passes: O(n) time in best/average/worst cases for valid-size input. Default solve adds expected O(n) frequency-map work, generic hash worst case O(n²). Ordering exactly two outputs costs O(1), not a sort of n inputs.

## 12. Space Complexity

Candidate uses a total word, differing bit and two group accumulators: O(1) auxiliary space and two returned values. Default checked validation uses O(d) map entries for d distinct values. Input is never copied or modified by either core.

## 13. Python Implementation

Masking each value to 32 bits and masking -total makes low-bit isolation a finite-width operation. The returned pair is sorted only after signed decoding, so negative values precede nonnegative ones. Read [`python/solution.py`](python/solution.py). Importing it performs no demonstration.

## 14. C++ Implementation

All cancellation and low-bit operations use uint32_t. Word{0}-total has deliberate unsigned modular subtraction, explicitly cast back to Word before the AND. Signed int64_t decoding never negates INT32_MIN and no shift into a signed sign bit occurs. Two-result comparison/swapping follows signed order. Read [`cpp/solution.cpp`](cpp/solution.cpp), namespace atlas_bit. Define ALGORITHM_ATLAS_NO_MAIN when including it in an API driver. C++17 and C++20 use the same standard-library implementation.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '4 1 2 1 2 -7' | .venv/bin/python dsa/bit-manipulation/two-non-repeating-elements/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/bit-manipulation/two-non-repeating-elements/cpp/solution.cpp -o /tmp/atlas-bit-example
printf '%s\n' '4 1 2 1 2 -7' | /tmp/atlas-bit-example
```

Both output:

```json
[-7,4]
```

Replace -std=c++17 with -std=c++20 for that build. Tokens are signed decimal values without a count prefix. CLI errors exit 2 with error: on stderr, without partial output.

## 16. Edge Cases

[0,INT32_MIN], [INT32_MIN,INT32_MAX], [-1,0] and two ordinary distinct values are valid minima. Zero total is rejected. Triple counts, four singletons, repeated-only input and out-of-domain values are rejected by solve; nonzero XOR is not sufficient validation.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use [independent oracles](../bit_oracles.py), deterministic random cases and numeric boundaries. Exact vector counts, seeds and executed outcomes are recorded in [checkpoints](../../../docs/bit-manipulation-checkpoints.md).

## 17. Advantages

Separates two unknown singleton values with a constant number of word accumulators and deterministic output order.

## 18. Disadvantages and Limitations

Exactly two distinct singleton values are required. Candidate functions do not validate this promise; the default frequency validation has a separate memory cost. General k-singleton recovery needs different information.

## 19. When to Use It

Choose when the exact-pair promise holds except for two distinct unmatched values.

## 20. When Not to Use It

Do not treat a nonzero aggregate XOR as proof of valid counts or use this method for arbitrary multiplicities.

## 21. Comparison With Related Algorithms

One-singleton XOR needs only one accumulator. Frequency counting can recover any number of singleton values with extra memory. Sorting finds runs without a bit partition but takes O(n log n) time.

## 22. Interview Questions

Why do pairs stay together? What does zero total mean under the promise? How can the isolated bit be 0x80000000? Why is signed x & -x unsafe at INT_MIN in C++?

## 23. Practice Problems

Trace [-1,0,3,3]. Find a malformed input with nonzero total. Verify the high-bit-only partition case. Derive why signed ordering must happen after decoding.

## 24. References

[C++17 working draft N4659](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/n4659.pdf), integral conversion and unsigned arithmetic rules; [Python integer bitwise semantics](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types); [Sean Eron Anderson’s Bit Twiddling Hacks](https://graphics.stanford.edu/~seander/bithacks.html). The exact API and validation policy are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
