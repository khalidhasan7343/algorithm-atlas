# Selection Sort

## 1. Algorithm Name

**Selection Sort**, using minimum selection and a direct swap into a growing sorted prefix. No abbreviation is used. This lesson covers the conventional unstable array variant, not stable selection by shifting intervening elements.

## 2. Overview

Selection Sort scans the remaining unsorted values for a minimum, then moves it to the next output position. The sorted prefix grows one element per pass. It always performs quadratic comparisons, but at most a linear number of swaps. The public functions return a copy rather than modifying the caller's container.

## 3. Problem Statement

Given `n` values with a consistent strict ordering, produce a new container holding the same values in nondecreasing order. Python accepts `Sequence[T]` and returns `list[T]`; C++ accepts `const std::vector<T>&` and returns `std::vector<T>`. Only `<` is used for comparisons. Equal-key records are not guaranteed to retain their original order.

Both standalone programs accept whitespace-separated signed decimal integers with no length prefix and print sorted integers separated by spaces and terminated by a newline. Python supports arbitrary-size integers; C++ CLI values must fit its `long long` type.

## 4. Why Do We Need This Algorithm?

It separates comparison cost from data movement: finding the minimum may require many reads and comparisons while only one exchange occurs per pass. This makes it a useful study of loop invariants and cost models. Its performance does not depend on input order, offering a clear contrast with adaptive methods such as Insertion Sort.

## 5. Real-World Applications

- A teaching visualizer can display the selected minimum and the expanding final prefix independently.
- For a tiny array of records where element moves are costly and comparisons are cheap, its small swap count may be useful; the result-copy cost must still be budgeted for this API.
- A deterministic reference routine for small diagnostic fixtures is easy to inspect and reproduce.

These are conditional examples, not documented deployments or a claim that this algorithm minimizes every form of write. Flash storage applications, for example, require considering block behavior, copying, and alternative low-write algorithms before making a choice.

## 6. Core Intuition

If you know the smallest remaining value, you know exactly what belongs next. Find it by scanning the whole unsorted suffix. Exchange it with the suffix's first value and never revisit that output position. Continue until only one value is left; it must already occupy the final position.

## 7. Prerequisites

Understand array/list indexing, strict comparisons, swaps, and nested loops. Review the [complexity cheat sheet](../../../docs/complexity-cheatsheet.md) and [glossary](../../../docs/glossary.md) for asymptotic bounds, stability, and auxiliary memory. No recursion or auxiliary data structure is required.

## 8. Step-by-Step Working Process

1. Copy the input into the result.
2. For each start position from zero through `n - 2`, initially consider that position to be the minimum.
3. Scan every later position. Update the minimum index only when a strictly smaller value is found.
4. If the minimum index differs from the start, swap those two positions; skip a needless self-swap otherwise.
5. Advance the start. Stop when there are no remaining choices to make.

Before each pass, the prefix contains the smallest values in sorted final positions. During the scan, the minimum index names a smallest value among the scanned suffix values. Placing that minimum extends the prefix invariant by one. Every swap preserves the input multiset; after `n - 1` passes the entire result is ordered. The loop boundaries make empty and singleton cases terminate without indexing an element.

## 9. Pseudocode

```text
SELECTION_SORT(values):
    result = COPY(values)
    FOR start FROM 0 TO LENGTH(result) - 2:
        minimum = start
        FOR index FROM start + 1 TO LENGTH(result) - 1:
            IF result[index] < result[minimum]:
                minimum = index
        IF minimum != start:
            SWAP(result[start], result[minimum])
    RETURN result
```

The outer loop is empty when fewer than two elements exist. Choosing the first equal minimum does not make a direct-swap implementation stable: the other swapped value can leap over an equal-key record.

## 10. Dry Run

Input: `[5, 1, 4, 2]`.

| Pass | Scan and selected minimum | State after optional swap |
| --- | --- | --- |
| `start = 0` | Compare `1`, `4`, `2` against the running minimum; choose `1` at index 1 | `[1, 5, 4, 2]` |
| `start = 1` | Compare `4`, then `2`; choose `2` at index 3 | `[1, 2, 4, 5]` |
| `start = 2` | Compare `5` with `4`; choose current index 2 | `[1, 2, 4, 5]` |

There are `3 + 2 + 1 = 6` comparisons and two swaps. The input remains unchanged. To see instability, label equal keys: `[2a, 2b, 1c]` becomes `[1c, 2b, 2a]` after the first swap, reversing the two `2` records.

## 11. Time Complexity

Let `n` be the element count and assume constant-time comparison, copying, and swapping.

| Case | Time | Reason |
| --- | --- | --- |
| Best | Θ(n²) | Even sorted data requires every suffix scan |
| Average | Θ(n²) | Comparison count is independent of ordering |
| Worst | Θ(n²) | The same scans occur on every arrangement |

For `n >= 2`, the exact comparison count is `(n - 1) + (n - 2) + ... + 1 = n(n - 1)/2`. There are at most `n - 1` swaps and none on already sorted data in this implementation. Copying adds Θ(n) work, which does not change the quadratic bound. Empty and singleton inputs take constant time. Expensive comparisons, arbitrary-precision integer operations, element copying, and CLI digit processing require their own costs rather than the unit-cost assumption.

## 12. Space Complexity

The selection loop uses O(1) auxiliary memory and no recursion. The API's returned copy requires Θ(n) additional container storage for nonempty input, so this public function is not an in-place API despite its in-place sorting core. Python's copy holds references; C++ copies element values. Input plus result still uses Θ(n) container storage. The CLI adds text/token buffers in Python and an input vector in C++; their storage is separate from the core-loop bound.

## 13. Python Implementation

[python/solution.py](python/solution.py) provides `selection_sort(values)` with a fresh shallow list result. It compares using `<` and swaps only when the minimum comes from a different position. The import guard prevents CLI execution when loading the function. Custom record objects are preserved, including their identity; their keys must be ordered consistently.

The CLI validates all tokens before sorting, emits a short error on standard error for invalid tokens, and returns nonzero without partial output. It turns off Python's decimal integer conversion digit cap for this CLI to support very large integer tokens, subject to available memory and processing time.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) provides `algorithm_atlas::selection_sort<T>`. The generic type must support copying, swapping, and strict less-than comparison. The implementation uses only standard headers and works with C++17 and C++20. Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a library test driver. The standalone program validates signed decimal tokens and uses `std::from_chars` to detect numeric range errors; the optional leading plus is handled explicitly.

## 15. Input and Output Examples

From the **repository root**:

```sh
printf '5 1 4 2\n' | .venv/bin/python dsa/sorting/selection-sort/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/selection-sort/cpp/solution.cpp -o /tmp/atlas-selection-sort
printf '5 1 4 2\n' | /tmp/atlas-selection-sort
```

Each program prints exactly:

```text
1 2 4 5
```

Input `3 -2 +1 0 -2` prints `-2 -2 0 1 3`; empty input prints a single newline. The compiler flag can be changed to `-std=c++20`. To run Python tests and compile/execute C++ under both configured standards:

```sh
.venv/bin/python -m pytest dsa/sorting/selection-sort/tests --require-cpp
```

## 16. Edge Cases

Empty and singleton input are copied without comparisons. Repeated values sort correctly but labeled equal-key records can change order. Already sorted data performs zero swaps while retaining the full comparison count. Reverse data, negative values, zero, and `long long` boundary values need no special sorting logic. The CLI rejects malformed tokens such as `3x`, `1.2`, `1_000`, lone signs, and non-ASCII digits. Python supports values beyond C++ CLI range. NaNs or inconsistent comparators violate the ordering contract; generic comparison exceptions are not converted into arbitrary results.

Tests exercise known answers, 120 seeded random sequences, unchanged input, strings, the explicit tagged instability counterexample, exact comparison counts, malformed CLIs, large Python integers, and C++17/C++20 execution.

## 17. Advantages

The algorithm is deterministic, easy to trace, and requires constant core auxiliary memory. It performs at most one swap per outer pass and can avoid all swaps on already ordered data. Its invariant cleanly explains why final positions never need to be revisited.

## 18. Disadvantages and Limitations

The full suffix scan makes even sorted inputs quadratic. Direct swaps are unstable and may reorder records sharing a key. Small swap counts do not eliminate the cost of reading, comparing, or initially copying elements. The functions do not offer key callbacks, descending order, or external-memory processing. There are no production performance claims or heavy-input benchmarks in this lesson.

## 19. When to Use It

Choose it for learning selection invariants, comparing data-movement and comparison costs, or a tiny known-size input where a simple upper bound on swaps is valuable. Account for the initial returned-copy allocation before considering a constrained-memory use case.

## 20. When Not to Use It

Avoid it when stability matters, the input is large, comparisons are expensive, or nearly sorted data should finish quickly. [Insertion Sort](../insertion-sort/README.md) adapts to existing order; [Merge Sort](../merge-sort/README.md) provides a stable O(n log n) option. Application code should consider the language's standard sorting facilities.

## 21. Comparison With Related Algorithms

`n` denotes element count. Core space excludes the result copy shared by these APIs.

| Algorithm | Best time | Worst time | Stable here? | Movement characteristic |
| --- | --- | --- | --- | --- |
| Selection Sort | Θ(n²) | Θ(n²) | No | At most `n - 1` swaps |
| [Bubble Sort](../bubble-sort/README.md) | Θ(n) | Θ(n²) | Yes | One swap per inversion |
| [Insertion Sort](../insertion-sort/README.md) | Θ(n) | Θ(n²) | Yes | Shifts depend on inversions |
| [Heap Sort](../heap-sort/README.md) | O(n log n) | Θ(n log n) | No | Heap maintenance improves minimum/maximum selection |

Selection, Bubble, and Insertion Sort have O(1) core auxiliary space. Heap Sort also uses a constant-space iterative core, with an O(n log n) worst-case time bound. Stability is a property of the chosen implementation, not just its name.

## 22. Interview Questions

1. Why are all remaining elements scanned even if the first is the minimum? No ordering of the unexamined suffix has been established.
2. Why is the comparison count always `n(n - 1)/2`? Add the decreasing suffix lengths.
3. Does choosing the first equal minimum guarantee stability? No; trace `[2a, 2b, 1c]`.
4. Why skip self-swaps? They cannot change the order and needlessly move values.
5. How would stable selection work? Remove the chosen minimum and shift the intervening range, accepting potentially quadratic moves.

## 23. Practice Problems

1. Trace selected indices and swaps for `[4, 3, 2, 1]` and compare the two counts.
2. Count comparisons on ordered and reverse lists of length ten; both should yield 45.
3. Construct another labeled-record instability example and explain which record jumps over its equal.
4. As an independent exercise, design stable selection by shifting and compare its move count to this direct-swap implementation.

## 24. References

- [NIST Dictionary of Algorithms and Data Structures: Selection Sort](https://xlinux.nist.gov/dads/HTML/selectionSort.html) — repeated minimum selection, swap bound, and stability distinction.
- [Princeton Algorithms, 4th Edition: Elementary Sorts](https://algs4.cs.princeton.edu/21elementary/) — selection sorting and comparison with other elementary methods.
- [Princeton: Selection API documentation](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/Selection.html) — a separate educational implementation and its stated behavior.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). This original educational lesson and implementation are part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas) and distributed under its [MIT License](../../../LICENSE). See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for contribution and phase review rules.

[Sorting category](../README.md) · [Algorithm index](../../../docs/algorithm-index.md) · [Progress](../../../docs/progress.md)
