# Exponential Search

## 1. Algorithm Name

**Exponential Search** — iterative first-occurrence lookup.

## 2. Overview

Exponential Search first probes indices 1,2,4,8 and so on to bracket the target, then runs a lower-bound binary search inside the bracket. It returns the first equivalent index. This implementation operates on finite random-access sequences whose length is available.

## 3. Problem Statement

**Input:** a finite random-access sequence in nondecreasing order and a compatible target. Equivalence means neither key is strictly less than the other; the relation must be a consistent strict weak ordering. Python lists/tuples and C++ vectors are suitable. Default validation checks every adjacent pair and rejects a descending step. Pass `validate=False` (C++ third argument `false`) only when this precondition has already been established. This scan does not prove arbitrary comparators are consistent.

**Output:** the **first matching zero-based index**. Python returns `-1` when absent; C++ returns `std::nullopt` in `std::optional<std::size_t>`. Both CLIs print `-1` for absence. Index zero is a valid success. No input element is modified or reordered. The CLI accepts signed decimal integers; the reusable comparison API also supports compatible record types.

## 4. Why Do We Need This Algorithm?

A global binary search always pays for the full table size. Doubling finds a small bracket when the target is near the front, making unchecked cost depend on the target position. It also demonstrates how to bound expansion without overflowing or reading past the sequence.

## 5. Real-World Applications

- Locate near-front keys repeatedly in a long sorted immutable sequence.
- Study the doubling/galloping bracket idea used in ordered processing.
- Compare position-sensitive probe counts with Binary Search across a fixed table.

The original unbounded-search setting motivates the method, but this API requires finite length; it does not claim to expose an infinite-array adapter or a production merge operator.

## 6. Core Intuition

Try a nearby point, then twice as far, until the target cannot be beyond the bracket. Every skipped endpoint is strictly smaller than the target. Once the bracket is known, use the Binary Search boundary invariant to locate the first possible match.

## 7. Prerequisites

Nondecreasing random access, [Binary Search](../binary-search/README.md), doubling, half-open intervals, and safe unsigned index arithmetic. Equal keys must stop expansion rather than be skipped.

## 8. Step-by-Step Working Process

1. Check adjacent order unless validation is disabled.
2. Return absence on empty input. Resolve index zero directly when its value is not smaller than the target.
3. Start lower=bound=1. While an in-range bound holds a smaller key, move lower to bound+1 and double bound, saturating at n.
4. Set upper to bound+1 when that probe exists, otherwise n.
5. Run a lower-bound binary search on [lower,upper), moving upper on equality.
6. Check the final position for equivalence and return it or absence.

**Invariant:** everything before lower is smaller than the target. A terminating in-range bound is not smaller, or n is the exclusive limit. Therefore the first possible match lies in the bracket or at its lower-bound endpoint. The binary phase preserves this invariant and terminates. Strict comparison during expansion prevents skipping earlier duplicates.

## 9. Pseudocode

```text
EXPONENTIAL_SEARCH(a, target, validate=true):
    if validate: reject any adjacent descending pair
    n = length(a)
    if n == 0: return ABSENT
    if not (a[0] < target):
        return 0 if not (target < a[0]) else ABSENT
    lower = bound = 1
    while bound < n and a[bound] < target:
        lower = bound+1
        bound = n if bound >= n-bound else bound+bound
    upper = bound+1 if bound < n else n
    while lower < upper:
        middle = lower + floor((upper-lower)/2)
        if a[middle] < target: lower = middle+1
        else: upper = middle
    if lower < n and not (target < a[lower]): return lower
    return ABSENT
```

`ABSENT` maps to Python -1 or C++ nullopt. Intervals are half-open unless stated otherwise.

## 10. Dry Run

Input `[0,2,4,6,8,10,10,10,12,14,16,18]`, target `10`. Index zero is too small.

| Phase | Probe / interval | Value | Action |
| --- | --- | ---: | --- |
| Expand | index 1 | 2 | lower=2, bound=2 |
| Expand | index 2 | 4 | lower=3, bound=4 |
| Expand | index 4 | 8 | lower=5, bound=8 |
| Expand | index 8 | 12 | Stop; bracket `[5,9)` |
| Binary | midpoint 7 | 10 | upper=7 |
| Binary | midpoint 6 | 10 | upper=6 |
| Binary | midpoint 5 | 10 | upper=5 |

Return **5**, the earliest ten. With only the first seven values, doubling from bound 4 caps at n=7, and `[5,7)` still returns 5. Target below the first key returns -1 immediately in unchecked mode; target above the last key expands safely to the end.

## 11. Time Complexity

Let `n` be the number of elements. The table assumes constant-cost element comparisons and indexing.

| Mode / case | Time | Assumption |
| --- | --- | --- |
| Unchecked best | Θ(1) | Target at/before the beginning, empty data, or fixed small position |
| Unchecked position-sensitive | O(1+log(p+1)) | p is the first not-smaller insertion position, 0<=p<=n |
| Successful average | Θ(log(n+1)) | Uniform unique matching rank |
| Unchecked worst | Θ(log(n+1)) | Target near/beyond the end |
| Default checked API | Θ(n) for n>=2 | Full validation dominates |

Doubling takes logarithmically many probes in p; the bracket width is O(p), so binary narrowing has the same bound. The supplied container still has known finite length. Sorting/index construction and validation-once costs must be counted separately across repeated queries.

Big integers, strings, and user-defined comparisons can cost more than O(1). CLI parsing/formatting depends on text length and is separate from these API bounds.

## 12. Space Complexity

The iterative API uses **O(1) auxiliary element/index slots**, allocates no copied input or subarrays, and has no recursion stack. The result is one index or an absence marker. The caller owns the O(n) input storage. C++ passes elements and target by const reference. Python stores references; large integer payloads may increase byte costs. The standalone CLI buffers parsed values and text, using O(n) value slots plus storage proportional to input text; this is not a constant-memory process claim.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `exponential_search(values, target, *, validate=True)`.

Python uses only indexed reads and < comparisons; it does not slice a bracket or call a library binary search. The same saturating bound formula is used as C++ for comparable behavior. A virtual range test searches over 2^40 positions without allocation and checks that fewer than 200 element reads are needed.

The main guard keeps imports silent. Python requires 3.11+ and no runtime dependency. Integer CLI parsing uses signed ASCII decimal grammar and disables the interpreter decimal digit cap, subject to available resources. The `validate` switch must be exactly a bool, even for empty input; invalid switches raise TypeError, descending data raises ValueError.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::exponential_search`.

The private expansion helper assumes 0<bound<n and tests bound>=n-bound before doubling. If true it returns n; otherwise bound+bound<n is representable. lower=bound+1 is assigned only when bound<n, and upper=bound+1 is likewise guarded. The binary midpoint uses lower+(upper-lower)/2. Tests exercise expansion near size_t maximum independently of vector allocation, plus actual vectors around powers of two.

Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a driver. Normal compilation supplies a standalone integer CLI. Standard headers and C++17/C++20 are supported. CLI conversion uses grammar validation plus `std::from_chars`, rejecting overflow before producing output. Descending data throws `std::invalid_argument` in the default checked API.

## 15. Input and Output Examples

From the repository root, **the target comes first**, followed by zero or more values. There is no length prefix.

```sh
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | .venv/bin/python dsa/searching/exponential-search/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/searching/exponential-search/cpp/solution.cpp -o /tmp/atlas-exponential-search
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | /tmp/atlas-exponential-search
```

Both print exactly `1` followed by a newline. Target `1` with those same values prints `-1`. Input `7` means an empty sequence searched for 7 and prints `-1`; empty stdin is an error because the target is missing. Whitespace may span lines. Replace c++17 with c++20 for the other supported standard.

```sh
.venv/bin/python -m pytest --require-cpp dsa/searching/exponential-search/tests
```

## 16. Edge Cases

Empty and singleton data, index zero, duplicate blocks crossing powers of two, a capped final bracket, and absent targets below/inside/above the sequence are tested. The bound is never dereferenced once it equals n. Nondecreasing order is validated even if index zero could otherwise resolve the target. Strict weak ordering excludes NaNs and inconsistent comparisons.

CLI syntax rejects bare signs, decimal points, underscores, non-ASCII digits, and trailing junk. C++ CLI keys must fit signed `long long` (64 bits on the tested platform); Python keys can be arbitrarily large within resources. No partial result is printed on validation errors. API comparison/equality failures propagate, and input is left unchanged unless user-supplied operators themselves have side effects.

## 17. Advantages

Position-sensitive unchecked cost near the front; logarithmic worst-case core; constant workspace; explicit bounded expansion; first duplicates found with lower-bound narrowing rather than backward scanning.

## 18. Disadvantages and Limitations

Extra bracket probes can lose to a global Binary Search for late targets. Checked calls are linear. This finite sequence API does not implement the original unknown-length interface. No promise is made about actual cache or latency benefits.

## 19. When to Use It

Use when many queries concentrate near the front of stable sorted data, or to study galloping brackets. Establish order once to measure its actual unchecked core.

## 20. When Not to Use It

For uniformly distributed ranks, Binary Search is a simpler baseline. Unsorted collections need Linear Search or preprocessing. Do not pass an infinite stream or a linked list and assume the documented random-access costs apply.

## 21. Comparison With Related Algorithms

| Method | Input / unchecked search | Tradeoff |
| --- | --- | --- |
| [Linear](../linear-search/README.md) | Unordered; O(n) worst | No sorted validation needed |
| [Binary](../binary-search/README.md) | Sorted random access; O(log n) | Strong general baseline, first-match lower bound |
| [Jump](../jump-search/README.md) | Sorted random access; O(sqrt(n)) | Coarse blocks then a short sequential scan |
| [Interpolation](../interpolation-search/README.md) | Sorted integers; expected O(log log n) under uniform distinct keys, worst O(n) | Distribution-sensitive and exact integer estimates |
| [Exponential](../exponential-search/README.md) | Sorted random access; O(1+log(p+1)) for insertion position p | Near-front bracket advantage |
| [Ternary](../ternary-search/README.md) | Sorted random access; O(log n) | Two-pivot lookup, not unimodal optimization |

Checked sorted APIs add O(n) validation. Compare equivalent contracts and account for preprocessing; fewer probes alone do not guarantee less elapsed time.

## 22. Interview Questions

1. Why must equality stop expansion?
2. Why is checking n-bound before doubling safer than checking a doubled value afterwards?
3. What happens when the doubled bound would pass n?
4. Why does the near-front bound disappear in the default validated API?

## 23. Practice Problems

1. Trace target 10 in both example lengths 12 and 7.
2. Test positions one below, equal to, and one above powers of two.
3. Count reads for a near-front target as n grows.
4. Describe what a separate unknown-length accessor would need to signal, without changing this finite API.

## 24. References

- [Bentley and Yao, An almost optimal algorithm for unbounded searching (1976)](https://doi.org/10.1016/0020-0190(76)90071-5). This finite doubling-plus-binary lesson does not claim every optimization of that paper.
- [NIST DADS: binary search](https://xlinux.nist.gov/dads/HTML/binarySearch.html), used for bracket narrowing.

References describe the underlying methods; repository-specific first-match, validation, return-type, and CLI contracts are defined by this lesson and executable tests.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. See [CONTRIBUTING.md](../../../CONTRIBUTING.md) and the [MIT License](../../../LICENSE). This lesson and its implementations are part of the authorized Searching category.
