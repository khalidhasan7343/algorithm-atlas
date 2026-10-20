# Merge Sort

## 1. Algorithm Name

**Merge Sort**, implemented as stable, top-down, two-way merge sort with one reusable auxiliary buffer. This canonical lesson serves both [Sorting](../README.md) and [Divide and Conquer](../../divide-and-conquer/README.md); their indexes share this implementation.

## 2. Overview

Merge sort divides a sequence into two nearly equal halves, recursively orders each half, and combines them by repeatedly selecting the smaller front item. A range with fewer than two items is already sorted. These implementations return a new container and leave the input unchanged.

Every nontrivial range is merged, even when the data is ordered. Best, average, and worst time are therefore Θ(n log n) for n ≥ 2, assuming constant-time comparisons and copies.

## 3. Problem Statement

Given a finite sequence of n comparable items, return the same items in nondecreasing order. Preserve the relative order of items with equivalent comparison keys: this is **stability**. Do not modify the input sequence or its element objects.

The Python API accepts `Sequence[T]` and returns `list[T]`. The C++ API accepts `const std::vector<T>&` and returns `std::vector<T>`. Elements need a consistent `<` relation; C++ elements must also be copy constructible and copy assignable. Neither API exposes a key or comparator parameter. Standalone programs accept whitespace-separated signed decimal integers, without an element count.

## 4. Why Do We Need This Algorithm?

Ordering data simplifies grouping, reporting, and later scans. Insertion sort may move quadratically many items on large reversed inputs. Merge sort limits the number of merge levels to logarithmic depth, keeping work Θ(n log n) regardless of initial ordering.

Stability matters when records already have a meaningful secondary order. If transactions arrive chronologically, a stable sort by account keeps equal-account transactions chronological. A reusable buffer makes stable array merging straightforward to implement and prove correct.

## 5. Real-World Applications

- **Stable record processing:** order records by customer, priority, or category while retaining arrival order for equal keys. The generic APIs demonstrate this operation with comparable records.
- **External sorting:** sort chunks that fit in memory, write ordered runs, then merge their streams. This principle supports files larger than RAM; these in-memory implementations do not perform external sorting or disk I/O.
- **Combining ordered feeds:** the two-pointer merge operation combines timestamped logs or ordered report fragments in linear time when each input is already ordered.
- **Algorithm analysis:** inversion counting can augment a merge step to count out-of-order pairs efficiently. It is a practice task, not shipped functionality.

These are applications of stable merging and merge-sort design, not claims about a product deployment. The [NIST entry](https://xlinux.nist.gov/dads/HTML/mergesort.html) describes the general algorithm and its relationship to external sorting.

## 6. Core Intuition

Imagine two queues of ordered cards. The smallest remaining card must be at the front of one queue. Copy the smaller front card and advance only that queue. After one queue empties, copy the remaining cards from the other.

Recursion supplies the two ordered queues by dividing until ranges have fewer than two items. During merging, choose the left item whenever the right item is not strictly smaller. Equal-key items in the left half originally preceded those in the right, so this tie rule preserves stability.

## 7. Prerequisites

Understand arrays or lists, indices, half-open ranges `[start, end)`, function calls, recursion, and asymptotic notation. Review the [glossary](../../../docs/glossary.md) and [complexity cheat sheet](../../../docs/complexity-cheatsheet.md). The [divide-and-conquer category](../../divide-and-conquer/README.md) lists related topics; some lessons remain planned.

No external runtime package is needed. Repository tests require the development dependencies and compiler described in [CONTRIBUTING.md](../../../CONTRIBUTING.md).

## 8. Step-by-Step Working Process

1. Copy the input into `result`; initialize an equally sized `buffer` from that copy.
2. For a range `[start, end)`, return if its length is zero or one.
3. Compute `middle = start + (end - start) // 2`. Recursively sort `[start, middle)` and `[middle, end)`.
4. Set `left = start` and `right = middle`. Fill the buffer range by taking the smaller current item. If the right half is exhausted, take from the left. When both have items, choose the left unless the right is strictly smaller.
5. Copy the merged buffer range back into `result`. Return the result after the full-range call finishes.

**Merge invariant:** before each destination is filled, the buffer prefix contains the smallest consumed items in sorted, stable order. Each pointer marks the first unconsumed item in its ordered half. Taking the minimum front extends the invariant. Each iteration consumes one item, so the merge terminates after exactly the range length steps.

**Recursive correctness:** base ranges are sorted. Assuming smaller recursive ranges are correctly and stably sorted, the invariant proves their merged range is too. Range lengths strictly shrink, establishing termination.

## 9. Pseudocode

```text
MERGE_SORT(values):
    result = shallow copy of values
    buffer = shallow copy of result
    SORT_RANGE(0, length(result))
    return result

SORT_RANGE(start, end):
    if end - start < 2:
        return
    middle = start + floor((end - start) / 2)
    SORT_RANGE(start, middle)
    SORT_RANGE(middle, end)
    left = start
    right = middle
    for destination from start through end - 1:
        if right == end OR
           (left < middle AND NOT (result[right] < result[left])):
            buffer[destination] = result[left]
            left = left + 1
        else:
            buffer[destination] = result[right]
            right = right + 1
    for position from start through end - 1:
        result[position] = buffer[position]
```

The `OR` and `AND` conditions short-circuit, so exhausted ranges are never indexed. Recursive calls share the two arrays; they do not create subarray slices.

## 10. Dry Run

Input: `[5, 1, 4, 2, 8]`.

| Range | Split or merge | Result in the range |
| --- | --- | --- |
| `[0, 5)` | Split at index 2 | `[5, 1]` and `[4, 2, 8]` |
| `[0, 2)` | Merge `[5]` and `[1]` | `[1, 5]` |
| `[2, 5)` | Split into `[4]` and `[2, 8]` | Pending recursive merge |
| `[3, 5)` | Merge `[2]` and `[8]` | `[2, 8]` |
| `[2, 5)` | Merge `[4]` and `[2, 8]` | `[2, 4, 8]` |
| `[0, 5)` | Merge `[1, 5]` and `[2, 4, 8]` | `[1, 2, 4, 5, 8]` |

During the final merge, the buffer prefix becomes `[1]`, `[1, 2]`, `[1, 2, 4]`, `[1, 2, 4, 5]`, and `[1, 2, 4, 5, 8]`. The full merged range is copied back. The original input stays `[5, 1, 4, 2, 8]`.

For stability, label equal keys by arrival order: `[2a, 1x, 2b, 1y]` becomes `[1x, 1y, 2a, 2b]`. Left items win equal-key comparisons across halves.

## 11. Time Complexity

Let n count items, with O(1) comparisons and copies. A merge writes every item to the buffer and back, costing Θ(k) for a range of k items. The recurrence is `T(n) = T(floor(n/2)) + T(ceil(n/2)) + Θ(n)`.

| Case | Bound | Reason |
| --- | --- | --- |
| Best | Θ(n log n) | Ordered inputs still undergo every merge. |
| Average | Θ(n log n) | Each merge level processes Θ(n) items. |
| Worst | Θ(n log n) | There are Θ(log n) levels. |
| n = 0 or 1 | Θ(1) | Only constant-size initialization and a base call. |

Initial copies add Θ(n). If comparing or copying records costs more than O(1), include those costs. Comparing arbitrary-precision Python integers depends on their bit lengths. This version has no already-ordered boundary shortcut.

## 12. Space Complexity

The returned result stores n items and the reusable buffer stores another n items. Recursion contributes Θ(log n) stack frames. Auxiliary working memory excluding the result is Θ(n); total new storage including it is also Θ(n), approximately two arrays plus stack frames. This is not an in-place implementation.

Python copies references without deep-copying element objects. C++ copies elements, whose own resources can increase actual memory and copy cost. The caller's original input storage is excluded from the new-storage count.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `merge_sort(values: Sequence[T]) -> list[T]`. It copies the sequence for the result and buffer, then a nested function sorts index ranges. A `<` comparison suffices; equality and `<=` are unnecessary. Records are shallowly copied and not modified.

For example, `merge_sort([5, 1, 4, 2, 8])` returns `[1, 2, 4, 5, 8]`, and `merge_sort((3, 1, 2))` returns a list `[1, 2, 3]`. Demonstration execution is guarded by `if __name__ == "__main__"`.

Python integers are not restricted to the C++ `long long` range. The interpreter's integer-string digit limit and available memory still bound exceptionally large CLI tokens.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) provides `algorithm_atlas::merge_sort(const std::vector<T>&)`. Copy-initializing the buffer supports records without a default constructor. Half-open ranges use `std::size_t`; `start + (end - start) / 2` avoids overflowing a sum of indices.

Define `ALGORITHM_ATLAS_NO_MAIN` before including the file in an educational driver to use the template. Types need a strict weak ordering through `<`, copy construction, and copy assignment. The standalone program parses `long long` values and rejects malformed or out-of-range tokens with stderr and a nonzero exit status.

## 15. Input and Output Examples

Run from the repository root. Input contains only whitespace-separated signed decimal integers; there is **no leading count**.

```sh
printf '5 1 4 2 8\n' | .venv/bin/python dsa/sorting/merge-sort/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/merge-sort/cpp/solution.cpp -o /tmp/atlas-merge-sort
printf '5 1 4 2 8\n' | /tmp/atlas-merge-sort
```

Both print:

```text
1 2 4 5 8
```

Input `3 -1 0 -1 3` prints `-1 -1 0 3 3`. Empty input prints one newline. Whitespace may include multiple lines. Tokens `+2` and `0001` are valid; output normalizes decimal formatting.

Run the tests, including C++17 and C++20:

```sh
.venv/bin/python -m pytest dsa/sorting/merge-sort/tests --require-cpp
```

Tests cover independent known answers, fixed-seed random inputs, odd lengths, integer extremes, unchanged inputs, tagged-record stability using only `<`, non-default-constructible C++ records, and both valid and malformed CLI input.

## 16. Edge Cases

- Empty and single-item inputs return new containers immediately.
- Repeated keys preserve original order. All-equal input still performs normal merge work.
- Negative values and signed integer extremes need no value arithmetic, so sorting the keys does not overflow.
- Odd and non-power-of-two sizes use unequal halves correctly.
- Incomparable Python items raise `TypeError` without changing the input. NaN and inconsistent comparisons violate the ordering contract and have no sorted-order guarantee.
- CLI input rejects `1.5`, `0x10`, `1_000`, bare signs, and non-ASCII digits. Parsing finishes before output, so an invalid token produces no partial result.
- The C++ CLI accepts the platform's `long long` range: −2⁶³ through 2⁶³−1 on tested 64-bit platforms. Python accepts larger integers within interpreter and memory limits. Allocation failures and element-comparison exceptions are not converted into custom result values.

## 17. Advantages

Merge depth does not depend on pivot choices or adversarial ordering. Stability follows from an explicit tie rule. Sequential accesses make merging easy to trace. One shared buffer avoids fresh subarray allocation at every recursive call. The separation into division, recursive ordering, and merging supports a concise correctness proof.

## 18. Disadvantages and Limitations

Preserving input and using straightforward stable merging allocate two additional n-item containers. Every level copies items twice, and recursive calls add overhead on short ranges. Ordered data receives no linear-time fast path. These APIs require all data to fit in memory and do not implement external sorting, custom comparators, parallelism, or in-place merging.

Production Python sorting provides more features and implementation tuning. This educational implementation demonstrates the named algorithm directly rather than delegating to a built-in sort.

## 19. When to Use It

Use this approach for stable ordering and predictable Θ(n log n) work when memory is sufficient for the result and buffer. It also provides a clear reference for learning recursive correctness or extending a merge step to count statistics.

## 20. When Not to Use It

For constrained workspace, consider [Heap Sort](../heap-sort/README.md) and its stability tradeoff. For tiny or nearly ordered arrays, [Insertion Sort](../insertion-sort/README.md) can use fewer operations. For long preordered runs, adaptive [Tim Sort](../tim-sort/README.md) can exploit structure ignored here. Related lessons may remain planned until their batch is completed.

## 21. Comparison With Related Algorithms

Space describes core working memory excluding an optional copied result. Concrete lesson APIs may add a result copy to preserve input.

| Algorithm / variant | Best time | Worst time | Stable? | Core extra memory |
| --- | --- | --- | --- | --- |
| This Merge Sort | Θ(n log n) | Θ(n log n) | Yes | Θ(n) buffer and Θ(log n) stack |
| Standard Insertion Sort | Θ(n) | Θ(n²) | Yes, with strict shifting | Θ(1) |
| Typical in-place Quick Sort | Θ(n log n) | Θ(n²) | Usually no | Depends on stack management |
| Standard Heap Sort | Θ(n log n) | Θ(n log n) | No | Θ(1), iterative sift-down |
| Adaptive Tim Sort family | Θ(n) | O(n log n) | Yes | O(n) |

Quick Sort's space and recursion bounds depend on partitioning and stack choices. Merge Sort trades additional array space for stability and a worst-case guarantee.

## 22. Interview Questions

1. Why choose the left item when keys are equivalent? Show how choosing right first changes the labeled dry run.
2. Why can all calls share a buffer? Each merge overwrites its range before copying it back; a parent starts after both child calls finish.
3. Why is the best case Θ(n log n) here? Identify the absent ordered-boundary shortcut and its possible effect.
4. How do half-open ranges handle n = 0 and n = 5 without negative indices?
5. Where does copying back appear in the recurrence? Two linear passes still cost Θ(n) per level.
6. Why does Θ(log n) recursion not imply Θ(log n) total auxiliary space? Include the shared buffer.

## 23. Practice Problems

1. Trace `[7, 3, 5, 3, 1]`, label the duplicate 3s, and record every completed merge.
2. Count comparisons on ordered, reversed, and fixed-seed shuffled arrays of length 32. Separate operation counts from timing claims.
3. Design a key/comparator parameter preserving stability, then test records whose equality differs from comparison equivalence.
4. Derive bottom-up iterative merge sort using the same buffer; prove the invariant for doubling run widths.
5. Derive inversion counting: when a right item precedes the current left item, how many unconsumed left items form inversions? Compare with a quadratic oracle on short inputs.

These are further exercises, not claims of additional shipped algorithms.

## 24. References

- [NIST Dictionary of Algorithms and Data Structures: merge sort](https://xlinux.nist.gov/dads/HTML/mergesort.html) — definition, running time, and related variants.
- [NIST: merge](https://xlinux.nist.gov/dads/HTML/merge.html) — combining sorted sequences.
- [Python documentation: Sorting HOWTO](https://docs.python.org/3/howto/sorting.html) — stable sorting and record ordering; Python's production sorter is separate from this lesson.
- [Project complexity guide](../../../docs/complexity-cheatsheet.md) — notation and storage accounting.

Code and explanations are written for Algorithm Atlas; references supply conceptual background, not copied implementation source.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). This lesson belongs to the [Algorithm Atlas project](../../../README.md) and is distributed under its [MIT License](../../../LICENSE). Read [CONTRIBUTING.md](../../../CONTRIBUTING.md) for attribution, testing, and review requirements.
