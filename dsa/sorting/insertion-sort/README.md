# Insertion Sort

## 1. Algorithm Name

**Insertion Sort**, using a saved item and rightward shifts. This is linear insertion sort: it scans the ordered prefix backward to locate the insertion point. It is distinct from binary insertion sort, which uses binary search for that location but still shifts array elements.

## 2. Overview

Insertion sort grows an ordered prefix one item at a time. Each new item moves left past strictly larger items until it reaches its position. The implementation returns a new sorted container and preserves the original input. It is stable: records with equal comparison keys keep their original order.

## 3. Problem Statement

Given a sequence of `n` comparable elements, return those same elements in nondecreasing order under `<`, preserving equal-key order. Elements must have a consistent ordering: for example, ordinary integers, strings, or records comparing by one key. Comparisons must not mutate their operands.

The Python API accepts a `Sequence[T]` and returns `list[T]`. The C++ API accepts `const std::vector<T>&` and returns `std::vector<T>`; elements must support copying, assignment, and `<`. Both preserve their input. Copies are shallow in Python: the returned list contains the same element objects.

The command-line programs accept whitespace-separated signed decimal integers and print one sorted line. Python supports arbitrary-precision integers subject to available memory. The C++ CLI accepts the platform's `long long` range, commonly `[-9223372036854775808, 9223372036854775807]`. The reusable APIs also support other appropriate comparable types.

## 4. Why Do We Need This Algorithm?

An algorithm with little setup can work well on short sequences. An already ordered prefix also provides useful information: a new item may already belong at the end, avoiding further movement. Insertion sort exploits this existing order naturally.

The lesson demonstrates an invariant, stability, and adaptive behavior using simple loops. Its quadratic worst case also shows why correctness alone does not establish suitability for large inputs.

## 5. Real-World Applications

- **Small ordered batches:** an application collecting a few comparable readings or display records can maintain a small ordered batch with direct insertion. The benefit depends on batch size and comparison cost.
- **Nearly ordered data:** periodic updates to an otherwise ordered list can require few shifts if few pairs are out of order. This fits a small local ranking or timestamp list when the updates rarely move far.
- **Hybrid sorting:** larger sorting methods can finish small subarrays with insertion sort to reduce overhead. Princeton's [MergeX implementation](https://algs4.cs.princeton.edu/code/edu/princeton/cs/algs4/MergeX.java.html) is a concrete educational example using an insertion-sort cutoff.

These are selection examples, not claims that a named commercial service deploys this exact implementation. This API copies the entire sequence for each call; an application that repeatedly inserts single arrivals may prefer a dedicated incremental container.

## 6. Core Intuition

Think of arranging playing cards in your hand. The cards already held are ordered. Save the next card, move each larger card one place right, and place the saved card in the gap.

Saving the item before shifting matters: shifting temporarily overwrites its original position. Using a strict comparison matters too: a new card does not cross an earlier card with the same key, preserving stability.

## 7. Prerequisites

- Sequences, indices, assignment, and loops.
- A consistent comparison ordering and the meaning of equal comparison keys.
- [Asymptotic notation and memory accounting](../../../docs/complexity-cheatsheet.md).
- [Stability and related vocabulary](../../../docs/glossary.md).

No recursion, external packages, or advanced data structures are required.

## 8. Step-by-Step Working Process

1. Copy the input into the output container. The prefix containing only index `0` is ordered.
2. For each index `i` from `1` to `n - 1`, save the element at `i` as `item`.
3. Start a gap at `i`. While the gap is not at the beginning and `item` is strictly smaller than its left neighbor, shift that neighbor one place right and move the gap left.
4. Write `item` into the gap. The prefix through `i` is now ordered.
5. Return the container after every element has been inserted.

**Invariant:** before iteration `i`, the prefix `[0, i)` is an ordered, stable permutation of the original first `i` elements. Shifting only elements greater than `item` leaves a gap after all earlier equivalent items. Filling it extends the invariant to `[0, i + 1)`. No element is lost because `item` is saved before shifts. The inner loop decreases its gap index, and the outer loop increases `i` within a finite sequence. At termination the prefix is the whole sequence, so the result is ordered, stable, and contains every original item.

## 9. Pseudocode

```text
INSERTION_SORT(values):
    result = copy(values)
    for i = 1 to length(result) - 1:
        item = result[i]
        position = i
        while position > 0 and item < result[position - 1]:
            result[position] = result[position - 1]
            position = position - 1
        result[position] = item
    return result
```

The left side of `and` is evaluated first, preventing access before index `0`.

## 10. Dry Run

Input: `[5, 2a, 4, 2b, 1]`, where `2a` and `2b` compare as equal but have different identities.

| Iteration | Saved item | Items shifted right, in order | Container after insertion | Ordered prefix length |
| --- | --- | --- | --- | ---: |
| Initial | — | — | `[5, 2a, 4, 2b, 1]` | 1 |
| `i = 1` | `2a` | `5` | `[2a, 5, 4, 2b, 1]` | 2 |
| `i = 2` | `4` | `5` | `[2a, 4, 5, 2b, 1]` | 3 |
| `i = 3` | `2b` | `5`, `4` | `[2a, 2b, 4, 5, 1]` | 4 |
| `i = 4` | `1` | `5`, `4`, `2b`, `2a` | `[1, 2a, 2b, 4, 5]` | 5 |

During `i = 3`, after shifting `5` the array temporarily reads `[2a, 4, 5, 5, 1]`; the saved `2b` remains in `item`. After shifting `4`, the gap is at index `1`. The comparison `2b < 2a` is false, so `2b` is placed after `2a`. There are eight shifts in total, one for each original inversion.

## 11. Time Complexity

Let `n` be the number of elements and `I` the number of strict inversions: pairs of indices `i < j` for which `values[j] < values[i]`. Assume constant-time comparisons and element copies or assignments.

Every shift removes one inversion. The outer loop also does linear work, so runtime is **Θ(n + I)** for nonempty inputs, including the initial copy. Empty input takes constant overhead.

| Case | Runtime | Reason |
| --- | --- | --- |
| Best: already ordered or all keys equal | Θ(n) | One failed comparison per insertion; no shifts |
| Average: uniformly random permutation of distinct keys | Θ(n²) | Expected inversion count is `n(n - 1) / 4` |
| Worst: descending distinct keys | Θ(n²) | Every earlier element shifts; `I = n(n - 1) / 2` |

For `I = O(n)`, the algorithm runs in linear time. A vague description such as “almost sorted” does not guarantee this unless its inversion count is small. The shift bound and adaptive behavior are consistent with [Princeton's elementary-sorting discussion](https://algs4.cs.princeton.edu/21elementary/).

Python big integers, long strings, or expensive record copies can make individual operations nonconstant. The table counts element operations, not bit operations or text parsing costs.

## 12. Space Complexity

The insertion loop uses **O(1) auxiliary element slots**: the saved item and indices. This is the familiar in-place insertion-sort core, but **these public functions allocate an O(n) returned copy** to preserve their input. Additional storage relative to the supplied input is therefore O(n), and total input-plus-output storage is O(n). There is no recursive stack.

Python duplicates references rather than cloning objects. C++ copies elements into its returned vector and temporarily stores one additional element. The CLI also retains its parsed input and output; Python's token list and text representation add storage proportional to the input's textual size.

## 13. Python Implementation

Source: [python/solution.py](python/solution.py).

```python
def insertion_sort(values: Sequence[T]) -> list[T]:
    result = list(values)
    for index in range(1, len(result)):
        item = result[index]
        position = index
        while position > 0 and item < result[position - 1]:
            result[position] = result[position - 1]
            position -= 1
        result[position] = item
    return result
```

Only `<` is needed; no `<=`, equality, or integer arithmetic is required of elements. A mixed sequence such as integers and strings raises `TypeError` when comparison is attempted. Importing the module does not execute the CLI. The script validates every token before sorting and disables Python's decimal conversion digit guard only when its CLI runs so integer magnitude is bounded by resources rather than that guard.

## 14. C++ Implementation

Source: [cpp/solution.cpp](cpp/solution.cpp).

The API is `algorithm_atlas::insertion_sort<T>(const std::vector<T>&)`. It uses a `std::size_t` gap with a `position > 0` check before subtracting one, so index underflow cannot occur. Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a separate driver to use the template without its demonstration entry point.

The standalone CLI validates token grammar and uses `std::from_chars` to reject partial numbers and overflow. A leading `+` is checked and removed explicitly because integer `from_chars` does not accept it. Code uses standard headers and supports both C++17 and C++20.

## 15. Input and Output Examples

Run these commands **from the repository root**. Python needs Python 3.11+ and no third-party runtime packages. C++ needs a compiler supporting C++17 or C++20.

```sh
printf '5 2 4 2 1\n' | python3 dsa/sorting/insertion-sort/python/solution.py
# Output: 1 2 2 4 5

c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/insertion-sort/cpp/solution.cpp -o /tmp/atlas-insertion-sort
printf '5 2 4 2 1\n' | /tmp/atlas-insertion-sort
# Output: 1 2 2 4 5

printf '+3 -7 0 -7\n' | /tmp/atlas-insertion-sort
# Output: -7 -7 0 3

printf '' | python3 dsa/sorting/insertion-sort/python/solution.py
# Output: one empty line
```

Every successful output ends in a newline. There is no length prefix. To run the Python tests plus compile and execute both C++ standards:

```sh
.venv/bin/python -m pytest dsa/sorting/insertion-sort/tests --require-cpp
```

Tests cover independently known outputs, deterministic random differential cases, preserved input, tagged-record stability, sorted/reverse/one-inversion comparison counts, and valid/invalid CLI behavior.

## 16. Edge Cases

| Input or condition | Behavior |
| --- | --- |
| Empty sequence or whitespace-only CLI input | Empty result; CLI prints a newline |
| One element | Returned copy contains that element |
| Equal keys | No shifts across equal keys; original order survives |
| Negative values and zero | Ordered using ordinary comparison |
| Already ordered sequence | Linear work with no shifts |
| Descending sequence | Maximum shifts for distinct keys |
| Python integers outside machine range | Supported, with magnitude-dependent costs |
| C++ CLI integer outside `long long` range | Nonzero exit, error on stderr, no result on stdout |
| Invalid CLI tokens such as `1.5`, `0x10`, `1_000`, or `two` | Entire input rejected; nonzero exit and stderr error |
| Comparator without a consistent ordering, including floating NaN | Outside the sorting contract; no meaningful sorted-order guarantee |

CLI digits are ASCII `0` through `9`; a sign alone is invalid. The C++ API can sort other numeric types when their `<` meets the contract. Resource exhaustion is not recovered into a partial sorted answer.

## 17. Advantages

- Simple loop structure makes the invariant and stable handling of equal keys clear.
- Requires very little working storage beyond this API's returned copy.
- Adapts to the actual inversion count and handles ordered data in linear time.
- Supports arbitrary comparable records without a numeric key range assumption.
- Uses contiguous storage and local shifts, which can make short runs practical.

## 18. Disadvantages and Limitations

- Quadratic work on large disordered sequences quickly dominates its low setup cost.
- Moving a long prefix can be costly when elements are expensive to copy or assign.
- This implementation copies the input even if it is already ordered.
- The API has no explicit key function or comparator parameter; records must define `<` appropriately.
- Python's output is a shallow copy. Mutation of an element object is visible through both containers.
- It is a batch API, not an unbounded stream or external-memory sorter. The input must fit in memory.

## 19. When to Use It

Choose it for short arrays, educational demonstrations of stable sorting, or inputs known to have only a small number of inversions. It is also a reasonable building block when writing an explicitly designed hybrid sorter with a measured small-run threshold. Use this copy-returning API when preserving the caller's container is useful and the allocation is acceptable.

## 20. When Not to Use It

For large arbitrary inputs, consider an O(n log n) method. For a long-lived data structure receiving frequent middle insertions, consider an ordered structure that avoids shifting a large array repeatedly. For fixed small integer ranges, a noncomparison method may exploit information this algorithm ignores. For production Python application code, the standard sorting API usually offers a better tested and optimized general solution.

## 21. Comparison With Related Algorithms

The table describes the usual algorithm cores; each lesson must account separately for a returned copy.

| Method | Best | Average / worst | Stable in usual variant? | Key tradeoff |
| --- | --- | --- | --- | --- |
| Insertion sort | Θ(n) | Θ(n²) / Θ(n²) | Yes | Adapts to inversions; shifts larger elements |
| [Selection sort](../selection-sort/README.md) | Θ(n²) | Θ(n²) / Θ(n²) | No | Few swaps but always scans the remaining suffix |
| [Bubble sort](../bubble-sort/README.md), early exit | Θ(n) | Θ(n²) / Θ(n²) | Yes | Neighbor swaps rather than a saved item and shifts |
| [Merge sort](../merge-sort/README.md), standard top-down | Θ(n log n) | Θ(n log n) / Θ(n log n) | Yes | Better large-input bound; ordinarily needs a merge buffer |

Binary insertion reduces comparisons to O(n log n) in the worst case, but array movement remains O(n²). That variant is not the implementation here.

## 22. Interview Questions

1. **What is ordered before iteration `i`?** The stable prefix `[0, i)`, containing the original first `i` items.
2. **Why save the next item before shifting?** Its original slot can be overwritten while a gap moves left.
3. **What breaks if the condition also shifts equal keys?** Later equal-key items can cross earlier ones, destroying stability.
4. **Why can the best case be linear?** Each insertion ends after its first comparison; the unavoidable copy is linear too.
5. **Does using binary search remove the quadratic bound?** No; the elements between the insertion point and current item must still move.
6. **Is this API O(1) extra space?** The sorting loop is, but the returned copy adds O(n) storage.

## 23. Practice Problems

1. Trace `[3, 1, 3, 2]` with tags on the two `3` values. Count shifts and verify stable order.
2. Instrument the algorithm to count shifts. Independently count strict inversions with a double loop and check that the counts agree on small seeded inputs.
3. Add a key-function interface while evaluating each key once. Explain the new storage cost and test duplicate-key stability.
4. Design a separate in-place API and test that its mutation behavior differs clearly from this API.
5. Explore binary insertion on expensive-to-compare records. Measure comparisons separately from element moves and explain the tradeoff.

These exercises do not change the implemented API or claim additional completed catalog topics.

## 24. References

- Robert Sedgewick and Kevin Wayne, [Algorithms, 4th Edition: Elementary Sorts](https://algs4.cs.princeton.edu/21elementary/) — analysis of insertion sort and partially ordered input.
- Princeton Algorithms library, [Insertion API documentation](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/Insertion.html) — stability and inversion-based discussion for its exchange-based variant.
- Princeton Algorithms library, [MergeX source](https://algs4.cs.princeton.edu/code/edu/princeton/cs/algs4/MergeX.java.html) — a verifiable insertion-sort cutoff example.

The implementations in this lesson use shifts and preserve the caller's input; those choices and their storage costs are explained above rather than inferred from the reference's in-place exchange variant.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). This lesson follows the [contribution standards](../../../CONTRIBUTING.md) and is distributed under the repository's [MIT License](../../../LICENSE).

[Sorting category](../README.md) · [Project home](../../../README.md) · [Progress](../../../docs/progress.md)
