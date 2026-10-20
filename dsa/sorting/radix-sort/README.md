# Radix Sort

## 1. Algorithm Name

**Radix Sort**, specifically stable **LSD (least significant digit) Radix Sort** with base 256. Digits are groups of eight bits. Python handles signed integers by subtracting the minimum; C++ maps its fixed-width signed domain into unsigned keys by flipping the sign position. These are two signed-key encodings of the same stable digit-processing algorithm.

## 2. Overview

Rather than repeatedly comparing whole values, Radix Sort groups values by one digit at a time, starting with the least significant. A stable counting pass preserves the order established for lower digits. After the highest relevant digit, all values are ordered. Both functions return a copy, leave input unchanged, and avoid built-in sorting functions.

## 3. Problem Statement

Given a finite sequence of signed integers, return the same values in ascending order in a new container. Python's `radix_sort(values: Sequence[int]) -> list[int]` accepts only native `int` values; booleans, integer subclasses, floats, strings, and other numeric types raise `TypeError`. Python integer magnitude is unrestricted by a fixed machine width. C++ exposes `algorithm_atlas::radix_sort(const std::vector<long long>&)` and requires the full signed 64-bit `long long` range, checked at compilation.

The standalone programs read whitespace-separated ASCII signed-decimal tokens, without a length prefix, and print one space-separated line. Empty input produces a newline. Invalid tokens produce a standard-error message, nonzero exit, and no partial sorted output. C++ also rejects overflow.

## 4. Why Do We Need This Algorithm?

A comparison sort must learn ordering from pairwise outcomes. Integer keys expose more structure: a byte has only 256 possible values, so a frequency table can place each item without a comparison search. Repeating stable passes exploits that structure while avoiding a frequency table spanning the entire integer range. Its benefit depends on digit count, allocation cost, and key representation.

## 5. Real-World Applications

- Sorting batches of fixed-width integer identifiers or encoded timestamps is a natural fit when several linear passes and a work buffer are acceptable.
- Preparing integer keys for grouping or duplicate analysis can benefit from processing bytes independently of the data's distribution.
- Educational data-processing tools can illustrate how digit encoding and stable distribution replace comparison sorting.

These describe appropriate workloads, not measured speedups or named deployments of this repository. This implementation sorts integers directly; attaching payload records, parallel processing, and hardware-specific optimization require additional design.

## 6. Core Intuition

Sort by the last digit, then by the next digit while preserving the earlier order among equal current digits. Lower digits then act as a tie-breaker without being explicitly compared again. Repeating this process sorts the complete keys. Stability is the crucial link: an unstable later pass could erase the ordering established by earlier digits.

Signed values first need order-preserving nonnegative keys. Python uses `key = value - minimum`, so ordering is unchanged and the smallest key is zero. C++ uses `uint64(value) XOR 2^63`; negative signed values map below nonnegative values, and each half retains increasing order.

## 7. Prerequisites

Understand integer division or bit shifting, masks, prefix sums, arrays, and stable ordering. [Counting Sort](../counting-sort/README.md) explains the per-digit distribution idea. Review [complexity notation](../../../docs/complexity-cheatsheet.md) and the [glossary](../../../docs/glossary.md). No recursion is needed.

## 8. Step-by-Step Working Process

1. Copy input and check the Python type contract. Return immediately for zero or one item.
2. Establish an order-preserving digit key. Python stores offset keys and chooses enough eight-bit digits for the largest key, with at least one pass. C++ computes a sign-flipped unsigned key and processes all eight digits.
3. Initialize 256 frequency counters for the selected digit.
4. Replace each frequency with the exclusive prefix total: the starting output position for that digit.
5. Traverse the current values from left to right. Place each value into its digit's next free position and advance that position. Python moves its stored key alongside its original value.
6. Swap the current and output buffers, then advance by eight bits.

After pass `p`, the sequence is ordered by its lowest `8p` key bits. The next stable pass groups by the next digit while retaining the lower-bit ordering inside each group, proving the invariant by induction. All keys fit within the processed digits, so the final order is the full key order. The encoding preserves signed order, which proves the desired result. Every scatter moves each input item exactly once, preserving multiplicity.

## 9. Pseudocode

```text
RADIX_SORT(values):
    result = COPY(values)
    VALIDATE_INPUT(values)
    IF LENGTH(result) < 2: RETURN result
    key(value) = an order-preserving nonnegative encoding
    d = number of eight-bit digits to process
    buffer = ARRAY(LENGTH(result))
    FOR pass FROM 0 TO d - 1:
        counts[0..255] = zero
        FOR value IN result:
            digit = (key(value) >> (8 * pass)) AND 255
            counts[digit] += 1
        next_position = 0
        FOR digit FROM 0 TO 255:
            frequency = counts[digit]
            counts[digit] = next_position
            next_position += frequency
        FOR value IN result, from left to right:
            digit = (key(value) >> (8 * pass)) AND 255
            buffer[counts[digit]] = value
            counts[digit] += 1
        SWAP(result, buffer)
    RETURN result
```

In Python, `key(v) = v - min(values)` is materialized once; a parallel key buffer follows every scatter. Its pass count is `max(1, ceil(bit_length(max_key) / 8))`. In C++, `key(v) = uint64(v) XOR 2^63` is computed when needed and `d = 8`. The pseudocode's forward scatter matches both implementations.

## 10. Dry Run

Input: `[256, -2, 1, -1, 0, 255]`.

Python chooses minimum `-2`, producing keys `[258, 0, 3, 1, 2, 257]`.

| Pass | Digits of current keys | Values after stable scatter |
| --- | --- | --- |
| Low byte | `[2, 0, 3, 1, 2, 1]` | `[-2, -1, 255, 256, 0, 1]` |
| Next byte | `[0, 0, 1, 1, 0, 0]` | `[-2, -1, 0, 1, 255, 256]` |

For the low-byte counts, digit 0 starts at position 0, digit 1 at position 1, digit 2 at position 3, and digit 3 at position 5. The two digit-1 values retain their relative order, as do the two digit-2 values. The largest key is 258, so two passes suffice.

C++ uses different keys and therefore different intermediate states:

| Processed byte | Values after stable scatter |
| --- | --- |
| 0, least significant | `[256, 0, 1, -2, -1, 255]` |
| 1 | `[0, 1, 255, 256, -2, -1]` |
| 2 through 6 | `[0, 1, 255, 256, -2, -1]` |
| 7, sign-adjusted | `[-2, -1, 0, 1, 255, 256]` |

For byte 7, negative values have digit 127 and these nonnegative values have digit 128. The final pass puts the negatives first while preserving each group's lower-byte order. Neither implementation changes the original input.

## 11. Time Complexity

Let `n` be the item count, `R = 256`, and `d` the processed digit count. For `n >= 2`, under constant-cost key extraction, each pass costs Θ(n + R): counting, prefix totals, and scattering. Best, average, and worst cases all take **Θ(d(n + 256))** for fixed `n` and `d`; existing sortedness does not eliminate passes. Empty and singleton inputs take constant work after copying/type checking.

C++ always uses `d = 8`, giving Θ(n + 256), conventionally Θ(n) with the radix fixed. Python uses the bit length of `max(values) - min(values)`, rounded up to bytes, with at least one pass; equal inputs thus take one pass. Its preprocessing adds a linear number of comparisons/subtractions.

The Python formula is a digit-operation model, not a claim that arbitrary-precision arithmetic takes constant time. If inputs occupy up to `L` bits and offset keys occupy up to `B` bits, finding the minimum, subtracting it, shifting keys, and updating growing counters have bit-length-dependent costs. Shifting a Python big integer can copy multiple machine words; `d` also grows with `B`. A conservative bit-operation upper bound includes `O(nL + d(n(B + log(n)) + 256 log(n)))`, apart from input/output conversion. Huge integers therefore do not have a linear-in-`n` guarantee independent of magnitude.

## 12. Space Complexity

At fixed key width, auxiliary container space is O(n + 256), including the scatter buffer and counters; the returned copy also needs O(n) storage. There is no recursion. C++ holds a result vector, a second equally sized value buffer, and 256 counters in addition to the caller's input.

Python additionally holds two key-reference arrays and the offset integer objects. Original integer objects remain shared with the input. Key payload memory depends on their bit lengths, up to O(nB) bits for `B`-bit offset keys, plus O(n) reference slots and counter storage. The two key lists reference the same key objects rather than duplicating their payload on every pass. CLI text and token storage are extra and scale with the input's digit length.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `radix_sort(values)`. It rejects any element for which `type(value) is not int`, including `bool` and subclasses, before the short-input return. Offsetting handles arbitrary negative magnitudes without a fixed-width sign convention. Separate value and key buffers retain the original equal integer objects in stable order. No input mutation or sorting-library call occurs.

The guarded CLI validates ASCII integer syntax and disables Python's decimal conversion digit cap so very large signed tokens can be parsed and printed. Memory and runtime remain bounded by the machine's resources, and work grows with the integer width.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::radix_sort`. A compile-time assertion requires `long long` to cover exactly `[-2^63, 2^63 - 1]`. Conversion to `std::uint64_t` is defined modulo `2^64`, so even the minimum signed value is safe: its mapped key is zero. `-1` maps to `2^63 - 1`, zero to `2^63`, and the maximum signed value to `2^64 - 1`. No absolute value or negation of the minimum is performed.

The eight shifts are 0 through 56, avoiding a shift by the type width. Stable forward scatter writes within prefix-sum ranges. Define `ALGORITHM_ATLAS_NO_MAIN` to include the source in a test driver. The CLI uses strict token checks and `std::from_chars`, detecting malformed or out-of-range input before producing output.

## 15. Input and Output Examples

Run from the **repository root**:

```sh
printf '256 -2 1 -1 0 255\n' | .venv/bin/python dsa/sorting/radix-sort/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/radix-sort/cpp/solution.cpp -o /tmp/atlas-radix-sort
printf '256 -2 1 -1 0 255\n' | /tmp/atlas-radix-sort
```

Each prints:

```text
-2 -1 0 1 255 256
```

Input `9223372036854775807 -9223372036854775808 0` produces `-9223372036854775808 0 9223372036854775807`. Empty input produces a newline. C++20 is available by changing the standard flag. Execute both language suites with:

```sh
.venv/bin/python -m pytest dsa/sorting/radix-sort/tests --require-cpp
```

## 16. Edge Cases

Empty and singleton input return a new container. All-zero, all-equal, negative-only, mixed-sign, repeated, already ordered, and reverse inputs work. Boundary values at 255/256 and later powers of 256 exercise digit transitions. C++ includes the minimum and maximum signed 64-bit values safely. Python additionally handles much wider signed integers.

Malformed CLI syntax includes decimal points, scientific notation, underscores, hexadecimal prefixes, lone signs, and non-ASCII digits. C++ rejects overflow; Python rejects non-native integer API values even in a singleton input. C++ equal integers have no record identity exposed by its value-only API, so stability there follows from forward scattering; Python tests verify distinct equal integer objects retain order.

Tests also include deterministic wide-range randomized differential checks, unchanged input, positive signs/leading zeros, and an integer longer than Python's default decimal conversion limit.

## 17. Advantages

The fixed radix uses only 256 counters regardless of the total value range. Stable passes produce deterministic output without pivot selection or comparison-based search. C++ has eight predictable passes across the entire signed 64-bit domain. Python's offset keys can avoid processing a large shared magnitude when the actual value spread is small.

## 18. Disadvantages and Limitations

Scatter buffers and key storage cost linear memory and repeated passes move substantial data. Small inputs may not justify initializing 256 counters. Python's arbitrary-precision operations can become expensive as keys widen, and conversion of very long decimal tokens has its own cost. The two languages intentionally have different numeric domains and pass counts. These APIs do not support floating-point values, custom records, key callbacks, descending order, strings, GPU processing, or external-memory datasets.

## 19. When to Use It

Consider it when data is already integer-valued, fixed-width processing or a manageable key spread keeps `d` small, stable ordering is useful, and O(n + 256) workspace is affordable. Use this implementation to study stable distribution and signed encodings; measure its performance against standard sorting on the actual workload before choosing it for throughput.

## 20. When Not to Use It

Choose a comparison sort for arbitrary ordered records, a tiny sequence where simpler work dominates, or strict memory limits. Avoid assuming that Python's unbounded integer domain implies constant-cost digits. [Heap Sort](../heap-sort/README.md) offers a constant-space core for comparison data; [Merge Sort](../merge-sort/README.md) supports stable generic ordering with O(n) workspace.

## 21. Comparison With Related Algorithms

| Algorithm | Key requirement | Typical bound | Core workspace | Stable implementation here? |
| --- | --- | --- | --- | --- |
| Radix Sort | Integer digit encoding | Θ(d(n + 256)) in the digit model | O(n + 256) fixed-width words | Yes |
| [Counting Sort](../counting-sort/README.md) | Manageable integer span `k` | O(n + k) | O(n + k) | Depends on reconstruction/record API |
| [Quick Sort](../quick-sort/README.md) | Consistent comparisons | Average O(n log n), worst O(n²) | Depends on partition/stack variant | No |
| [Merge Sort](../merge-sort/README.md) | Consistent comparisons | O(n log n) | O(n) | Yes |

Radix Sort uses a small table repeatedly instead of allocating a table across the entire integer span. Its unit-cost bound depends on digit width; comparison-sort bounds depend on the cost of comparisons. The returned-copy allocation is additional to any constant-space sorting core.

## 22. Interview Questions

1. Why must each LSD pass be stable? Equal current digits must retain the lower-digit ordering already established.
2. Why can ordinary unsigned conversion alone misorder signed data? Negative values wrap above nonnegative values; flipping the high sign position rotates the halves into signed order.
3. Why avoid `abs(LLONG_MIN)`? Its positive magnitude cannot be represented as signed `long long`.
4. Does Radix Sort violate comparison sorting's lower bound? It uses digit structure rather than the comparison-only model.
5. Why does a small Python value spread help even with enormous magnitudes? Subtracting the minimum reduces the number of digit passes, while preprocessing still pays for the original integer widths.

## 23. Practice Problems

1. Reproduce the two Python passes in the dry run, including the starting positions for each nonzero count.
2. Construct a two-digit example where an unstable second pass destroys lower-digit order.
3. Compute mapped C++ keys for `LLONG_MIN`, `-1`, zero, and `LLONG_MAX`; prove monotonicity on both signed halves.
4. As a separate exercise, compare bases 16 and 256 by counting passes and counter initializations; do not assume the larger base always runs faster.
5. Design an extension that moves payload records alongside integer keys while preserving ties. This repository's current public API remains integer-only.

## 24. References

- [NIST Dictionary of Algorithms and Data Structures: Radix Sort](https://xlinux.nist.gov/dads/HTML/radixsort.html) — digit-based sorting and related variants.
- [Princeton Algorithms: LSD.java](https://algs4.cs.princeton.edu/code/edu/princeton/cs/algs4/LSD.java.html) — stable bytewise distribution and signed fixed-width handling in an independent Java implementation.
- [Princeton Algorithms: LSD API documentation](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/LSD.html) — specified key domains and implementation context.

The Python offset encoding and C++ sign-bit mapping here are explained explicitly above; no external benchmark result is claimed for these implementations.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). This original educational implementation and lesson are part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under its [MIT License](../../../LICENSE). See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for contribution and phase approval requirements.

[Sorting category](../README.md) · [Algorithm index](../../../docs/algorithm-index.md) · [Progress](../../../docs/progress.md)
