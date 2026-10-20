# Heap Sort

## 1. Algorithm Name

**Heap Sort** (also written **heapsort**), using bottom-up max-heap construction and iterative sift-down. The heap occupies an array prefix; extraction grows an ordered suffix. This lesson implements the sorting operation directly, without a library heap or sorting call.

## 2. Overview

Heap sort organizes values so the largest remaining item sits at index zero. It swaps that item to the end of the active heap, shrinks the heap by one, repairs its root, and repeats until all items are ordered.

The core algorithm uses constant auxiliary space and has Θ(n log n) worst-case time. These APIs first copy the input, so total new storage is Θ(n). Heap sort is not stable: equal-key records may change their relative order. Because sift-down stops early when a parent is already large enough, all-equal input takes Θ(n), rather than Θ(n log n), in this version.

## 3. Problem Statement

Given a finite sequence of n comparable items, return the same items in nondecreasing order without changing the input or modifying its elements. Stability is not required and is not provided.

Python exposes `heap_sort(values: Sequence[T]) -> list[T]`; C++ exposes `algorithm_atlas::heap_sort(const std::vector<T>&) -> std::vector<T>`. Items need a consistent `<` relation. C++ values must also support copying and swapping. Neither API accepts a key or comparator argument. The programs accept whitespace-separated signed decimal integers with no leading element count.

## 4. Why Do We Need This Algorithm?

Repeatedly scanning for a maximum would take quadratic time. A heap encodes enough partial order to find each maximum immediately and repair the remaining structure in logarithmic time.

Heap sort offers a comparison-based worst-case guarantee without the linear work buffer used by straightforward merge sort. This is useful when predictable work and small core workspace matter more than stability. Preserving the input here still requires a result copy, so applications with a strict constant-total-space requirement would need an explicitly mutating API.

## 5. Real-World Applications

- **Predictable comparison sorting:** an iterative heap sort bounds worst-case work without pivot assumptions or recursion depth, useful when studying sorting under adversarial ordering.
- **Sorting where buffer space is constrained:** a mutating heap sort can order a writable array with constant extra workspace. The algorithm taught here has that core property, while its public API allocates a copy to preserve input.
- **Hybrid sort fallback:** introspective sorting designs can fall back to heap sort when partitioning produces excessive recursion depth. This lesson supplies heap sort itself, not a complete hybrid sorter.
- **Heap and priority-queue education:** maximum extraction demonstrates why a heap supports efficient priority operations. A dynamic priority queue is a related data structure, not additional functionality implemented here.

The [NIST entry](https://xlinux.nist.gov/dads/HTML/heapSort.html) defines heap sort through heap construction and repeated maximum extraction. These are design applications, not claims about a particular deployed product.

## 6. Core Intuition

Picture a tournament tree stored inside an array. Every parent is at least as large as its children, so the root must be maximal. After removing the winner, place the last competitor at the root and repeatedly exchange it with the larger child until the tournament property holds again.

The structure needs only a partial order: siblings and separate subtrees need not be sorted. That is enough to expose the next maximum. Putting successive maxima at the far right produces ascending final order.

## 7. Prerequisites

Know zero-based arrays, comparisons and swaps, loops, and tree terminology. For node i, the left and right children are `2*i + 1` and `2*i + 2`; the parent is `floor((i - 1)/2)` when i > 0. Leaves occupy the indices from `floor(n/2)` onward.

Review the [glossary](../../../docs/glossary.md) and [complexity guide](../../../docs/complexity-cheatsheet.md). No third-party runtime dependency is needed; tests use the repository's pytest and compiler setup in [CONTRIBUTING.md](../../../CONTRIBUTING.md).

## 8. Step-by-Step Working Process

1. Copy the input into `result`.
2. Build a max-heap from the bottom up: process internal nodes from `floor(n/2)-1` down to zero. Sift each node down, assuming its child subtrees are already heaps.
3. To sift, select the larger existing child. If the parent is not smaller, stop. Otherwise swap parent and child, move to the child's index, and continue.
4. Swap the heap's root with its final active item. That places the maximum at its final sorted position.
5. Exclude that position from the heap and sift its new root down. Repeat until the active heap contains at most one item.

**Build invariant:** when processing a parent, each child subtree is already a max-heap because descendants were processed first. Sift-down restores that parent's subtree by moving its only possible violation downward.

**Extraction invariant:** the active prefix is a max-heap; the suffix is sorted and contains items at least as large as every item in the prefix. Moving the root to the suffix extends it correctly. Sifting repairs only the prefix, leaving the suffix untouched. The heap shrinks by one each iteration, so extraction terminates with the whole array sorted.

## 9. Pseudocode

```text
HEAP_SORT(values):
    result = shallow copy of values
    for parent from floor(length(result)/2)-1 down through 0:
        SIFT_DOWN(parent, length(result))
    for end from length(result)-1 down through 1:
        swap result[0], result[end]
        SIFT_DOWN(0, end)
    return result

SIFT_DOWN(root, count):
    while root < floor(count/2):
        child = 2*root + 1
        if child + 1 < count AND result[child] < result[child + 1]:
            child = child + 1
        if NOT (result[root] < result[child]):
            return
        swap result[root], result[child]
        root = child
```

`count` is the exclusive boundary of the active heap. Looping only over internal nodes guarantees an existing left child. Both implementations use iterative sifting, without a recursive stack.

## 10. Dry Run

Input: `[4, 10, 3, 5, 1]`.

| Stage | Action | Active heap / ordered suffix |
| --- | --- | --- |
| Build, parent 1 | 10 is already above children 5 and 1 | `[4, 10, 3, 5, 1] / []` |
| Build, parent 0 | Swap 4 with 10, then 4 with 5 | `[10, 5, 3, 4, 1] / []` |
| Extract 10 | Swap root with 1; sift 1 below 5, then 4 | `[5, 4, 3, 1] / [10]` |
| Extract 5 | Swap root with 1; swap 1 with 4 | `[4, 1, 3] / [5, 10]` |
| Extract 4 | Swap root with 3; 3 is above child 1 | `[3, 1] / [4, 5, 10]` |
| Extract 3 | Swap root with 1; one item remains | `[1] / [3, 4, 5, 10]` |

Result: `[1, 3, 4, 5, 10]`; the original sequence remains unchanged.

For instability, label equal keys: `[2a, 2b, 2c]`. Heap construction makes no swaps. Extraction swaps a and c, then c and b, yielding `[2b, 2c, 2a]`. Key order is correct, but original tie order is lost.

## 11. Time Complexity

Let n count items, with O(1) comparisons and swaps. One sift costs O(log n), but bottom-up construction is Θ(n): many nodes are near the leaves and need very few steps. Its work sums over node heights, bounded by `n * sum(h / 2^h)` for positive heights h, which is O(n).

| Case | Bound | Assumptions / explanation |
| --- | --- | --- |
| Best over the accepted input domain | Θ(n) | On all-equal keys every sift stops immediately, and n−1 extractions still occur. |
| Average | Θ(n log n) | Standard model of uniformly permuted distinct keys. |
| Worst | Θ(n log n) | Up to logarithmic repair per extraction; worst inputs attain the bound. |
| Empty or singleton | Θ(1) | No heap work is required. |

This version does not promise a useful distribution-independent average-case expression for arbitrary duplicate frequencies. The often quoted Θ(n log n) best-case statement assumes additional restrictions or a different sift procedure; it does not describe our all-equal case. Large Python integers or costly record comparisons add their own costs.

## 12. Space Complexity

The core heap occupies the result array and uses a constant number of indices and a swap temporary: Θ(1) working storage beyond the returned result. Sift-down is iterative, so there is no recursive stack. The public API copies n items, giving Θ(n) total new storage including the result.

Python copies references shallowly. C++ copies elements and swaps them, so element-owned resources can add memory and time costs. The caller's original input is outside the new-storage count. The programs also buffer parsed input; constant core workspace is not a claim of constant process memory.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) defines `heap_sort(values: Sequence[T]) -> list[T]`. It converts the sequence to a new list, then uses a nested iterative `sift_down` that shares that list. Only `<` is used, allowing records that define no equality or `<=` operation.

For example, `heap_sort((4, 10, 3, 5, 1))` returns `[1, 3, 4, 5, 10]`. The main guard prevents the CLI from running during imports. Python integers may exceed the C++ integer range, subject to interpreter integer-string conversion limits and memory.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) defines `algorithm_atlas::heap_sort(const std::vector<T>&)`. It supports C++17 and C++20 with standard headers only. Define `ALGORITHM_ATLAS_NO_MAIN` before including it in an educational driver.

Unsigned heap indices are safe for empty input: the build loop counts parents down while greater than zero, and extraction runs only while the heap has at least two elements. Checking `root < count/2` before calculating a child also prevents overflow of child-index arithmetic. Copy construction and swapping are required, but default construction of record elements is not.

The standalone program parses signed decimal `long long` tokens, validates the full token, and fails with stderr and nonzero status on malformed input or overflow.

## 15. Input and Output Examples

From the repository root:

```sh
printf '4 10 3 5 1\n' | .venv/bin/python dsa/sorting/heap-sort/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/heap-sort/cpp/solution.cpp -o /tmp/atlas-heap-sort
printf '4 10 3 5 1\n' | /tmp/atlas-heap-sort
```

Both print:

```text
1 3 4 5 10
```

Input has **no leading count**. Input `3 -1 0 -1 3` prints `-1 -1 0 3 3`; empty input prints a newline. Multiple input lines and tabs are accepted, as are `+2`, `-0`, and `0001`. Output uses normalized decimal values.

Run the lesson tests with both C++ standards:

```sh
.venv/bin/python -m pytest dsa/sorting/heap-sort/tests --require-cpp
```

Tests check known answers, input preservation, fixed-seed random data, complete and incomplete heap levels, large ordered/reversed/duplicate-heavy arrays, signed extremes, generic strings and records, the instability example, linear all-equal comparison counts, and CLI failures.

## 16. Edge Cases

- Empty and single-item inputs return new containers without index underflow.
- Two-element and even-length heaps test a parent with only a left child; odd lengths can include both children.
- Equal values sort correctly but do not preserve tie order.
- Negatives and integer extremes require no value arithmetic, avoiding key overflow during sorting.
- Mixed incomparable Python elements raise `TypeError` and leave the input unchanged. NaN and inconsistent comparisons violate the ordering contract.
- CLI tokens such as `1.5`, `0x10`, `1_000`, bare signs, and non-ASCII digits fail before any sorted output is printed.
- C++ input is bounded by the platform's `long long` range, −2⁶³ through 2⁶³−1 on tested 64-bit platforms. Python accepts larger integers within conversion and memory limits. Allocation failures and comparison exceptions propagate rather than becoming custom results.

## 17. Advantages

Worst-case comparison work remains O(n log n), with no pivot selection or recursive call stack. Bottom-up construction is linear rather than n separate logarithmic insertions. The core uses constant workspace, independent of input order, and accepts generic comparable items without integer-key restrictions.

## 18. Disadvantages and Limitations

Heap sort is unstable, and distant parent/child accesses can have worse locality than sequential merging. Constant extra core storage does not remove the result-copy allocation in these preserving APIs. Ordered distinct inputs are not exploited as a linear run. No key parameter, comparator parameter, dynamic priority queue, or mutating public API is provided.

This teaching implementation prioritizes a visible heap invariant. It does not claim a benchmark advantage over tuned library sorting.

## 19. When to Use It

Choose heap sort when worst-case O(n log n) work and constant core workspace matter, stability is unnecessary, and the array is accessible by index. It is also useful as a reference for understanding heap construction or a fallback within a separately designed hybrid sorter. Use this preserving API when keeping the original data justifies a result allocation.

## 20. When Not to Use It

For stable record ordering, use [Merge Sort](../merge-sort/README.md) or an adaptive stable algorithm. For tiny or nearly ordered inputs, [Insertion Sort](../insertion-sort/README.md) can need less work. If ordered runs dominate, [Tim Sort](../tim-sort/README.md) is designed to exploit them. For a narrow integer range, [Counting Sort](../counting-sort/README.md) can avoid comparison-based bounds when its range storage is affordable. Related batch lessons may still be in progress.

## 21. Comparison With Related Algorithms

Space describes core workspace excluding an optional preserving result copy. Variant choices affect recursion and memory bounds.

| Algorithm / variant | Best time | Worst time | Stable? | Core extra space |
| --- | --- | --- | --- | --- |
| This Heap Sort | Θ(n), all equal | Θ(n log n) | No | Θ(1), iterative |
| Standard Selection Sort | Θ(n²) | Θ(n²) | Usually no | Θ(1) |
| This project's top-down Merge Sort | Θ(n log n) | Θ(n log n) | Yes | Θ(n) buffer plus stack |
| Typical Quick Sort | Θ(n log n), distinct keys | Θ(n²) | Usually no | Depends on stack handling |
| Standard Insertion Sort | Θ(n) | Θ(n²) | Yes with strict shifts | Θ(1) |

Selection sort scans the remaining range to find each maximum or minimum. Heap sort maintains enough structure to avoid that repeated full scan. Comparisons for all-equal data depend on the precise variant; the Heap Sort row describes the shipped early-stop implementation.

## 22. Interview Questions

1. Why is bottom-up heap construction O(n) even though one sift may cost O(log n)? Count nodes by height.
2. Why does swapping the root to the last active position preserve the suffix invariant?
3. Which array indices are leaves, and why does `root < count/2` identify internal nodes?
4. Why does an all-equal input take Θ(n) here? Trace how quickly sifts stop.
5. Can heap sort preserve equal-key order? Explain the `[2a, 2b, 2c]` counterexample before proposing metadata or a different method.
6. Why is this API's total new storage Θ(n) if its heap operations use Θ(1) extra memory?

## 23. Practice Problems

1. Build the max-heap for `[9, 1, 8, 2, 7, 3]` and trace each completed extraction.
2. Instrument comparisons on all-equal, ordered, reversed, and fixed-seed random inputs; distinguish a measured count from a proof.
3. Design a min-heap version producing descending order and restate its invariant.
4. Derive a mutating API and explain its space contract, exception behavior, and how it differs from the provided preserving API.
5. Explain how a heap could retain only the k largest values of a stream; compare its memory goal with sorting every value.

These are proposed exercises, not additional implemented algorithms or data structures.

## 24. References

- [NIST Dictionary of Algorithms and Data Structures: heapsort](https://xlinux.nist.gov/dads/HTML/heapSort.html) — definition, running-time bound, and historical references.
- [NIST: build-heap](https://xlinux.nist.gov/dads/HTML/buildHeap.html) — bottom-up heap construction and linear-time bound.
- [NIST: heap](https://xlinux.nist.gov/dads/HTML/heap.html) — the heap data structure and property.
- [Project complexity guide](../../../docs/complexity-cheatsheet.md) — notation and storage accounting.

The source and teaching material are written for Algorithm Atlas. References provide conceptual background; no reference implementation is copied.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). This lesson is part of [Algorithm Atlas](../../../README.md), distributed under its [MIT License](../../../LICENSE). Follow [CONTRIBUTING.md](../../../CONTRIBUTING.md) for attribution, testing, and phase-review requirements.
