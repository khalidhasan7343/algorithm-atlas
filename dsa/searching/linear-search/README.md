# Linear Search

## 1. Algorithm Name

**Linear Search** — also called sequential search.

## 2. Overview

Sequential search walks from the beginning and returns as soon as an item equals the target. It works on unordered data and retains the original position of every item. It is a useful baseline against which more specialized searches can be evaluated.

## 3. Problem Statement

**Input:** a finite sequence of equality-comparable elements and a compatible target. No ordering requirement applies; input positions refer to the supplied sequence.

**Output:** the **first matching zero-based index**. Python returns `-1` when absent; C++ returns `std::nullopt` in `std::optional<std::size_t>`. Both CLIs print `-1` for absence. Index zero is a valid success. No input element is modified or reordered. The CLI accepts signed decimal integers; the reusable comparison API also supports compatible record types.

## 4. Why Do We Need This Algorithm?

Many collections are small, transient, or lack an index. Sorting solely to answer one query costs work and changes positions; building a hash index also needs preprocessing and compatible keys. A direct scan needs neither prerequisite and gives a predictable earliest match.

## 5. Real-World Applications

- Find the first matching entry in a short configuration or priority list, where position matters.
- Check an unsorted batch of identifiers once without paying for a persistent index.
- Search small collections of equality-comparable records that do not provide an ordering.

These are suitable use cases, not claims about particular deployed products.

## 6. Core Intuition

Inspect labeled boxes from left to right. Once a label matches, every earlier box has already failed, so this is necessarily the first occurrence. Finding no match requires opening every box.

## 7. Prerequisites

Sequence iteration, zero-based indexing, equality, and the difference between an absent value and index zero. No sorted order, hashing, recursion, or numeric distribution is required.

## 8. Step-by-Step Working Process

1. Start at index zero.
2. Compare the current element with the target using equality.
3. Return its index immediately if equal; otherwise advance one position.
4. Return absence after exhausting the sequence.

**Invariant:** before position `i`, no earlier position equals the target. Each failed comparison extends that invariant; a success is therefore the first match. The iterator advances finitely and never changes the data.

## 9. Pseudocode

```text
LINEAR_SEARCH(values, target):
    for i from 0 through length(values)-1:
        if values[i] == target: return i
    return ABSENT
```

`ABSENT` maps to Python -1 or C++ nullopt. Intervals are half-open unless stated otherwise.

## 10. Dry Run

Input `[4, -2, 4, 0, -2]`, target `-2`.

| Index | Value | Comparison | Action |
| --- | --- | --- | --- |
| 0 | 4 | `4 == -2` is false | Advance |
| 1 | -2 | Equal | Return **1** |

The later duplicate at index 4 is never inspected. For target `3`, all five comparisons fail and the result is `-1`. Empty input makes no element comparisons; `[7]` returns 0 for target 7 and -1 for target 8.

## 11. Time Complexity

Let `n` be the number of elements. The table assumes constant-cost element comparisons and indexing.

| Case | Time | Assumption |
| --- | --- | --- |
| Best | Θ(1) | First item matches, or input is empty |
| Successful average | Θ(n) | Unique target position is uniformly random: `(n+1)/2` equality checks |
| Worst / unsuccessful | Θ(n) | Match at the end, or no match |

Duplicates change the first-match position distribution; there is no universal average independent of that distribution. Equality cost multiplies the number of checks. There is no hidden validation pass before a successful early return.

Big integers, strings, and user-defined comparisons can cost more than O(1). CLI parsing/formatting depends on text length and is separate from these API bounds.

## 12. Space Complexity

The iterative API uses **O(1) auxiliary element/index slots**, allocates no copied input or subarrays, and has no recursion stack. The result is one index or an absence marker. The caller owns the O(n) input storage. C++ passes elements and target by const reference. Python stores references; large integer payloads may increase byte costs. The standalone CLI buffers parsed values and text, using O(n) value slots plus storage proportional to input text; this is not a constant-memory process claim.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `linear_search(values, target)`.

The Python function iterates directly with `enumerate`, using `==` rather than imposing an ordering. It accepts tuples as well as lists; examples with strings and dictionaries demonstrate equality-only use. It never builds a copy or calls a library search routine.

The main guard keeps imports silent. Python requires 3.11+ and no runtime dependency. Integer CLI parsing uses signed ASCII decimal grammar and disables the interpreter decimal digit cap, subject to available resources.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::linear_search`.

The template requires equality-comparable elements and takes a const vector reference plus a const target reference. `std::size_t` indices advance only while strictly below vector size. Returning an optional index avoids casting large unsigned indices to a signed sentinel. No subtraction from zero or midpoint arithmetic is needed.

Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a driver. Normal compilation supplies a standalone integer CLI. Standard headers and C++17/C++20 are supported. CLI conversion uses grammar validation plus `std::from_chars`, rejecting overflow before producing output.

## 15. Input and Output Examples

From the repository root, **the target comes first**, followed by zero or more values. There is no length prefix.

```sh
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | .venv/bin/python dsa/searching/linear-search/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/searching/linear-search/cpp/solution.cpp -o /tmp/atlas-linear-search
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | /tmp/atlas-linear-search
```

Both print exactly `1` followed by a newline. Target `1` with those same values prints `-1`. Input `7` means an empty sequence searched for 7 and prints `-1`; empty stdin is an error because the target is missing. Whitespace may span lines. Replace c++17 with c++20 for the other supported standard.

```sh
.venv/bin/python -m pytest --require-cpp dsa/searching/linear-search/tests
```

## 16. Edge Cases

Unordered and descending collections are accepted. Duplicates return their earliest original position. Negative numbers, zeros, and signed integer boundaries are ordinary keys. A successful first comparison does not inspect the suffix; equality exceptions propagate from the API. The CLI rejects missing target, malformed tokens, or C++ overflow before printing anything.

CLI syntax rejects bare signs, decimal points, underscores, non-ASCII digits, and trailing junk. C++ CLI keys must fit signed `long long` (64 bits on the tested platform); Python keys can be arbitrarily large within resources. No partial result is printed on validation errors. API comparison/equality failures propagate, and input is left unchanged unless user-supplied operators themselves have side effects.

## 17. Advantages

No preprocessing, ordering, or hashability requirement; constant workspace; straightforward first-match proof; early success for front-heavy workloads; original index meaning is preserved.

## 18. Disadvantages and Limitations

Large repeated searches rescan the same data. An absent target takes a full scan. Expensive record equality can dominate. This is a single-value lookup API, not a substring matcher or an index-building facility.

## 19. When to Use It

Prefer a scan for one query over a small or unordered collection, especially when the earliest entry has meaning or equality exists without ordering.

## 20. When Not to Use It

For many queries on already ordered random-access data, Binary Search avoids repeated full scans. A maintained hash index may fit exact-key workloads when preprocessing, extra memory, and loss of positional ordering are acceptable.

## 21. Comparison With Related Algorithms

| Method | Input / unchecked search | Tradeoff |
| --- | --- | --- |
| [Linear](../linear-search/README.md) | Unordered; O(n) worst | No sorted validation needed |
| [Binary](../binary-search/README.md) | Sorted random access; O(log n) | Strong general baseline, first-match lower bound |
| [Jump](../jump-search/README.md) | Sorted random access; O(sqrt(n)) | Coarse blocks then a short sequential scan |

Checked sorted APIs add O(n) validation. Compare equivalent contracts and account for preprocessing; fewer probes alone do not guarantee less elapsed time.

## 22. Interview Questions

1. Why does returning immediately prove the index is the first duplicate?
2. Why can an absent key not be ruled out before scanning an arbitrary suffix?
3. When does preprocessing an index become worthwhile across many queries?
4. Why does equality-only support permit records that Binary Search cannot order?

## 23. Practice Problems

1. Trace target 4 in `[4,-2,4,0,-2]`; explain why the answer is 0.
2. Count equality operations for every target position and derive the successful uniform average.
3. Write tests for equality-comparable records without a less-than operator.
4. Design a separate all-occurrences API and explain its output-space cost; it is not implemented here.

## 24. References

- [NIST DADS: linear search](https://xlinux.nist.gov/dads/HTML/linearSearch.html).
- [Python sequence semantics](https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range).

References describe the underlying methods; repository-specific first-match, validation, return-type, and CLI contracts are defined by this lesson and executable tests.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. See [CONTRIBUTING.md](../../../CONTRIBUTING.md) and the [MIT License](../../../LICENSE). This lesson and its implementations are part of the authorized Searching category.
