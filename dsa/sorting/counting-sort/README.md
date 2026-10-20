# Counting Sort

## 1. Algorithm Name

**Counting Sort**, implemented with a frequency array, cumulative counts, and stable output placement. A minimum-key offset supports negative integers. This is the bounded-integer counting method, not a comparison sort or a bucket sorter with arbitrary lists inside each bucket.

## 2. Overview

Counting sort uses integer values as indices into a table of frequencies. Running totals determine where each key's group ends in the result. Scanning the input backward places each occurrence into the final free position for its key.

Its performance depends on the entire span of possible values between the minimum and maximum, including absent values. This implementation guards that span before allocating the count array.

## 3. Problem Statement

Given a sequence of integers, return a new list or vector containing the same values in nondecreasing order. Preserve the input container. Let `k = maximum - minimum + 1` for nonempty input. Require `k <= max_range`, where the default limit is **1,000,000** count slots.

Python exposes `counting_sort(values: Sequence[int], *, max_range: int = 1_000_000) -> list[int]`. Both values and `max_range` must be native Python integers: booleans, integer subclasses, floats, and other types are rejected. `max_range` must be positive even for empty input. Integers can have arbitrary magnitude when their span is acceptable.

C++ exposes `algorithm_atlas::counting_sort(const std::vector<long long>& values, std::size_t max_range = 1000000)`. A zero limit is invalid. The CLI uses the default limit and signed decimal integers; the C++ CLI also requires each value to fit `long long`.

## 4. Why Do We Need This Algorithm?

If keys occupy a small integer interval, comparing pairs repeatedly ignores useful information. Counting each key once and assigning positions from totals can sort in Θ(n + k) time. When `k = O(n)`, that is linear in the number of input values.

This does not contradict the comparison-sorting lower bound: indexing by integer keys is an extra operation outside that model. The cost of the count table must still be included; two values a billion apart are a poor fit even if only two distinct keys occur.

## 5. Real-World Applications

- **Bounded scores or ratings:** integer scores from a documented small scale can be grouped or sorted through one count per possible score.
- **Quantized measurements:** an application with small fixed integer bins can order the quantized codes without pairwise key comparisons. The conversion to bins is a separate modeling decision.
- **Digit processing:** a stable counting pass is useful inside a least-significant-digit radix sorter, where each digit comes from a small alphabet. A digit-key version would attach positions to whole records; this lesson's public API sorts integers directly.
- **Histogram-based ordering:** the frequency stage naturally produces counts, which may also support cumulative distribution calculations. The API here returns the sorted data rather than exposing a histogram.

These are conditions under which the method fits, not claims about a named product's deployment. NIST's [counting-sort entry](https://xlinux.nist.gov/dads/HTML/countingsort.html) describes counting keys and assigning final positions from running totals.

## 6. Core Intuition

Imagine labeled trays for every integer from the smallest key through the largest. First determine how many items belong to each tray. Then add those counts from left to right. The running total for a key is one past the end of that key's segment in the output.

Decrement that total to reserve the last free slot for an occurrence. Working backward through the original sequence reserves later slots for later equal-key occurrences, which preserves their original order.

## 7. Prerequisites

- Arrays, integer indexing, loops, and [complexity notation](../../../docs/complexity-cheatsheet.md).
- Frequencies, prefix sums, and the [meaning of stability](../../../docs/glossary.md).
- The distinction between integer magnitude, key span, and the number of distinct keys.
- For the C++ implementation, signed overflow and modular unsigned arithmetic.

No external runtime package or recursive technique is needed.

## 8. Step-by-Step Working Process

1. Validate the positive range limit. Python also copies the input and validates every element's exact native integer type.
2. Return an empty result for empty input. Otherwise find `minimum` and `maximum`.
3. Compute the inclusive key span safely and reject it when it exceeds the configured limit, before allocating `k` counters.
4. Create `k` zero counts. For each value, increment `counts[value - minimum]`.
5. Accumulate counts left to right. Each entry becomes the number of input items with key less than or equal to its associated key.
6. Allocate an output container with `n` positions. Traverse input from right to left. Decrement its key's cumulative count and place the value at that output index.
7. Return the result without changing the caller's container.

**Correctness:** frequency counting accounts for every input occurrence exactly once. The prefix sum partitions output into consecutive, disjoint segments in increasing key order. Each placement consumes exactly one unused position in its key's segment; no position is duplicated or omitted. Therefore the output is a permutation and is ordered. The backward traversal assigns later equal keys to later positions, giving stable placement. The exposed integer API does not support tagged records, so equal-value record ordering is explained by this placement rule rather than claimed as a tested record API.

## 9. Pseudocode

```text
COUNTING_SORT(values, max_range = 1000000):
    validate max_range is positive
    validate supported integer input types
    if length(values) = 0:
        return []
    minimum = minimum_key(values)
    maximum = maximum_key(values)
    k = safely_compute_inclusive_span(maximum, minimum)
    if k > max_range:
        fail with range error
    counts = array(k, initially 0)
    for value in values:
        counts[value - minimum] += 1
    for j = 1 to k - 1:
        counts[j] += counts[j - 1]
    result = array(length(values))
    for i = length(values) - 1 down to 0:
        offset = values[i] - minimum
        counts[offset] -= 1
        result[counts[offset]] = values[i]
    return result
```

Python uses unbounded integer arithmetic for the span. C++ checks the unsigned distance before adding one; the mathematical subtraction in this pseudocode must not be translated into overflowing signed arithmetic.

## 10. Dry Run

Input: `[2a, -1a, 2b, 0, -1b]`. Tags illustrate occurrence order only; public inputs contain integers. `minimum = -1`, `maximum = 2`, and `k = 4`.

| Key | `-1` | `0` | `1` | `2` |
| --- | ---: | ---: | ---: | ---: |
| Offset | 0 | 1 | 2 | 3 |
| Frequency | 2 | 1 | 0 | 2 |
| Cumulative count | 2 | 3 | 3 | 5 |

The zero-frequency key `1` still occupies a counter because the span is inclusive.

| Backward input occurrence | Count decremented | Output position | Output after placement |
| --- | --- | ---: | --- |
| `-1b` | `counts[0]: 2 → 1` | 1 | `[_, -1b, _, _, _]` |
| `0` | `counts[1]: 3 → 2` | 2 | `[_, -1b, 0, _, _]` |
| `2b` | `counts[3]: 5 → 4` | 4 | `[_, -1b, 0, _, 2b]` |
| `-1a` | `counts[0]: 1 → 0` | 0 | `[-1a, -1b, 0, _, 2b]` |
| `2a` | `counts[3]: 4 → 3` | 3 | `[-1a, -1b, 0, 2a, 2b]` |

Removing illustrative tags gives the tested result `[-1, -1, 0, 2, 2]`.

## 11. Time Complexity

Let `n` be the number of input items and `k = maximum - minimum + 1` for an accepted nonempty input. Assume constant-time bounded integer arithmetic, indexing, and element assignments.

| Case | Runtime | Reason |
| --- | --- | --- |
| Best, average, and worst for fixed accepted `n` and `k` | Θ(n + k) | Scan/count/place `n` items and initialize/accumulate `k` counts |
| All keys equal | Θ(n) | `k = 1` |
| Empty input | O(1) | Limit validation followed by empty return |
| Input rejected for excessive span | O(n) | Validate/scan before rejecting; no count table allocated |

Initial order does not change how many frequency and placement operations are performed. There is no separate random-distribution assumption needed for the bound. Calling it O(n) requires stating that `k = O(n)` or that the key domain is a fixed constant.

Python arbitrary-precision subtraction, comparison, parsing, and formatting depend on integer bit length; the element-operation bound does not claim constant time for arbitrarily long integers. CLI text processing also depends on the input's byte length.

## 12. Space Complexity

The count array needs O(k) slots and the returned result needs O(n) slots: **O(n + k) additional space**, or Θ(n + k) for accepted nonempty inputs in the usual slot model. Python also keeps an O(n) shallow input copy; C++ reads directly from the const input vector. These choices do not change the bound. There is no recursive stack.

The default guard caps count-table length at 1,000,000; it does not cap input length or guarantee enough free memory. In C++, each counter is `std::size_t`, often eight bytes. Python counter objects and list references use more storage than a compact byte array. Raising `max_range` deliberately permits larger allocations and is the caller's resource decision.

## 13. Python Implementation

Source: [python/solution.py](python/solution.py).

The function validates `type(value) is int`, deliberately excluding `bool` and subclasses. A keyword-only `max_range` makes a changed allocation limit explicit. Python computes the span without integer overflow, then checks it before creating the count list. The input is copied before processing and returned output is separate.

No built-in sorting function performs the task. Frequency counting, prefix accumulation, and reverse placement implement the algorithm directly. The CLI disables the decimal conversion digit guard when run as a script, allowing very large nearby Python integers subject to memory limits.

## 14. C++ Implementation

Source: [cpp/solution.cpp](cpp/solution.cpp).

The API returns `std::vector<long long>` and uses `std::vector<std::size_t>` for counts. It validates `max_range` before checking whether the input is empty. Zero throws `std::invalid_argument`; an excessive inclusive span throws `std::length_error`.

**Signed-boundary safety:** evaluating `maximum - minimum` as signed arithmetic can overflow. Instead, both endpoints are converted to the unsigned counterpart of `long long`, then subtracted. Because `maximum >= minimum`, modular subtraction represents their nonnegative distance exactly in that unsigned domain. A distance equal to its unsigned maximum cannot be incremented safely. The code rejects that case and any distance `>= max_range` before adding one or allocating. Each key offset is computed by the same unsigned method.

Thus values near `LLONG_MIN` or `LLONG_MAX` work when close together; the pair containing both extremes is rejected safely. Prefix sums never exceed input size, which is representable by the vector's size type. Define `ALGORITHM_ATLAS_NO_MAIN` to include the source in an API driver. Both C++17 and C++20 are supported.

## 15. Input and Output Examples

Run **from the repository root**. Python requires Python 3.11+ with no third-party runtime package; C++ requires a supporting compiler.

```sh
printf '2 -1 2 0 -1\n' | python3 dsa/sorting/counting-sort/python/solution.py
# Output: -1 -1 0 2 2

c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/counting-sort/cpp/solution.cpp -o /tmp/atlas-counting-sort
printf '2 -1 2 0 -1\n' | /tmp/atlas-counting-sort
# Output: -1 -1 0 2 2

printf '+3 -0 -7\n' | /tmp/atlas-counting-sort
# Output: -7 0 3

printf '0 1000000\n' | /tmp/atlas-counting-sort
# Nonzero exit, error on stderr, no stdout: inclusive span is 1000001.
```

There is no length prefix and the CLI has no range-limit flag. Use the reusable API to customize `max_range`. Empty input prints one empty line. To execute algorithm tests and compile/run both C++ standards:

```sh
.venv/bin/python -m pytest dsa/sorting/counting-sort/tests --require-cpp
```

Tests include known answers, deterministic random comparisons against a test-only sorting oracle, preserved inputs, negative offsets, close signed extremes, full-domain rejection, exact limit boundaries, custom limits, type errors, and valid/invalid CLIs. Tagged records are outside this integer API.

## 16. Edge Cases

| Condition | Result |
| --- | --- |
| Empty input with a positive valid limit | Empty copied result; CLI prints newline |
| Zero or negative Python limit | `ValueError`, including empty input |
| Non-native Python integer limit | `TypeError`, including `True` |
| C++ zero limit | `std::invalid_argument`, including empty input |
| Single key or all equal keys | One count slot, regardless of absolute magnitude |
| Negative values spanning zero | Offset maps minimum to index zero |
| `k == max_range` | Accepted |
| `k == max_range + 1` | Rejected before count allocation |
| Close values near signed extremes | Accepted when span fits |
| `LLONG_MIN` and `LLONG_MAX` together | Safely rejected as excessive span |
| Python bool, float, string, or integer subclass in API input | `TypeError`; input unchanged |
| Malformed CLI token, such as `1.5` or `1_000` | Nonzero exit, stderr error, no partial stdout |
| Integer beyond C++ `long long` range | CLI rejects with nonzero exit |

CLI syntax is an optional single `+` or `-` followed by ASCII decimal digits. Python's CLI can accept huge nearby integers; C++ cannot exceed its element type. Resource exhaustion is not a successful partial sort. A `std::size_t` limit cannot express a negative limit; callers must validate signed values before conversion rather than pass a converted negative number.

## 17. Advantages

- Θ(n + k) work gives linear sorting when the integer span is sufficiently small.
- Duplicate-heavy bounded keys are handled by simple frequency increments.
- Stable output placement is suitable as a model for digit-key counting passes.
- Negative and large-magnitude nearby integers need only a small offset table.
- The explicit limit prevents accidental count-table allocation from a very wide span.

## 18. Disadvantages and Limitations

- Sparse wide intervals waste counters; few distinct keys alone do not make this method efficient.
- O(n + k) storage can exceed a comparison sort's memory needs.
- The API supports integer values, not arbitrary comparable objects or keyed records.
- The default limit is a practical guard, not an algorithmic universal constant or a memory-availability promise.
- The default CLI rejects broad ranges even when a different sorting method could handle them easily; it does not silently switch algorithms.
- Python permits unbounded integer magnitudes but their arithmetic and text conversion are not constant-cost.

## 19. When to Use It

Use it when the keys are integers, the inclusive span is known to be small enough for a dense counter table, and preserving the input is desirable. Estimate both `n` and `k`, not just the number of distinct values. A bounded score scale or a compact set of quantized measurement codes is a natural candidate.

## 20. When Not to Use It

Choose another method for generic strings or records without integer key extraction, enormous sparse intervals, or strict memory budgets. Sorting two very distant integers needs only a comparison; allocating a table across their gap would be wasteful. For data that cannot fit in memory, use a design addressing external storage rather than raising this guard blindly.

## 21. Comparison With Related Algorithms

| Method | Typical domain | Time model | Additional space | Selection criterion |
| --- | --- | --- | --- | --- |
| Counting sort here | Integers in span `k` | Θ(n + k) | O(n + k) | Dense, affordable key interval |
| [Insertion sort](../insertion-sort/README.md) | Comparable elements | Θ(n + I), `I` inversions | O(n) here due to returned copy | Small or nearly ordered input |
| [Heap sort](../heap-sort/README.md) | Comparable elements | O(n log n) worst-case guarantee | O(n) here due to returned copy | Wide ranges with predictable comparison bounds |
| [Merge sort](../merge-sort/README.md) | Comparable elements | Θ(n log n) standard top-down | O(n) | Stable sorting independent of integer span |
| [Radix sort](../radix-sort/README.md) | Digit-decomposable keys | O(d(n + b)) for `d` passes and base `b` | O(n + b) for a usual stable pass | Wide keys decomposable into small digit domains |

The linked lessons define their exact implementation choices. A frequency-only reconstruction can produce sorted integers too, but this implementation retains the cumulative-position method to teach stable placement.

## 22. Interview Questions

1. **Why is the span `maximum - minimum + 1`?** Both endpoints need slots; a difference of five covers six integer values.
2. **Why do negative keys work?** Subtracting the minimum maps the smallest key to zero and preserves order.
3. **Why traverse backward when decrementing end positions?** Later equal-key occurrences must receive later positions.
4. **Does this violate an Ω(n log n) lower bound?** That bound applies to general comparison sorting; counting uses key-indexed access.
5. **Why reject full signed-domain endpoints before subtraction?** Signed subtraction could overflow, and the required table would be unreasonable.
6. **Is a small number of distinct keys sufficient?** No; this dense table pays for every integer in the span.

## 23. Practice Problems

1. Compute frequencies and cumulative positions for `[-2, 1, -2, 0, 1]`, then reproduce the backward placement trace.
2. Give two ten-element inputs with the same number of distinct keys but dramatically different spans. Explain the memory difference.
3. Extend a separate exercise implementation to keyed records, then test equal-key tag order. Define the new API rather than passing records into this integer-only function.
4. Compare a histogram reconstruction variant with stable prefix placement. Count storage and explain when identity information matters.
5. Design a caller-side policy choosing between dense counting and a comparison sort using a memory budget. Keep that policy explicit rather than silently hiding rejected spans.

## 24. References

- NIST Dictionary of Algorithms and Data Structures, [Counting Sort](https://xlinux.nist.gov/dads/HTML/countingsort.html) — frequency counting and final positions from cumulative counts.
- Pat Morin, [Open Data Structures, section 11.2: Counting Sort and Radix Sort](https://opendatastructures.org/versions/edition-0.1/ods-java.pdf) — stable counting and its relationship to radix sorting.
- Virginia Tech OpenDSA, [Binsort](https://opendsa-server.cs.vt.edu/ODSA/Books/unp/inf1-62-4001/spring-2025/FTK102/html/BinSort.html) — integer-indexed sorting and key-domain considerations.

The negative offset, strict native-integer Python contract, explicit default range guard, and C++ overflow checks are implementation decisions documented by this lesson.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). Follow the [contribution standards](../../../CONTRIBUTING.md); code and documentation use the repository's [MIT License](../../../LICENSE).

[Sorting category](../README.md) · [Project home](../../../README.md) · [Progress](../../../docs/progress.md)
