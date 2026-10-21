# Bubble Sort

## 1. Algorithm Name

**Bubble Sort**, using adjacent exchanges, a shrinking unsorted suffix boundary, and an early exit when a pass makes no swaps. There is no standard abbreviation used here. This is the ordinary forward-pass variant, rather than bidirectional cocktail sorting.

## 2. Overview

Bubble Sort repeatedly compares neighboring values and exchanges an inverted pair. Each forward pass carries a largest remaining value to the right. This implementation returns a new sorted container and preserves the caller's input. It is stable: records with equal ordering keys retain their original relative order.

## 3. Problem Statement

Given a finite sequence of `n` values with a consistent strict ordering, return the same values in nondecreasing order without changing the input. The reusable Python function accepts a `Sequence[T]`; the C++ function accepts `const std::vector<T>&`. Their comparisons use only `<`, so a custom record needs a meaningful less-than operation, not every comparison operator.

The standalone programs accept whitespace-separated signed decimal integers on standard input and print the sorted values separated by spaces, followed by a newline. Python integers have arbitrary precision; the C++ CLI accepts the implementation's `long long` range. The CLI does not take a leading length field.

## 4. Why Do We Need This Algorithm?

It provides a small, inspectable example of ordering, loop invariants, stability, and the difference between an algorithm's worst case and its behavior on already ordered data. Every exchange fixes one adjacent inversion, making correctness and movement visible. The early exit demonstrates how an observation made during work can avoid unnecessary later passes.

## 5. Real-World Applications

- An instructional sorting visualizer can animate each neighboring exchange and highlight the settled suffix.
- A diagnostic tool working on a tiny list can use the simple implementation as a correctness reference against a more complex sorting routine.
- A tiny already ordered sequence can be verified and copied in linear work by the early-exit path.

These are suitability examples, not claims about named production deployments. In ordinary application code, a standard library sort is usually the practical choice.

## 6. Core Intuition

Imagine moving the largest item toward the right by comparing it with its next neighbor. If the next neighbor is smaller, exchange them; otherwise the neighbor is at least as large and becomes the next candidate. After a full pass the last position is settled. Repeat over the shorter prefix. Equal neighbors never cross, which explains stability.

## 7. Prerequisites

Understand sequence indexing, nested loops, swapping, strict comparison, and [asymptotic complexity](../../../docs/complexity-cheatsheet.md). The [glossary](../../../docs/glossary.md) explains stability and auxiliary space. No recursion, heap, or graph knowledge is needed.

## 8. Step-by-Step Working Process

1. Copy the input into the result container.
2. Set `end` to the last index of the unsorted prefix.
3. Scan indices `0` through `end - 1`. Swap only when the right value is strictly smaller than the left value, recording that a swap occurred.
4. The value at `end` is now a maximum of the prefix. Decrease `end` before the next pass.
5. If a pass performed no swaps, stop: every neighboring pair in the prefix is ordered, and the settled suffix is already in its final position.

During a pass, the value at the current right position is a maximum among the values seen so far. Between passes, the suffix beyond `end` contains the largest values in final order. The unsorted prefix shrinks, so the process terminates. Swaps preserve the multiset; the final ordering plus this invariant proves the requested result.

## 9. Pseudocode

```text
BUBBLE_SORT(values):
    result = COPY(values)
    FOR end FROM LENGTH(result) - 1 DOWN TO 1:
        swapped = false
        FOR index FROM 0 TO end - 1:
            IF result[index + 1] < result[index]:
                SWAP(result[index], result[index + 1])
                swapped = true
        IF NOT swapped:
            BREAK
    RETURN result
```

The descending loop is empty for zero or one item. The C++ implementation uses an exclusive boundary to avoid unsigned subtraction on an empty vector; its comparisons and passes are the same.

## 10. Dry Run

Input: `[5, 1, 4, 2]`.

| Pass | Neighbor comparison | State after comparison |
| --- | --- | --- |
| `end = 3` | `5, 1`: swap | `[1, 5, 4, 2]` |
| | `5, 4`: swap | `[1, 4, 5, 2]` |
| | `5, 2`: swap | `[1, 4, 2, 5]` |
| `end = 2` | `1, 4`: keep | `[1, 4, 2, 5]` |
| | `4, 2`: swap | `[1, 2, 4, 5]` |
| `end = 1` | `1, 2`: keep | `[1, 2, 4, 5]` |

The last pass has no swaps and terminates. There are six comparisons and four swaps. The original input remains `[5, 1, 4, 2]` because all exchanges affect the copy.

## 11. Time Complexity

Let `n` be the number of elements; assume comparison, element copying, and swapping each take constant time.

| Case | Time | Explanation |
| --- | --- | --- |
| Best, already ordered | Θ(n) | Copy and one pass of `n - 1` comparisons for `n >= 2` |
| Average, uniformly random distinct permutation | Θ(n²) | The expected number of inversions is `n(n - 1)/4`; each swap removes one |
| Worst, reverse distinct ordering | Θ(n²) | `n(n - 1)/2` comparisons and swaps |

Empty and singleton input take constant time. A few inversions alone do not guarantee linear time: a small value at the far right moves left only one position per pass. For big integers or expensive user comparisons, multiply the comparison and copy counts by their actual costs. CLI parsing/formatting also depends on the number of digits.

## 12. Space Complexity

The sorting loop uses O(1) auxiliary space beyond the result container, with no recursion stack. This API deliberately copies input, so the returned list/vector uses Θ(n) additional container storage for nonempty input. Python copies references to objects; C++ copies elements. Total input-plus-output storage is Θ(n), excluding element payload sizes. The CLI additionally stores its input values, and Python's tokenization stores input text and tokens; these buffers are not included in the sorting-loop bound.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `bubble_sort(values)` and guards the CLI behind `if __name__ == "__main__"`. It makes a shallow list copy and compares only with `<`. Existing objects are reused rather than deep-copied. Do not supply incomparable mixtures or a relation that changes during sorting.

The CLI validates every token against ASCII signed-decimal syntax before sorting, reports malformed input on standard error, and returns nonzero without partial output. It disables Python's decimal digit conversion cap for this command so large integer tokens can be read and printed; memory and processing time remain finite resources.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::bubble_sort<T>(const std::vector<T>&)` using standard headers and C++17 facilities. Types must be copyable, swappable, and less-than comparable. Define `ALGORITHM_ATLAS_NO_MAIN` before including this educational source in a custom driver. Ordinary builds provide the integer CLI. Explicit signed-decimal token checks and range-checked `std::stoll`, including a full-consumption check, reject overflow, trailing characters, and lone signs. Conversion exceptions produce a parse failure. A leading `+` is accepted.

## 15. Input and Output Examples

Run these commands **from the repository root**. Build output goes outside the checkout.

```sh
printf '5 1 4 2\n' | .venv/bin/python dsa/sorting/bubble-sort/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/bubble-sort/cpp/solution.cpp -o /tmp/atlas-bubble-sort
printf '5 1 4 2\n' | /tmp/atlas-bubble-sort
```

Both print exactly:

```text
1 2 4 5
```

Input `3 -2 +1 0 -2` prints `-2 -2 0 1 3`. Empty input prints one newline. C++20 works by replacing `c++17` with `c++20`. Execute the algorithm's Python and C++ tests with:

```sh
.venv/bin/python -m pytest dsa/sorting/bubble-sort/tests --require-cpp
```

## 16. Edge Cases

Empty input returns a new empty container; a singleton is copied unchanged. Equal keys never swap; negative values and zero need no special branch. Ordered input exits after one pass. Reverse input takes the maximum number of swaps. Both CLIs reject `1.2`, `1e3`, `1_000`, `+-1`, and non-ASCII digits. C++ rejects values outside its `long long` range; the Python function supports larger integers. NaN values and inconsistent comparators do not define the ordering required by this API. Generic API comparison errors propagate to the caller.

Tests cover explicit boundaries, 120 deterministic random sequences, unchanged inputs, generic strings, tagged stability, the early-exit comparison count, valid CLIs, malformed tokens, and C++17/C++20 execution.

## 17. Advantages

The state is compact and each step is easy to inspect. Stability follows directly from the strict swap condition. Already ordered input needs only a linear pass, and the core loop requires constant auxiliary storage. No pivot selection, recursion, or distribution assumptions are required.

## 18. Disadvantages and Limitations

Quadratic work and many exchanges make it unsuitable for large unsorted inputs. Stable behavior depends on swapping only strict inversions. The copied-output API has a linear allocation even when the input is already sorted. A sequence may be nearly ordered by inversion count yet still force many passes. This implementation has no key function, descending option, external-memory support, or production optimization claims.

## 19. When to Use It

Use it to teach adjacent inversions, verify a tiny test fixture, inspect every swap, or study adaptive early termination. Choose it when transparency is more valuable than throughput and the list is demonstrably small.

## 20. When Not to Use It

Avoid it for large inputs, costly record moves, or performance-sensitive application sorting. Use [Insertion Sort](../insertion-sort/README.md) for an elementary approach that responds better to many nearly ordered inputs, or [Merge Sort](../merge-sort/README.md) when a stable O(n log n) bound matters. Consider standard library facilities in application code.

## 21. Comparison With Related Algorithms

Here, `n` counts elements; space is core auxiliary space before the copied result.

| Algorithm | Best time | Worst time | Stable here? | Core extra space |
| --- | --- | --- | --- | --- |
| Bubble Sort, early exit | Θ(n) | Θ(n²) | Yes | O(1) |
| [Selection Sort](../selection-sort/README.md) | Θ(n²) | Θ(n²) | No | O(1) |
| [Insertion Sort](../insertion-sort/README.md) | Θ(n) | Θ(n²) | Yes | O(1) |
| [Merge Sort](../merge-sort/README.md) | O(n log n) | Θ(n log n) | Yes | O(n) |

Selection Sort limits swaps to at most `n - 1`, while Bubble Sort can perform quadratic swaps. Merge Sort trades a buffer for a better worst-case bound.

## 22. Interview Questions

1. Why is the final position settled after one forward pass? Identify the running maximum invariant.
2. Why does swapping equal values destroy stability? Give two equal-key records with distinct labels.
3. What does the `swapped` flag prove, and how many comparisons occur on sorted input? It certifies an ordered prefix; the count is `n - 1` for `n >= 2`.
4. Can one displaced value force quadratic time? Trace `[2, 3, 4, 5, 1]` and explain its leftward speed.
5. Is this public API in place? The loop is, but the public function allocates the returned copy.

## 23. Practice Problems

1. Trace all comparisons for `[3, 2, 1]`; verify three swaps and the final order.
2. Count inversions independently and confirm that Bubble Sort performs exactly that many adjacent swaps.
3. Sort labeled records by key and prove their equal-key order is preserved.
4. As a separate exercise, design a last-swap boundary optimization and prove that skipping the later suffix is safe; this lesson does not implement that variant.

## 24. References

- [NIST Dictionary of Algorithms and Data Structures: Bubble Sort](https://xlinux.nist.gov/dads/HTML/bubblesort.html) — adjacent exchange definition, stability, and shrinking-boundary observation.
- [Princeton COS 226: Elementary Sorting Algorithms](https://www.cs.princeton.edu/courses/archive/spr03/cs226/demo/sort/) — educational visualizations of elementary sorting movement.
- [Project development standards](../../../docs/development.md) — reproducibility, testing, and documentation requirements used here.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). This original educational implementation and lesson belong to the [Algorithm Atlas repository](https://github.com/khalidhasan7343/algorithm-atlas) under its [MIT License](../../../LICENSE). Follow [CONTRIBUTING.md](../../../CONTRIBUTING.md) for changes and phase review requirements.

[Sorting category](../README.md) · [Algorithm index](../../../docs/algorithm-index.md) · [Progress](../../../docs/progress.md)
