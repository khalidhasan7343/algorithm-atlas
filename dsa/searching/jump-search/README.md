# Jump Search

## 1. Algorithm Name

**Jump Search** — iterative first-occurrence lookup.

## 2. Overview

Jump Search checks the last key of successive square-root-sized blocks, then scans the first block whose endpoint is not smaller than the target. Stopping at that first eligible block preserves earliest-duplicate semantics.

## 3. Problem Statement

**Input:** a finite random-access sequence in nondecreasing order and a compatible target. Equivalence means neither key is strictly less than the other; the relation must be a consistent strict weak ordering. Python lists/tuples and C++ vectors are suitable. Default validation checks every adjacent pair and rejects a descending step. Pass `validate=False` (C++ third argument `false`) only when this precondition has already been established. This scan does not prove arbitrary comparators are consistent.

**Output:** the **first matching zero-based index**. Python returns `-1` when absent; C++ returns `std::nullopt` in `std::optional<std::size_t>`. Both CLIs print `-1` for absence. Index zero is a valid success. No input element is modified or reordered. The CLI accepts signed decimal integers; the reusable comparison API also supports compatible record types.

## 4. Why Do We Need This Algorithm?

A two-stage search illustrates how ordered data can reduce comparisons without repeatedly bisecting an interval. It exposes the tradeoff between coarse block probes and sequential local scanning. It is primarily useful for education or a workload whose block/scan access pattern is appropriate.

## 5. Real-World Applications

- Explore coarse block selection followed by a small sequential scan in an ordered in-memory table.
- Compare probe counts with Binary Search when sequential local reads and scattered probes have different costs.
- Demonstrate square-root decomposition of a search workload.

This vector/list implementation is not a disk index and does not claim actual I/O savings or superiority over Binary Search.

## 6. Core Intuition

Look at the last label in each group. If it is too small, every member of that group is too small. Once a group endpoint reaches the target, inspect that group from its beginning. Equal endpoints must stop jumping so earlier duplicates are not skipped.

## 7. Prerequisites

Nondecreasing order, random access, integer square roots, strict comparison equivalence, and [Linear Search](../linear-search/README.md). Understand why block endpoints bound all earlier block members.

## 8. Step-by-Step Working Process

1. Validate adjacent order unless explicitly disabled.
2. For nonempty data set `step=max(1,floor(sqrt(n)))`, `start=0`, and `end=min(step,n)`.
3. While `values[end-1] < target`, advance to the next capped block. Return absence if the previous block already ended at n.
4. Scan the eligible block from left to right, stopping at the first not-smaller value. Return that index only if equivalent.

**Invariant:** all indices before `start` hold keys strictly smaller than the target. The first eligible block therefore contains the first match if one exists. A failed local scan or a greater candidate rules out the target globally because later blocks cannot contain a smaller key. Every jump/scan advances, so the algorithm terminates.

## 9. Pseudocode

```text
JUMP_SEARCH(values, target, validate=true):
    if validate: reject any adjacent descending pair
    n = length(values)
    if n == 0: return ABSENT
    step = max(1, floor(sqrt(n)))
    start = 0; end = min(step,n)
    while values[end-1] < target:
        start = end
        if start == n: return ABSENT
        end = start + min(step,n-start)
    for i from start through end-1:
        if not (values[i] < target):
            if not (target < values[i]): return i
            return ABSENT
    return ABSENT
```

`ABSENT` maps to Python -1 or C++ nullopt. Intervals are half-open unless stated otherwise.

## 10. Dry Run

Input `[0,2,4,4,4,6,8,10,12,14,16,18,20,22,24,26]`, n=16, step=4, target `14`.

| Stage | Range / index | Value checked | Action |
| --- | --- | ---: | --- |
| Jump | `[0,4)`, endpoint 3 | 4 | Skip block |
| Jump | `[4,8)`, endpoint 7 | 10 | Skip block |
| Jump | `[8,12)`, endpoint 11 | 18 | Scan this block |
| Scan | index 8 | 12 | Advance |
| Scan | index 9 | 14 | Return **9** |

For target `4`, the endpoint of the very first block is equal, so jumping stops there. Scanning indices 0,1,2 returns **2**, despite duplicates continuing at indices 3 and 4 across a block boundary. Target 27 exhausts the blocks and returns -1.

## 11. Time Complexity

Let `n` be the number of elements. The table assumes constant-cost element comparisons and indexing.

| Mode / case | Time | Reason |
| --- | --- | --- |
| Unchecked best | Θ(1) | First block resolves immediately near its beginning |
| Unchecked average | Θ(sqrt(n)) | A unique successful rank is uniformly distributed |
| Unchecked worst | Θ(sqrt(n)) | O(n/step) endpoints plus O(step) local comparisons |
| Default checked API | Θ(n) for n >= 2 | Full order validation dominates |

Balancing `n/step + step` gives step near sqrt(n). Missing keys after the last block can require only the endpoint phase, still O(sqrt(n)). Constant-cost random access and machine-word arithmetic are assumed. Python integer square-root and index costs depend on bit width in a bit-operation model.

Big integers, strings, and user-defined comparisons can cost more than O(1). CLI parsing/formatting depends on text length and is separate from these API bounds.

## 12. Space Complexity

The iterative API uses **O(1) auxiliary element/index slots**, allocates no copied input or subarrays, and has no recursion stack. The result is one index or an absence marker. The caller owns the O(n) input storage. C++ passes elements and target by const reference. Python stores references; large integer payloads may increase byte costs. The standalone CLI buffers parsed values and text, using O(n) value slots plus storage proportional to input text; this is not a constant-memory process claim.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `jump_search(values, target, *, validate=True)`.

Python uses `math.isqrt` for the exact block size and caps every block at the sequence end. It scans directly by index without slicing. Only `<` is required, with strict-order equivalence rather than object equality. Checked and unchecked results share exactly the same search core.

The main guard keeps imports silent. Python requires 3.11+ and no runtime dependency. Integer CLI parsing uses signed ASCII decimal grammar and disables the interpreter decimal digit cap, subject to available resources. The `validate` switch must be exactly a bool, even for empty input; invalid switches raise TypeError, descending data raises ValueError.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::jump_search`.

The block-size helper starts with a square-root estimate that safely fits `size_t`, then corrects rounding using division comparisons instead of `step*step`. Tests include the maximum representable size without allocating such a vector. `start+min(step,n-start)` is bounded by n, and `end-1` is read only for a nonempty block. The API returns an optional unsigned index.

Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a driver. Normal compilation supplies a standalone integer CLI. Standard headers and C++17/C++20 are supported. CLI conversion uses grammar validation plus `std::from_chars`, rejecting overflow before producing output. Descending data throws `std::invalid_argument` in the default checked API.

## 15. Input and Output Examples

From the repository root, **the target comes first**, followed by zero or more values. There is no length prefix.

```sh
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | .venv/bin/python dsa/searching/jump-search/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/searching/jump-search/cpp/solution.cpp -o /tmp/atlas-jump-search
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | /tmp/atlas-jump-search
```

Both print exactly `1` followed by a newline. Target `1` with those same values prints `-1`. Input `7` means an empty sequence searched for 7 and prints `-1`; empty stdin is an error because the target is missing. Whitespace may span lines. Replace c++17 with c++20 for the other supported standard.

```sh
.venv/bin/python -m pytest --require-cpp dsa/searching/jump-search/tests
```

## 16. Edge Cases

Empty data returns absence before computing a block endpoint. Step is at least one for singleton input. Partial final blocks, lengths around perfect squares, keys after the last item, duplicates straddling blocks, negatives, and signed extrema are tested. Default validation rejects late disorder before searching; unchecked calls require already-validated data.

CLI syntax rejects bare signs, decimal points, underscores, non-ASCII digits, and trailing junk. C++ CLI keys must fit signed `long long` (64 bits on the tested platform); Python keys can be arbitrarily large within resources. No partial result is printed on validation errors. API comparison/equality failures propagate, and input is left unchanged unless user-supplied operators themselves have side effects.

## 17. Advantages

Simple block-plus-scan structure; constant auxiliary storage; first-duplicate behavior without a backward scan; a useful explicit example of balancing two competing comparison costs.

## 18. Disadvantages and Limitations

O(sqrt(n)) unchecked comparisons are asymptotically worse than Binary Search. Random-access and sorted-order assumptions remain; default validation is linear. Block size is not tuned to hardware, record costs, or actual storage pages.

## 19. When to Use It

Choose it for studying block searches or a measured environment where its access pattern fits. Validate stable data once if comparing the search core against other methods.

## 20. When Not to Use It

Do not choose it merely because the data is large or stored on disk. Binary Search is the usual baseline for sorted in-memory lookup; use Linear Search for unordered data. Do not skip validation on unknown order.

## 21. Comparison With Related Algorithms

| Method | Input / unchecked search | Tradeoff |
| --- | --- | --- |
| [Linear](../linear-search/README.md) | Unordered; O(n) worst | No sorted validation needed |
| [Binary](../binary-search/README.md) | Sorted random access; O(log n) | Strong general baseline, first-match lower bound |
| [Jump](../jump-search/README.md) | Sorted random access; O(sqrt(n)) | Coarse blocks then a short sequential scan |

Checked sorted APIs add O(n) validation. Compare equivalent contracts and account for preprocessing; fewer probes alone do not guarantee less elapsed time.

## 22. Interview Questions

1. Why stop jumping on equality rather than continue?
2. How does minimizing `n/s+s` give a square-root step?
3. Why is the last partial block safe?
4. How do default validation and core complexity differ?

## 23. Practice Problems

1. Trace target 4 across the duplicate block boundary in the example.
2. Count endpoint probes for a missing key greater than all items.
3. Test lengths one below, equal to, and one above a perfect square.
4. Compare actual element-comparison counts with Binary Search, without claiming wall-clock superiority.

## 24. References

- [NIST DADS: jump search](https://xlinux.nist.gov/dads/HTML/jumpsearch.html), including the square-root step tradeoff.
- [Python math.isqrt](https://docs.python.org/3/library/math.html#math.isqrt).

References describe the underlying methods; repository-specific first-match, validation, return-type, and CLI contracts are defined by this lesson and executable tests.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. See [CONTRIBUTING.md](../../../CONTRIBUTING.md) and the [MIT License](../../../LICENSE). This lesson and its implementations are part of the authorized Searching category.
