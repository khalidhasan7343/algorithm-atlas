# Brian Kernighan’s Set Bit Counting

## 1. Algorithm Name

Brian Kernighan’s Set Bit Counting

## 2. Overview

Count one set bit per iteration by replacing a nonzero unsigned word with word AND (word-1).

## 3. Problem Statement

Given a signed 32-bit input, return the number of ones in its finite 32-bit two’s-complement representation, from zero through 32.

**API:** solve(value) accepts one native Python int or C++ int64_t constrained to -2147483648..2147483647. It returns an integer count. The executable requires exactly one decimal token.

Read [fixed-width contracts](../../../docs/bit-conventions.md) for decimal grammar, two’s-complement interpretation, errors and resource limits.

## 4. Why Do We Need This Algorithm?

Scanning all 32 positions works but ignores sparsity. Clearing the lowest set bit makes the loop count depend on the number of ones instead of their positions.

## 5. Real-World Applications

Counting enabled flags in a bounded mask, checking Hamming-weight properties and teaching sparse bit processing. A CPU popcount intrinsic may be faster in production, but is not used to bypass this lesson.

## 6. Core Intuition

For nonzero word, subtracting one flips its trailing zeros to ones and its lowest one to zero. AND with the original word restores the higher bits and clears exactly that lowest one.

## 7. Prerequisites

Understand binary place values, arrays, loops and asymptotic analysis. Bitwise XOR/AND act independently on each bit. Two’s-complement words are a mathematical interpretation of unsigned values here; C++17 signed representation is not assumed. See [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Validate the signed input. Convert to its unsigned 32-bit word by modulo/masking. Start count at zero. While the word is nonzero, replace it by word & (word-1) and increment count. Return the count when no ones remain.

**Correctness:** At each loop boundary, count equals the number of original ones removed, and every remaining one is an original set bit. The subtraction-and-AND identity removes exactly one and preserves every higher set bit. Thus the invariant advances by one, and a finite word with k ones terminates after exactly k iterations, returning k. Zero never enters subtraction in the loop.

## 9. Pseudocode

```text
validate signed-32 input
word = value modulo 2^32
count = 0
while word != 0:
    word = word AND (word-1)
    count += 1
return count
```

## 10. Dry Run

For 44, binary 00101100 becomes 00101000, then 00100000, then 00000000: three iterations. For -1, the fixed-width word is 32 ones, so 32 iterations. INT32_MIN is 0x80000000 and takes exactly one iteration.

## 11. Time Complexity

O(k) loop work for k set bits, with at most 32 iterations. Including constant validation/return work, total time is O(k+1); zero is O(1), and for the fixed-width domain the absolute worst case is bounded by 32. There is no input-length preprocessing pass. A general w-bit model would have worst O(w).

## 12. Space Complexity

O(1) auxiliary storage: one 32-bit word and a counter. No table, returned bit array, string conversion or recursion is used by the implementation.

## 13. Python Implementation

Validation occurs before value & 0xffffffff. This masking is essential: repeatedly clearing bits of an unmasked negative Python integer does not converge to zero under its unbounded signed bitwise model. Production code does not call int.bit_count or bin. Read [`python/solution.py`](python/solution.py). Importing it performs no demonstration.

## 14. C++ Implementation

The loop variable is uint32_t and count is int64_t. Because word is nonzero in the body, subtraction by Word{1} is defined and the unsigned word cannot trigger signed overflow. Conversion of negative input to unsigned is modulo 2^32; no signed shifts or representation-dependent reinterpretation are used. Read [`cpp/solution.cpp`](cpp/solution.cpp), namespace atlas_bit. Define ALGORITHM_ATLAS_NO_MAIN when including it in an API driver. C++17 and C++20 use the same standard-library implementation.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '-1' | .venv/bin/python dsa/bit-manipulation/brian-kernighan-set-bit-counting/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/bit-manipulation/brian-kernighan-set-bit-counting/cpp/solution.cpp -o /tmp/atlas-bit-example
printf '%s\n' '-1' | /tmp/atlas-bit-example
```

Both output:

```json
32
```

Replace -std=c++17 with -std=c++20 for that build. Tokens are signed decimal values without a count prefix. CLI errors exit 2 with error: on stderr, without partial output.

## 16. Edge Cases

Zero returns zero; powers of two return one. -1 represents all 32 ones and returns 32, while INT32_MAX returns 31 and INT32_MIN returns one. Alternating positive/negative masks exercise upper bits. Values such as unsigned 4294967295 must be supplied as signed -1 under this contract. Bool, floats, missing/multiple CLI tokens and out-of-domain integers are rejected.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use [independent oracles](../bit_oracles.py), deterministic random cases and numeric boundaries. Exact vector counts, seeds and executed outcomes are recorded in [checkpoints](../../../docs/bit-manipulation-checkpoints.md).

## 17. Advantages

Simple sparse-bit loop with work proportional to the actual number of set bits, and a direct termination proof.

## 18. Disadvantages and Limitations

Fixed signed-32 semantics differ from Python’s absolute-value bit_count behavior on negatives. Branching loop performance need not beat hardware popcount. Wider words and arbitrary-precision bit models require a different explicit contract.

## 19. When to Use It

Choose for sparse fixed-width masks and when demonstrating removal of individual set bits.

## 20. When Not to Use It

Do not use unmasked negative Python input or expect this educational loop to outperform platform population-count instructions.

## 21. Comparison With Related Algorithms

A fixed-position reference scans 32 bits regardless of density. Lookup tables and hardware instructions trade implementation/platform complexity for speed. The XOR lessons instead exploit parity across arrays, not population count of one word.

## 22. Interview Questions

Which bit changes in word & (word-1)? Why is zero checked first? Why does -1 have 32 ones here but abs(-1) has one? Why is an unmasked negative Python loop nonterminating?

## 23. Practice Problems

Trace 0b101010. Check every 12-bit word and its signed 32-bit complement against a representation oracle. Prove count(-2^j)=32-j for 0≤j≤31.

## 24. References

[C++17 working draft N4659](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/n4659.pdf), integral conversion and unsigned arithmetic rules; [Python integer bitwise semantics](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types); [Sean Eron Anderson’s Bit Twiddling Hacks](https://graphics.stanford.edu/~seander/bithacks.html). The exact API and validation policy are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
