# Bucket Sort

## 1. Algorithm Name

**Bucket Sort**, using equal-width buckets on the closed unit interval and stable insertion sorting inside each bucket. This is a distribution sort; it differs from counting exact integer frequencies and from repeatedly processing digits in Radix Sort. No abbreviation is used.

## 2. Overview

Divide a known value range into ordered intervals, place each input value into its interval's bucket, sort the smaller buckets, and concatenate them. If values spread evenly and the bucket count is proportional to the number of items, the expected work is linear. Concentrated, adversarial input can require quadratic work. Both implementations preserve the input and return a new sorted container.

## 3. Problem Statement

Sort finite real values in **[0, 1], including both endpoints**, into ascending order. Python exposes `bucket_sort(values: Sequence[float], *, bucket_count: int | None = None) -> list[float]`. Native `float` and native `int` values are accepted; booleans, numeric subclasses, strings, and other numeric types are rejected. Only integer 0 and 1 satisfy the range. Original values and Python object identities are preserved.

C++ exposes `algorithm_atlas::bucket_sort(const std::vector<double>&, std::size_t bucket_count = 0)`. Python's `None` and C++'s zero choose `k = max(1, n)` automatically. An explicit Python count must be a positive native integer fitting `sys.maxsize`; C++ counts are nonnegative `size_t`, with zero reserved for automatic selection. The CLI reads decimal/scientific real tokens, unlike the integer-only CLIs of most other sorting lessons. No leading length is expected.

## 4. Why Do We Need This Algorithm?

Known numeric ranges provide information that generic comparisons do not exploit. A simple arithmetic map can separate distant values immediately, leaving only local ordering work. Bucket Sort demonstrates why an input-distribution assumption can improve expected performance without improving the worst case. The choice of bucket count exposes a concrete tradeoff between overhead and the size of each local sorting problem.

## 5. Real-World Applications

- Already normalized measurement values can be sorted by dividing their known unit range into small intervals, provided the distribution is suitable.
- Probability-valued scores can be arranged for subsequent inspection or grouping while retaining equal-score order. Large masses at a few scores need separate performance consideration.
- Sorting visualizers and teaching tools can show how distribution changes workload even when two inputs have the same size and range.

These are workload examples, not assertions about named deployments. Raw measurements require a justified normalization policy before using this particular API; the implementation does not silently rescale arbitrary data.

## 6. Core Intuition

If one bucket contains only smaller intervals and another contains larger intervals, values in the first bucket never need to be compared with values in the second. All remaining ambiguity is local. Stable insertion sorting resolves that ambiguity inside each bucket. Appending bucket 0, then bucket 1, and so on produces the global order.

For `0 <= x <= 1`, the intended map is `min(k - 1, floor(x * k))`. The minimum ensures the inclusive endpoint 1 belongs to the final bucket. Floating-point multiplication can round near an interval boundary; the clamped index remains nondecreasing with the input value, and sorting each bucket preserves correctness.

## 7. Prerequisites

Understand arrays, nested containers, index arithmetic, and [Insertion Sort](../insertion-sort/README.md). Review [complexity analysis](../../../docs/complexity-cheatsheet.md), especially expected versus worst-case bounds, and [stability](../../../docs/glossary.md). The expected-time argument additionally assumes independent uniformly distributed input values.

## 8. Step-by-Step Working Process

1. Copy the input; determine and validate the bucket count and numeric domain.
2. Return the copy immediately for fewer than two values, after validation.
3. Allocate `k` empty buckets.
4. Compute each value's clamped bucket index and append it. Original order within a bucket is preserved during distribution.
5. For each bucket, run insertion sort. Move an earlier value right only when the current value is strictly smaller, so equal values never cross.
6. Concatenate buckets in index order into the result and return it.

During insertion, the processed prefix of a bucket is sorted and retains equal-value order. Inserting the next value extends that invariant. The bucket map is nondecreasing, so every value in an earlier bucket is no greater than every value in a later bucket. Sorted local buckets therefore concatenate into a sorted whole. Distribution and local rearrangement preserve every original value and its multiplicity. Equal values map to the same bucket and insertion is stable, proving global stability.

## 9. Pseudocode

```text
BUCKET_SORT(values, optional_count):
    result = COPY(values)
    k = optional_count, or MAX(1, LENGTH(result))
    VALIDATE_COUNT_AND_DOMAIN(k, result)
    IF LENGTH(result) < 2: RETURN result
    buckets = k empty lists
    FOR value IN result, from left to right:
        index = MIN(k - 1, FLOOR(value * k))
        APPEND value TO buckets[index]
    CLEAR result
    FOR bucket IN buckets, in index order:
        FOR index FROM 1 TO LENGTH(bucket) - 1:
            value = bucket[index]
            position = index
            WHILE position > 0 AND value < bucket[position - 1]:
                bucket[position] = bucket[position - 1]
                position -= 1
            bucket[position] = value
        APPEND ALL bucket values TO result
    RETURN result
```

The C++ implementation checks/clamps the floating result before converting to `size_t`, then clamps the integer index again. This prevents an out-of-range floating-to-integer conversion at extreme requested bucket counts and handles the inclusive upper endpoint safely.

## 10. Dry Run

Input: `[0.42, 0.17, 0.39, 0.26, 0.72, 0.94, 1.0]`; choose `k = 4`.

| Bucket | Intended interval | Values after distribution |
| --- | --- | --- |
| 0 | `[0, 0.25)` | `[0.17]` |
| 1 | `[0.25, 0.5)` | `[0.42, 0.39, 0.26]` |
| 2 | `[0.5, 0.75)` | `[0.72]` |
| 3 | `[0.75, 1]` | `[0.94, 1.0]` |

Inside bucket 1, insert 0.39 by shifting 0.42 right: `[0.39, 0.42, 0.26]`. Then insert 0.26 by shifting 0.42 and 0.39: `[0.26, 0.39, 0.42]`. Bucket 3 is already ordered; comparing 1.0 with 0.94 makes no shift. Concatenating produces `[0.17, 0.26, 0.39, 0.42, 0.72, 0.94, 1.0]`. The original input is unchanged. For 1.0, `floor(1.0 * 4)` is 4, and clamping changes the index to 3.

## 11. Time Complexity

Let `n` be the number of values, `k` the bucket count, `n_i` the occupancy of bucket `i`, and `I` the total number of inversions inside the distributed buckets. For `n >= 2`, initializing, distributing, and collecting costs Θ(n + k). Stable insertion sorting costs Θ(n + I) across the buckets. The order-sensitive total is therefore **Θ(n + k + I)**, with upper bound **O(n + k + Σ n_i²)**.

| Case | Time | Conditions |
| --- | --- | --- |
| Best | Θ(n + k) | Every bucket is already ordered, including equal-only data |
| Expected | Θ(n + k + n²/k) | Independent uniform continuous values on the unit interval, in the ideal arithmetic model |
| Worst | Θ(n² + k) | Distinct reverse-ordered values concentrate in one bucket |

For uniform input, `E[Σ n_i²] = n + n(n - 1)/k`; random relative order inside a bucket supplies the matching expected inversion cost. With default `k = n`, expected time is Θ(n), while worst-case time remains Θ(n²). With `k = 1`, it becomes insertion sorting of the entire input. Extremely large `k` increases initialization and empty-bucket scanning even when input is small.

The exact Θ(Σ n_i²) claim would be incorrect for every input: all equal values share a bucket but cause no shifts. Clustering can increase local work, especially with descending distinct values. Endpoint atoms and other discrete masses violate the continuous-uniform expectation; repeated equal keys alone do not force quadratic insertion work. Floating-point rounding perturbs ideal interval boundaries. Empty and singleton inputs return after validation without allocating or scanning `k` buckets.

## 12. Space Complexity

The bucket array uses O(k) container headers and O(n) stored references/values. The returned copy uses another O(n) container storage, so total additional space is O(n + k); the insertion loop inside one bucket uses O(1) auxiliary space. There is no recursion. Python reuses original immutable numeric objects, while C++ stores copied `double` values. Dynamic container spare capacity adds constant-factor overhead under ordinary allocation behavior.

The CLI additionally holds input text/tokens in Python or its input vector in C++. Requested bucket counts are not a promise that enough memory exists: Python can raise `MemoryError`, and C++ can throw `std::length_error` or `std::bad_alloc`. No arbitrary small allocation cap is imposed.

## 13. Python Implementation

[python/solution.py](python/solution.py) accepts a sequence and an optional keyword-only count. It validates values before its short-input return and deliberately accepts only exact native integer/float types. Domain validation precedes `math.isfinite` so an enormous out-of-range integer is rejected with `ValueError` rather than overflowing a float conversion. Native integer endpoints and floating signed zero retain their identities and order in the result.

Each bucket is sorted by the explicit insertion loop in the source; no built-in sorting routine is used. The guarded CLI validates decimal/scientific token syntax and catches domain errors to emit a concise message without a traceback or partial output.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) provides a reusable vector function with zero as the automatic-count sentinel. Invalid finite-range inputs throw `std::invalid_argument`. Buckets are vectors; insertion uses explicit shifts and strict `<`. Index calculation clamps before a potentially unsafe cast, including when converting an enormous count to floating point rounds its endpoint.

Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a custom driver. Normal builds provide a standalone CLI. Its small decimal grammar rejects non-decimal and malformed strings before `std::strtod`; the standalone process uses the default C numeric locale. Finite subnormal values are accepted. Standard headers support C++17 and C++20, with no third-party dependency.

## 15. Input and Output Examples

From the **repository root**, run:

```sh
printf '1 .5 0 2.5e-1 +7.5E-1\n' | .venv/bin/python dsa/sorting/bucket-sort/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/bucket-sort/cpp/solution.cpp -o /tmp/atlas-bucket-sort
printf '1 .5 0 2.5e-1 +7.5E-1\n' | /tmp/atlas-bucket-sort
```

Both produce:

```text
0 0.25 0.5 0.75 1
```

Input `-0 +0.0 1.` produces `-0 0 1`. Empty input produces one newline. Output uses 17 significant digits, so decimal values may print their binary floating approximation rather than their original spelling. API callers can supply a custom count; the CLI always uses the default. C++20 builds replace `c++17` with `c++20`. Run all dedicated tests using:

```sh
.venv/bin/python -m pytest dsa/sorting/bucket-sort/tests --require-cpp
```

## 16. Edge Cases

Zero and one belong to the first and last bucket respectively; negative zero compares equal to positive zero and is accepted. Stable order preserves their signs. Values immediately below one, immediately around a bucket boundary, and positive subnormals remain valid. NaN, infinities, values below zero, and values above one are rejected by the API. All equal, ordered, reverse, and clustered inputs sort correctly even when their costs differ.

The CLI accepts decimal points and scientific notation, but rejects underscores, hexadecimal syntax, non-ASCII digits, `nan`, `inf`, lone signs, and incomplete exponents. It interprets tokens as machine floating values before checking the domain: ordinary rounding and underflow-to-zero can occur, including signed zero, and this is not exact decimal arithmetic. Overflow to infinity is rejected. Python's count zero is invalid; C++'s count zero requests automatic selection. Invalid Python counts are rejected even for empty input.

Tests verify boundaries, custom counts, object identity and signed-zero stability, seeded uniform data, reverse clustered data, malformed input, invalid types/counts, allocation-range failure in C++, and actual C++17/C++20 execution.

## 17. Advantages

Under suitable distribution assumptions, small buckets reduce the number of local comparisons and can yield expected linear work. The bucket count is explicit and adjustable. Stable insertion inside each bucket preserves ties. Numeric-domain checks and endpoint clamping make the chosen scope predictable, and the copied result leaves the caller's data available for comparison.

## 18. Disadvantages and Limitations

Performance depends on both distribution and local ordering. The method requires a known finite unit range, linear bucket storage, and potentially many empty container allocations. Descending clustered values degrade to quadratic insertion work. Floating values represent rounded machine numbers, not exact real arithmetic. This implementation does not normalize other ranges, sort arbitrary records, supply a key callback, adapt bucket boundaries to observed density, or guarantee production performance.

## 19. When to Use It

Consider it for already normalized finite data with a defensible roughly uniform distribution, enough workspace, and a bucket count scaled to input size. It is especially useful for studying how probabilistic assumptions and local inversion counts affect runtime. Measure bucket occupancy and application performance before choosing it for a real processing pipeline.

## 20. When Not to Use It

Avoid this implementation for arbitrary integer ranges, unnormalized data, NaNs, unknown or strongly clustered distributions, expensive container allocation, or strict worst-case timing requirements. [Merge Sort](../merge-sort/README.md) gives stable generic ordering with an O(n log n) bound; [Heap Sort](../heap-sort/README.md) offers a constant-space core. [Radix Sort](../radix-sort/README.md) is a different distribution strategy for integer digits.

## 21. Comparison With Related Algorithms

| Algorithm | Required structure | Time characteristic | Core extra storage | Stable here? |
| --- | --- | --- | --- | --- |
| Bucket Sort | Finite values in [0, 1] | Expected Θ(n) with default buckets and uniform data; worst Θ(n²) | O(n + k) | Yes |
| [Counting Sort](../counting-sort/README.md) | Manageable integer span | O(n + span) | O(n + span) | Value-only integer API |
| [Radix Sort](../radix-sort/README.md) | Integer digits | Θ(d(n + 256)) in the digit model | O(n + 256), fixed-width | Yes |
| [Insertion Sort](../insertion-sort/README.md) | Consistent comparisons | Best Θ(n), worst Θ(n²) | O(1) beyond returned copy | Yes |
| [Merge Sort](../merge-sort/README.md) | Consistent comparisons | O(n log n) | O(n) | Yes |

Bucket Sort distributes once and compares within intervals. Radix Sort distributes repeatedly by digit. Counting Sort counts exact discrete keys. Their assumptions and memory costs differ despite the shared use of distribution.

## 22. Interview Questions

1. Why is one clamped into the last bucket? The unadjusted index equals `k`, outside the allocated range.
2. Why is concatenation sufficient after local sorting? The bucket-index map is nondecreasing.
3. Does one heavily occupied bucket always imply quadratic work? No; equal or already ordered values produce linear insertion work.
4. Which assumptions establish expected linear time? Independent uniform continuous input and `k` proportional to `n`, with constant-cost arithmetic/allocation operations.
5. How is stability obtained? Append in input order and shift only strict inversions inside each bucket.
6. Why must NaN be rejected? It does not satisfy an ordinary total numeric ordering or a meaningful unit-interval bucket index.

## 23. Practice Problems

1. Trace `[0.6, 0.1, 1.0, 0.4, 0.0]` with two buckets and record each local insertion shift.
2. Compare one bucket, `n` buckets, and `2n` buckets on the same uniform sample by measuring occupancies and shifts.
3. Construct descending distinct values that all map to one bucket, then contrast their work with all equal values.
4. Derive `E[Σ n_i²]` by counting individual memberships and pairs that land together.
5. As an independent exercise, design a documented normalization policy for another known interval and analyze rounding; this implementation keeps the explicit [0, 1] contract.

## 24. References

- [NIST Dictionary of Algorithms and Data Structures: Bucket Sort](https://xlinux.nist.gov/dads/HTML/bucketsort.html) — distribution into range-based buckets and collection.
- [NIST: Distribution Sort](https://xlinux.nist.gov/dads/HTML/distributionSort.html) — the broader distribute-and-gather family.
- [UC San Diego CSE 202: Sorting in Expected Linear Time](https://cseweb.ucsd.edu/classes/sp11/cse202-a/lecture16-final.pdf) — expected-time sorting under uniform-range assumptions.
- [Upper Tail Analysis of Bucket Sort and Random Tries](https://arxiv.org/abs/2002.10499) — research on deviations from bucket sorting's expected linear behavior.

The finite closed interval, stable insertion loops, endpoint policy, and API validation are the specific implementation choices explained in this lesson.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). This original educational lesson and implementation are part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under its [MIT License](../../../LICENSE). Contribution and phase review requirements are in [CONTRIBUTING.md](../../../CONTRIBUTING.md).

[Sorting category](../README.md) · [Algorithm index](../../../docs/algorithm-index.md) · [Progress](../../../docs/progress.md)
