# Binary Search

## 1. Algorithm Name

**Binary Search** — iterative first-occurrence lookup.

## 2. Overview

This iterative lower-bound variant finds the first occurrence in a nondecreasing sequence, even when duplicates span the midpoint. It narrows a half-open interval instead of returning an arbitrary equal pivot.

## 3. Problem Statement

**Input:** a finite random-access sequence in nondecreasing order and a compatible target. Equivalence means neither key is strictly less than the other; the relation must be a consistent strict weak ordering. Python lists/tuples and C++ vectors are suitable. Default validation checks every adjacent pair and rejects a descending step. Pass `validate=False` (C++ third argument `false`) only when this precondition has already been established. This scan does not prove arbitrary comparators are consistent.

**Output:** the **first matching zero-based index**. Python returns `-1` when absent; C++ returns `std::nullopt` in `std::optional<std::size_t>`. Both CLIs print `-1` for absence. Index zero is a valid success. No input element is modified or reordered. The CLI accepts signed decimal integers; the reusable comparison API also supports compatible record types.

## 4. Why Do We Need This Algorithm?

Sorted random-access collections permit ruling out whole intervals with one comparison. First-match behavior is useful when equal keys mark the beginning of a group, and it avoids a potentially linear backward scan after an arbitrary duplicate is found.

## 5. Real-World Applications

- Find the earliest exact timestamp in an ordered event batch with duplicate timestamps.
- Locate the first equal identifier in an immutable sorted table reused for many queries.
- Teach boundary location, which underlies insertion positions and ordered range queries.

This API returns exact matches only; insertion positions and ranges are not exposed as extra features.

## 6. Core Intuition

Maintain the point where values stop being strictly less than the target. At a midpoint, a smaller item rules out the left portion; an equal or larger item moves the right boundary left. Equality must not trigger an early arbitrary-index return.

## 7. Prerequisites

Random-access sequences, consistent strict ordering, half-open intervals, integer division, and [complexity notation](../../../docs/complexity-cheatsheet.md). Sorting preprocessing is separate from searching.

## 8. Step-by-Step Working Process

1. Optionally check every adjacent pair for a descending step.
2. Set `lower=0`, `upper=n`.
3. Compute `middle=lower+floor((upper-lower)/2)`.
4. If the middle value is smaller, set `lower=middle+1`; otherwise set `upper=middle`.
5. At convergence, check that the position is inside the array and equivalent to the target.

**Invariant:** every position before `lower` is smaller than the target; every position at or after `upper` is not smaller. The interval length strictly decreases. At convergence `lower` is the earliest not-smaller position; the final equivalence check distinguishes a match from a missing key.

## 9. Pseudocode

```text
BINARY_SEARCH(values, target, validate=true):
    if validate: reject any adjacent descending pair
    lower = 0; upper = length(values)
    while lower < upper:
        middle = lower + floor((upper-lower)/2)
        if values[middle] < target: lower = middle+1
        else: upper = middle
    if lower < length(values) and not (target < values[lower]):
        return lower
    return ABSENT
```

`ABSENT` maps to Python -1 or C++ nullopt. Intervals are half-open unless stated otherwise.

## 10. Dry Run

Input `[-9,-4,-4,0,2,2,8]`, target `2`. Validation finds no descending pair.

| lower | upper (exclusive) | middle | Value | Next interval |
| ---: | ---: | ---: | ---: | --- |
| 0 | 7 | 3 | 0 | `[4,7)` |
| 4 | 7 | 5 | 2 | `[4,5)`; keep seeking an earlier equal key |
| 4 | 5 | 4 | 2 | `[4,4)` |

Position 4 is in bounds and equivalent, so return **4**, not 5. Target `1` follows the same boundary trace but the final value 2 is greater, so return -1. An empty sequence starts with `[0,0)` and returns absence without indexing.

## 11. Time Complexity

Let `n` be the number of elements. The table assumes constant-cost element comparisons and indexing.

| Mode / case | Time | Reason |
| --- | --- | --- |
| Unchecked core, best/average/worst for growing n | Θ(log(n+1)) | Lower-bound search continues past equality and shrinks by roughly half each iteration |
| Default checked API, n >= 2 | Θ(n) | Full adjacent validation dominates the logarithmic core |
| Empty or singleton | Θ(1) | Constant-size work |

This is not the any-match variant with an O(1) midpoint-hit best case. Under constant-cost operations there is no distribution-specific average improvement claimed. If callers validate immutable input once, later `validate=False` calls recover the logarithmic bound. Sorting a previously unordered array is an additional cost and changes index meaning.

Big integers, strings, and user-defined comparisons can cost more than O(1). CLI parsing/formatting depends on text length and is separate from these API bounds.

## 12. Space Complexity

The iterative API uses **O(1) auxiliary element/index slots**, allocates no copied input or subarrays, and has no recursion stack. The result is one index or an absence marker. The caller owns the O(n) input storage. C++ passes elements and target by const reference. Python stores references; large integer payloads may increase byte costs. The standalone CLI buffers parsed values and text, using O(n) value slots plus storage proportional to input text; this is not a constant-memory process claim.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `binary_search(values, target, *, validate=True)`.

A nested slice or copied subarray is never created. Comparisons use only `<`; two values are equivalent if neither is smaller, even for records whose object equality differs. The final not-less comparison is sufficient because the lower-bound invariant already establishes the opposite direction.

The main guard keeps imports silent. Python requires 3.11+ and no runtime dependency. Integer CLI parsing uses signed ASCII decimal grammar and disables the interpreter decimal digit cap, subject to available resources. The `validate` switch must be exactly a bool, even for empty input; invalid switches raise TypeError, descending data raises ValueError.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::binary_search`.

The template takes a const vector and returns an optional `std::size_t`. Half-open bounds allow `upper=n` without dereferencing it. `lower+(upper-lower)/2` cannot exceed `upper` or overflow; when the interval is nonempty, `middle<upper`, so `middle+1` is representable. There is no `middle-1` unsigned underflow.

Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a driver. Normal compilation supplies a standalone integer CLI. Standard headers and C++17/C++20 are supported. CLI conversion uses grammar validation plus `std::from_chars`, rejecting overflow before producing output. Descending data throws `std::invalid_argument` in the default checked API.

## 15. Input and Output Examples

From the repository root, **the target comes first**, followed by zero or more values. There is no length prefix.

```sh
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | .venv/bin/python dsa/searching/binary-search/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/searching/binary-search/cpp/solution.cpp -o /tmp/atlas-binary-search
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | /tmp/atlas-binary-search
```

Both print exactly `1` followed by a newline. Target `1` with those same values prints `-1`. Input `7` means an empty sequence searched for 7 and prints `-1`; empty stdin is an error because the target is missing. Whitespace may span lines. Replace c++17 with c++20 for the other supported standard.

```sh
.venv/bin/python -m pytest --require-cpp dsa/searching/binary-search/tests
```

## 16. Edge Cases

An all-equal array returns 0 for the matching key. Queries below, between, or above keys return absence. Default validation scans the complete input even if index 0 could match, so late disorder is rejected. Empty and singleton inputs are valid. Incomparable values may raise TypeError in Python; NaNs or inconsistent comparisons violate the ordering precondition.

CLI syntax rejects bare signs, decimal points, underscores, non-ASCII digits, and trailing junk. C++ CLI keys must fit signed `long long` (64 bits on the tested platform); Python keys can be arbitrarily large within resources. No partial result is printed on validation errors. API comparison/equality failures propagate, and input is left unchanged unless user-supplied operators themselves have side effects.

## 17. Advantages

Deterministic logarithmic unchecked search; direct first-duplicate result; iterative constant workspace; overflow-safe midpoint; no recursion-depth limitation.

## 18. Disadvantages and Limitations

Default validation costs linear time per call. Random indexing and nondecreasing order are required; linked-list indexing defeats the stated bound. Comparisons must describe one consistent ordering. The function does not sort input or build an index.

## 19. When to Use It

Use for exact first-match lookup on sorted random-access data, especially many queries on an immutable collection that can be validated once.

## 20. When Not to Use It

Avoid unchecked calls on unverified or concurrently modified data. Prefer Linear Search for a single query on a small unordered collection. Do not infer a valid ordering merely because an adjacent check happens to pass for NaNs.

## 21. Comparison With Related Algorithms

| Method | Input / unchecked search | Tradeoff |
| --- | --- | --- |
| [Linear](../linear-search/README.md) | Unordered; O(n) worst | No sorted validation needed |
| [Binary](../binary-search/README.md) | Sorted random access; O(log n) | Strong general baseline, first-match lower bound |
| [Jump](../jump-search/README.md) | Sorted random access; O(sqrt(n)) | Coarse blocks then a short sequential scan |

Checked sorted APIs add O(n) validation. Compare equivalent contracts and account for preprocessing; fewer probes alone do not guarantee less elapsed time.

## 22. Interview Questions

1. Why does moving `upper` on equality preserve the first match?
2. What invariants justify the final equivalence check?
3. Why does midpoint subtraction avoid overflow?
4. Why is the default public runtime linear despite a logarithmic search loop?

## 23. Practice Problems

1. Trace targets -10, -4, 1, and 9 in the example.
2. Derive a comparison bound for all-equal sequences.
3. Test equal-key records with different identities and no equality operator.
4. Explain how a separate insertion-position API would differ from this exact-match contract.

## 24. References

- [NIST DADS: binary search and safe midpoint](https://xlinux.nist.gov/dads/HTML/binarySearch.html).
- [Princeton BinarySearch documentation](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/BinarySearch.html), an any-match reference; our first-match variant deliberately differs.

References describe the underlying methods; repository-specific first-match, validation, return-type, and CLI contracts are defined by this lesson and executable tests.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. See [CONTRIBUTING.md](../../../CONTRIBUTING.md) and the [MIT License](../../../LICENSE). This lesson and its implementations are part of the authorized Searching category.
