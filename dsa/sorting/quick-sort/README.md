# Quick Sort

## 1. Algorithm Name

**Quick Sort (Quicksort)** — deterministic middle-pivot, three-way partitioning with smaller-side recursion. This is not randomized quicksort or introsort. The canonical implementation also serves the [Divide and Conquer category](../../divide-and-conquer/README.md).

## 2. Overview

Quicksort rearranges elements around a pivot, then orders the portions on either side. Three-way partitioning groups keys smaller than, equivalent to, and greater than the pivot. The equivalent group needs no further sorting. Both implementations return a new container and leave the input unchanged; equal-key records may change relative order.

## 3. Problem Statement

Given `n` elements with a consistent strict ordering under `<`, return a nondecreasing permutation. Python accepts `Sequence[T]` and returns `list[T]`; C++ accepts `const std::vector<T>&` and returns `std::vector<T>`. Python copies references, not element objects. C++ elements must support copying, assignment, and swapping. Comparisons must not mutate elements.

The standalone CLIs read whitespace-separated signed decimal integers, without a length prefix, and print one sorted line. Python supports arbitrary-precision integers subject to resources. The C++ CLI uses the platform's `long long` range, commonly signed 64-bit. The generic library APIs support other consistently comparable types, including strings and records.

## 4. Why Do We Need This Algorithm?

A partition can put many elements on their correct side of a pivot without maintaining a separate merge buffer. Repeating this decomposition often gives efficient comparison sorting on in-memory data. Three-way partitioning also avoids repeatedly processing a large group of equal keys.

Quicksort teaches how pivot choice, duplicate handling, and recursion strategy affect separate guarantees: a bounded stack does not imply a bounded worst-case runtime.

## 5. Real-World Applications

- **In-memory batch ordering:** order a collected set of numeric or textual keys before a scan, deduplication, or rank presentation when equal-key order does not matter.
- **Duplicate-heavy records:** ordering by a low-cardinality field can leave large equivalent groups; three-way partitioning removes those groups from later recursion.
- **Memory-conscious comparison sorting:** its partition core avoids a linear merge buffer, although this particular public API allocates a returned copy.

These are workload examples, not claims that a named service uses this code. Untrusted adversarial input or a strict latency bound calls for a sorter with a stronger worst-case guarantee; this educational implementation has no introspective fallback.

## 6. Core Intuition

Imagine dividing cards into three regions relative to one selected card: lower, same rank, and higher. Once every card is classified, only the lower and higher regions still need work. Keep the pivot value separately so swapping its original array position cannot change the reference value.

Process the smaller outer region through recursion, and use a loop for the larger region. This keeps the active call stack small even when the pivot splits very unevenly.

## 7. Prerequisites

Arrays, half-open index ranges, swaps, recursion, and a consistent comparison ordering. Review [complexity notation](../../../docs/complexity-cheatsheet.md) and [invariants and stability](../../../docs/glossary.md). [Merge Sort](../merge-sort/README.md) offers a useful alternative divide-and-conquer example.

## 8. Step-by-Step Working Process

1. Copy the input. Work on a half-open interval `[start, end)`; lengths zero or one are already sorted.
2. Save the middle-position value as the pivot. Initialize `lower = current = start` and `upper = end`.
3. Maintain four regions: `[start, lower)` is less than the pivot; `[lower, current)` is equivalent; `[current, upper)` is unknown; `[upper, end)` is greater.
4. If the current value is smaller, swap it with `lower` and advance both indices. If greater, decrement `upper` and swap with that position; inspect the newly received value next. Otherwise advance `current` only.
5. When `current == upper`, the unknown region is empty. The middle region is final.
6. Recursively sort the smaller outer region; continue the larger region by adjusting the interval in the loop.
7. Return the copied container.

Each partition step shrinks the unknown region. The saved pivot is an element of the interval, so at least one equivalent element is removed from recursive work. The region invariant establishes ordering between the three groups; induction establishes ordering within each outer group. Swaps preserve the multiset, so the final result is a sorted permutation.

## 9. Pseudocode

```text
QUICK_SORT(values):
    result = copy(values)
    SORT_RANGE(0, length(result))
    return result

SORT_RANGE(start, end):
    while end - start > 1:
        pivot = result[start + floor((end - start) / 2)]
        lower = current = start
        upper = end
        while current < upper:
            if result[current] < pivot:
                swap(result[lower], result[current])
                lower += 1
                current += 1
            else if pivot < result[current]:
                upper -= 1
                swap(result[current], result[upper])
            else:
                current += 1
        if lower - start < end - upper:
            SORT_RANGE(start, lower)
            start = upper
        else:
            SORT_RANGE(upper, end)
            end = lower
```

The pivot is a saved value/reference to the original element, not an alias to an array slot that changes during swaps. Comparisons use `<` in both directions; an equality operator is unnecessary.

## 10. Dry Run

Input `[4a, 2, 4b, 1, 3]`; the tags distinguish equivalent keys. The middle pivot is `4b`.

| Action | Array | `lower, current, upper` |
| --- | --- | --- |
| Initialize | `[4a, 2, 4b, 1, 3]` | `0, 0, 5` |
| `4a` equivalent: advance | `[4a, 2, 4b, 1, 3]` | `0, 1, 5` |
| `2` smaller: swap with index 0 | `[2, 4a, 4b, 1, 3]` | `1, 2, 5` |
| `4b` equivalent: advance | `[2, 4a, 4b, 1, 3]` | `1, 3, 5` |
| `1` smaller: swap with index 1 | `[2, 1, 4b, 4a, 3]` | `2, 4, 5` |
| `3` smaller: swap with index 2 | `[2, 1, 3, 4a, 4b]` | `3, 5, 5` |

The equivalent region `[3, 5)` is finished. The smaller right region is empty, so its call immediately returns; the loop continues on `[0, 3)`. Its middle pivot `1` produces `[1, 3, 2, 4a, 4b]`, with `1` fixed. The remaining `[3, 2]` interval has pivot `2` and becomes `[2, 3]`. Final result: `[1, 2, 3, 4a, 4b]`.

This example preserves the two fours by chance. It does not establish stability: `[2a, 1b, 2c]` instead becomes `[1b, 2c, 2a]`, an explicit instability case checked in both languages.

## 11. Time Complexity

Let `n` be the element count. Assume constant-time comparisons, copies, and swaps. A partition of `m` elements performs Θ(m) work and at most two `<` comparisons per examined element.

| Setting | Time | Reason |
| --- | --- | --- |
| Best with duplicates: all keys equivalent | Θ(n) | One partition consumes the whole interval |
| Balanced splits of distinct keys | Θ(n log n) | Linear work across each of logarithmically many levels |
| Average over uniformly random permutations of distinct keys | Θ(n log n) | Average pivot ranks yield the standard quicksort recurrence |
| Worst, adversarial middle-pivot ranks | Θ(n²) | Repeated very unbalanced partitions incur a decreasing linear sum |

There is no random shuffle or randomized guarantee in this implementation. Choosing the middle **position** does not guarantee a median **value**. Smaller-side recursion improves stack usage, not the quadratic worst-case bound. Empty input has constant overhead. Big-integer comparisons and expensive element copies require their own cost factors; text parsing is separate.

## 12. Space Complexity

The partition uses constant extra element slots. Smaller-side recursion has **O(log n) worst-case stack depth**, since every nested nontrivial call has at most half as many elements as its parent. The larger interval is handled iteratively. All-equivalent input uses constant stack depth.

The public API also allocates an **O(n) returned copy**. Thus additional memory relative to the caller's input is O(n), including stack; total input-plus-output storage is O(n). Python stores references; C++ stores element copies and one saved pivot per active frame. CLI token/text storage depends on the textual input size. There is no linear partition buffer.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `quick_sort(values)`. A nested helper operates on index ranges in one copied list. It never slices subarrays or calls Python's built-in sorting functions. Records need only a consistent `__lt__` method; equivalent keys are detected by neither direction being smaller. Importing the file does not run its CLI.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::quick_sort<T>`. A saved pivot prevents aliasing bugs during swaps. Half-open ranges allow the empty and singleton cases without subtracting from zero. Define `ALGORITHM_ATLAS_NO_MAIN` before including the file in an API test driver. The standalone entry point validates ASCII decimal token grammar and uses `std::from_chars` for range-checked conversion. All headers are standard C++17/C++20.

## 15. Input and Output Examples

From the repository root, with Python 3.11+ or a C++17 compiler, respectively:

```sh
printf '4 2 4 1 3\n' | python3 dsa/sorting/quick-sort/python/solution.py
# 1 2 3 4 4

g++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/quick-sort/cpp/solution.cpp -o /tmp/atlas-quick
printf '4 2 4 1 3\n' | /tmp/atlas-quick
# 1 2 3 4 4

printf '+03 -0 -7\n' | /tmp/atlas-quick
# -7 0 3

.venv/bin/python -m pytest dsa/sorting/quick-sort/tests --require-cpp
```

Input contains values only, not a leading count. Empty input prints a newline. Malformed tokens produce stderr and a nonzero exit without partial stdout. C++ overflow is rejected. The Python CLI disables the decimal conversion digit guard only in its entry point so very large Python integers are permitted subject to resources. There are no runtime package dependencies; tests use the root development requirements.

## 16. Edge Cases

Empty/singleton sequences, repeated keys, all-equivalent values, sorted and reverse inputs, negatives, and signed integer extremes are covered. Tests also exercise strings, custom records, unchanged input, long duplicate runs, and seeded random arrays against independent expected output. The C++ tests compile and execute both the reusable API driver and CLI under C++17 and C++20.

Mixed incomparable types raise Python `TypeError` if compared. Comparators with inconsistent ordering, including ordinary floating NaN comparisons, are outside the contract. Resource exhaustion is not converted into a partial result. Invalid CLI forms include sign-only tokens, `1.5`, `0x10`, underscores, and non-ASCII digits.

## 17. Advantages

Three-way classification handles equal-key groups efficiently. The partition core needs no linear temporary buffer. Smaller-side recursion protects stack depth even for poor pivots. The generic APIs preserve the input container and use only strict comparisons. The same canonical implementation explains both sorting and divide-and-conquer ideas.

## 18. Disadvantages and Limitations

The deterministic pivot allows quadratic adversarial runtime. Partitioning is unstable. The returned-copy API still needs linear allocation. Comparisons must define a consistent ordering; there is no custom key/comparator parameter, reverse flag, external-memory mode, insertion cutoff, or introspective fallback. Performance has not been benchmarked against standard libraries.

## 19. When to Use It

Use this implementation to learn partition invariants, equal-key handling, and bounded recursion, or for bounded educational in-memory workloads where instability and a quadratic worst case are acceptable. Duplicate-heavy data illustrates the three-way variant particularly clearly.

## 20. When Not to Use It

Choose [Merge Sort](../merge-sort/README.md) when stability is essential. Choose a method with a worst-case O(n log n) bound, such as [Heap Sort](../heap-sort/README.md), when adversarial runtime matters. In production application code, prefer the appropriate standard-library sorter rather than assuming this educational variant is faster or more robust.

## 21. Comparison With Related Algorithms

Bounds below count element operations; public returned-copy memory is additional to the algorithm core.

| Method | Best | Average / worst | Stable here? | Core extra space |
| --- | --- | --- | --- | --- |
| This three-way quicksort | Θ(n), equal keys | Θ(n log n) / Θ(n²) | No | O(log n) worst-case stack |
| Standard top-down [Merge Sort](../merge-sort/README.md) | Θ(n log n) | Θ(n log n) / Θ(n log n) | Yes | O(n) buffer and logarithmic stack |
| Iterative [Heap Sort](../heap-sort/README.md) | Variant/data dependent | O(n log n) / Θ(n log n) | No | O(1) |
| [Insertion Sort](../insertion-sort/README.md) | Θ(n) | Θ(n²) / Θ(n²) | Yes | O(1) |

A two-way partition need not isolate all equal keys at once. Randomization addresses expected pivot behavior; introspection adds a fallback for excessive partition depth. Neither feature is present here.

## 22. Interview Questions

1. State the four regions and explain why the scan index stays still after a greater-than swap.
2. Why must C++ copy the pivot instead of referencing its original slot?
3. Explain why all equal keys take linear time.
4. Prove logarithmic stack depth while allowing quadratic runtime.
5. Construct an instability example and explain why a middle-position pivot is not a median guarantee.

## 23. Practice Problems

Start by tracing every swap on a five-element array. Then implement an independent partition-property test checking all three regions and the multiset. Extend the API with an explicitly specified comparator. Finally, as a separate exercise, design a randomized pivot or introspective fallback and analyze how its guarantees differ. These exercises do not authorize implementing other catalog topics.

## 24. References

- Conrado Martinez, [Quicksort, NIST Dictionary of Algorithms and Data Structures](https://xlinux.nist.gov/dads/HTML/quicksort.html): definition, variants, and general worst-case behavior.
- Robert Sedgewick and Kevin Wayne, [Quick3way.java in the authors' Algorithms repository](https://github.com/kevin-wayne/algs4/blob/master/src/main/java/edu/princeton/cs/algs4/Quick3way.java): a primary three-way quicksort reference. Its randomization and pivot/recursion details differ from this explicitly documented implementation.

These links support the concepts; this lesson's exact bounds and trace refer to the code in this folder, not to every quicksort variant.

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the project [contribution guide](../../../CONTRIBUTING.md) and [MIT License](../../../LICENSE). Canonical source and contribution context: [Algorithm Atlas](../../../README.md).
