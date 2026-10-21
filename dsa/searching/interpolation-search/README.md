# Interpolation Search

## 1. Algorithm Name

**Interpolation Search** — iterative first-occurrence lookup.

## 2. Overview

Interpolation Search uses the numeric values at the current endpoints to estimate the target position. This implementation uses exact integer interpolation and continues left after equality to return the first duplicate, rather than an arbitrary matching probe.

## 3. Problem Statement

**Input:** a finite random-access nondecreasing integer sequence and an integer target.
Python checked mode requires exact native ints, excluding bool and int subclasses;
the target type is checked in every mode. C++ requires signed 64-bit long long.
Default validation checks types where applicable and every adjacent pair.
Pass validate=False (C++ false) only for already-validated integer data.

**Output:** the first equal zero-based index; Python -1 or C++ nullopt when absent.
The C++ result is optional size_t. Both CLIs print -1 for absence. No input is
modified or reordered. This API supports integer equality, not generic records.

## 4. Why Do We Need This Algorithm?

When ordered numeric keys are distributed approximately uniformly, the key magnitude can provide more positional information than a fixed midpoint. That extra assumption may reduce probes. The method also demonstrates why a distribution-sensitive expected bound must be distinguished from a worst-case guarantee.

## 5. Real-World Applications

- Explore exact lookup in a static, sorted numeric table with nearly uniform key spacing.
- Compare the number of probes with Binary Search on uniform versus skewed synthetic identifiers.
- Study how numeric distributions can guide access to ordered records.

These are conditional use cases, not claims that a particular database uses this lesson. Duplicates, outliers, and nonuniform gaps can remove the expected advantage.

## 6. Core Intuition

If a requested number is one quarter of the way between endpoint keys, try roughly one quarter of the way through their positions. A failed guess still excludes a range by sorted order. Unlike guessing a page in an arbitrary dictionary, this implementation has a precise integer formula and always makes progress.

## 7. Prerequisites

Nondecreasing integer sequences, random access, inclusive numeric ranges versus exclusive index bounds, integer division, and [Binary Search](../binary-search/README.md). Understand signed overflow and that multiplying two representable integers need not produce a representable fixed-width product.

## 8. Step-by-Step Working Process

1. Validate the bool switch and native Python target type. In checked mode validate all integer elements and adjacent order; C++ types are fixed at compilation.
2. Start with `[lower,upper)=[0,n)` and no saved match.
3. Continue only if the interval is nonempty and the target lies between its endpoint values.
4. If both endpoint values are equal, return lower; the range guard implies they equal the target.
5. Compute `offset=floor((target-a[lower])*(upper-lower-1)/(a[upper-1]-a[lower]))`, then probe `lower+offset`.
6. If the probe is smaller, move lower one past it. Otherwise save its index if equal and set upper to the probe, searching earlier positions.
7. Return the saved match or absence when the range is exhausted or the key is outside its endpoints.

**Invariant:** all positions before lower are strictly smaller; a saved match is valid and any earlier match must remain before upper. The range guard and nonzero denominator put the probe inside the interval. Every branch reduces interval length. Equal endpoints imply the whole interval is equal, making lower the earliest possible match.

## 9. Pseudocode

```text
INTERPOLATION_SEARCH(a, target, validate=true):
    validate switch and native Python target type
    if validate: validate element types and nondecreasing order
    lower = 0; upper = length(a); found = ABSENT
    while lower < upper and a[lower] <= target <= a[upper-1]:
        if a[lower] == a[upper-1]: return lower
        offset = exact_floor_product_ratio(target-a[lower],
                     upper-lower-1, a[upper-1]-a[lower])
        position = lower+offset
        if a[position] < target: lower = position+1
        else:
            if a[position] == target: found = position
            upper = position
    return found
```

`ABSENT` maps to Python -1 or C++ nullopt. Intervals are half-open unless stated otherwise.

## 10. Dry Run

Input `[0,10,20,20,20,30,100]`, target `20`.

| lower | upper | Endpoint values | Offset calculation | Probe / action |
| ---: | ---: | --- | --- | --- |
| 0 | 7 | 0, 100 | `floor(20*6/100)=1` | Index 1 is 10; lower becomes 2 |
| 2 | 7 | 20, 100 | `floor(0*4/80)=0` | Index 2 is 20; save 2, upper becomes 2 |

The interval is empty and the result is **2**, the first of three twenties. For `[5,5,5]`, target 5 returns 0 before any division; targets 4 or 6 fail the endpoint guard and return -1. Target 15 in the main example eventually lies outside the remaining endpoint values and returns absence.

## 11. Time Complexity

Let `n` be the number of elements. The table assumes constant-cost element comparisons and indexing.

| Mode / case | Time | Assumption |
| --- | --- | --- |
| Unchecked best | Θ(1) | Endpoint exclusion, equal endpoints, or a constant number of probes |
| Unchecked expected | O(log log n) probes | Ideal independent uniform distinct numeric keys, ordinary lookup model; not arbitrary duplicates/distributions |
| Unchecked worst | O(n), attainable | Skewed keys or a duplicate plateau can shrink by one index per probe |
| Default checked API | Θ(n) for n >= 2 | Validation plus a core with linear worst bound |

C++ computes each exact ratio in O(w) operations for w bits in size_t; on a fixed platform w is a constant (64 on the tested host), so the probe bounds give the table above. When treating word width as variable, multiply core probe cost by O(w). Python uses arbitrary-precision products/divisions, whose cost depends on key bit length. The first-match variant can scan a plateau through repeated probes, even without an explicit backward scan. All-equal input is a separate constant-time core case.

Big integers, strings, and user-defined comparisons can cost more than O(1). CLI parsing/formatting depends on text length and is separate from these API bounds.

## 12. Space Complexity

The iterative API uses **O(1) auxiliary element/index slots**, allocates no copied input or subarrays, and has no recursion stack. The result is one index or an absence marker. The caller owns the O(n) input storage. C++ passes elements and target by const reference. Python stores a constant number of integer objects, but exact interpolation temporaries may occupy O(B+log(n)) bits for B-bit keys. Constant slot count does not mean constant byte storage for unbounded integers. The standalone CLI buffers parsed values and text, using O(n) value slots plus storage proportional to input text; this is not a constant-memory process claim.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `interpolation_search(values, target, *, validate=True)`.

The Python API accepts only exact native ints, excluding bool and subclasses, and computes its interpolation product with unbounded arithmetic. The target type is checked even for empty or unchecked calls. Unchecked calls skip the full element/type/order pass and require those preconditions already established. No floating conversion or built-in search performs the lookup.

The main guard keeps imports silent. Python requires 3.11+ and no runtime dependency. Integer CLI parsing uses signed ASCII decimal grammar and disables the interpreter decimal digit cap, subject to available resources. The `validate` switch must be exactly a bool, even for empty input; invalid switches raise TypeError, descending data raises ValueError.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::interpolation_search`.

This integer-only API requires the full signed 64-bit long long range via a compile-time assertion. Endpoint and target distances use uint64_t subtraction after the range guard: even LLONG_MIN to LLONG_MAX has the exact unsigned distance 2^64-1, without signed overflow.

The private scaled_offset helper computes floor(a*b/d), with 0<=a<=d and d>0, without forming the product. It reads the bits of b from most significant to least, maintaining quotient q and remainder r for the processed prefix. Doubling r uses a comparison with d-r before addition; adding a uses d-a. Every remainder remains below d, and q never exceeds the processed prefix, hence the final width. Early zero/equal-ratio cases are exact. There are no floating casts or nonstandard 128-bit integers. Python big-int oracles independently test full-width helper results.

The offset is at most upper-lower-1, so adding it to lower remains below upper. Equal endpoints are handled before calculating a denominator.

Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a driver. Normal compilation supplies a standalone integer CLI. Standard headers and C++17/C++20 are supported. CLI conversion uses grammar validation plus `std::from_chars`, rejecting overflow before producing output. Descending data throws `std::invalid_argument` in the default checked API.

## 15. Input and Output Examples

From the repository root, **the target comes first**, followed by zero or more values. There is no length prefix.

```sh
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | .venv/bin/python dsa/searching/interpolation-search/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/searching/interpolation-search/cpp/solution.cpp -o /tmp/atlas-interpolation-search
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | /tmp/atlas-interpolation-search
```

Both print exactly `1` followed by a newline. Target `1` with those same values prints `-1`. Input `7` means an empty sequence searched for 7 and prints `-1`; empty stdin is an error because the target is missing. Whitespace may span lines. Replace c++17 with c++20 for the other supported standard.

```sh
.venv/bin/python -m pytest --require-cpp dsa/searching/interpolation-search/tests
```

## 16. Edge Cases

Empty/singleton data, zero, negatives, exact endpoints, all-equal keys, duplicate plateaus, highly skewed gaps, and both signed extrema are covered. Equal endpoints never reach division. The first occurrence is retained after a hit even when no earlier match exists. Checked Python calls reject float, NaN, infinity, bool, and int subclasses. Default order validation rejects disorder before an early hit.

CLI syntax rejects bare signs, decimal points, underscores, non-ASCII digits, and trailing junk. C++ CLI keys must fit signed `long long` (64 bits on the tested platform); Python keys can be arbitrarily large within resources. No partial result is printed on validation errors. API comparison/equality failures propagate, and input is left unchanged unless user-supplied operators themselves have side effects.

## 17. Advantages

Numeric information can reduce probes under a suitable distribution; exact arithmetic avoids precision-dependent placement; explicit equal-endpoint handling; first-match semantics; no input mutation or auxiliary arrays.

## 18. Disadvantages and Limitations

Linear worst case and distribution-sensitive expected bound; division/arithmetic overhead can outweigh probe savings. Integer-only API deliberately excludes arbitrary records, floating keys, and user-supplied distribution functions. First-match duplicate plateaus can be expensive. Default validation is linear.

## 19. When to Use It

Use for an educational or measured lookup workload over stable, ordered, approximately uniform integer keys. Validate once before repeated unchecked calls and compare against Binary Search with equivalent first-match semantics.

## 20. When Not to Use It

Prefer Binary Search for skewed, clustered, or unknown distributions when logarithmic worst-case search matters. Do not use interpolation on strings, NaNs, unordered input, or continuous unimodal optimization tasks.

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

1. Why is equal-endpoint handling required before division?
2. How can the signed endpoint difference overflow even if both keys fit?
3. Why does a uniform-data expected bound say nothing about a duplicate plateau?
4. How does saving a hit while shrinking upper retain the earliest index?

## 23. Practice Problems

1. Trace the seven-item example and target 15.
2. Construct an outlier case whose interpolation guesses advance one position at a time.
3. Compare the exact scaled-offset helper with Python integer arithmetic at full-width values.
4. Explain why removing the range guard could make an offset negative or exceed the interval.

## 24. References

- [NIST DADS: interpolation search](https://xlinux.nist.gov/dads/HTML/interpolationSearch.html).
- [Perl, Itai, and Avni, Interpolation Search—A Log Log N Search (1978)](https://doi.org/10.1145/359545.359557), the uniform-key analysis. The repository adds an explicit first-match duplicate contract.

References describe the underlying methods; repository-specific first-match, validation, return-type, and CLI contracts are defined by this lesson and executable tests.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. See [CONTRIBUTING.md](../../../CONTRIBUTING.md) and the [MIT License](../../../LICENSE). This lesson and its implementations are part of the authorized Searching category.
