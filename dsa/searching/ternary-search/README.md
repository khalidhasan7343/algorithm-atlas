# Ternary Search

## 1. Algorithm Name

**Ternary Search** — iterative first-occurrence lookup.

## 2. Overview

This lesson implements **exact lookup in a nondecreasing sequence**, using two pivots to reduce the candidate region to roughly one third. It returns the first equivalent index. It is not a numerical optimizer for a unimodal function and does not accept function callbacks or tolerance arguments.

## 3. Problem Statement

**Input:** a finite random-access sequence in nondecreasing order and a compatible target. Equivalence means neither key is strictly less than the other; the relation must be a consistent strict weak ordering. Python lists/tuples and C++ vectors are suitable. Default validation checks every adjacent pair and rejects a descending step. Pass `validate=False` (C++ third argument `false`) only when this precondition has already been established. This scan does not prove arbitrary comparators are consistent.

**Output:** the **first matching zero-based index**. Python returns `-1` when absent; C++ returns `std::nullopt` in `std::optional<std::size_t>`. Both CLIs print `-1` for absence. Index zero is a valid success. No input element is modified or reordered. The CLI accepts signed decimal integers; the reusable comparison API also supports compatible record types.

## 4. Why Do We Need This Algorithm?

Comparing two pivot values illustrates another divide-and-conquer boundary strategy. It makes it possible to compare shrink factor against comparisons per iteration, while preserving duplicate semantics. The ambiguous name is resolved explicitly so sorted lookup is not confused with unimodal optimization.

## 5. Real-World Applications

- Perform first-match lookup in a sorted release manifest or static identifier table when evaluating a two-pivot policy; earlier equal entries retain their positional meaning.
- Teach two-pivot interval elimination on ordered identifiers.
- Compare search comparison counts against Binary Search in an algorithm laboratory.
- Demonstrate first-match lower-bound reasoning across three candidate regions.

Binary Search is usually the stronger practical baseline for ordinary lookup. Unimodal cost minimization is a separate setting: comparing function values can eliminate one side only under a unimodality assumption. That optimizer is deliberately not implemented here.

## 6. Core Intuition

Place two markers near one third and two thirds of the interval. If the earlier marker is not smaller, the boundary is on its left. If the later marker is smaller, the boundary is on its right. Otherwise it lies between the markers. Equal pivots must retain the leftmost possible boundary.

## 7. Prerequisites

Sorted random-access sequences, consistent strict ordering, half-open intervals, and [Binary Search](../binary-search/README.md). Know the distinction between searching for an exact key and minimizing a function.

## 8. Step-by-Step Working Process

1. Validate adjacent nondecreasing order unless disabled.
2. Set lower=0, upper=n.
3. While nonempty, set third=floor((upper-lower)/3), first=lower+third, second=upper-1-third.
4. If the first pivot is not smaller than target, set upper=first.
5. Otherwise, if the second pivot is smaller, set lower=second+1.
6. Otherwise keep only [first+1,second). The second pivot is a known not-smaller boundary and need not remain inside the interval.
7. At convergence verify that lower is in bounds and equivalent.

**Invariant:** all positions before lower are smaller and all positions at/after upper are not smaller. Each branch preserves the boundary and strictly shrinks the interval. In the middle branch first<second must hold: coincident pivots could not satisfy its two opposite comparisons. A returned boundary is therefore the first match, not merely a matching pivot.

## 9. Pseudocode

```text
TERNARY_SEARCH(a, target, validate=true):
    if validate: reject any adjacent descending pair
    lower = 0; upper = length(a)
    while lower < upper:
        third = floor((upper-lower)/3)
        first = lower+third
        second = upper-1-third
        if not (a[first] < target): upper = first
        else if a[second] < target: lower = second+1
        else: lower = first+1; upper = second
    if lower < length(a) and not (target < a[lower]): return lower
    return ABSENT
```

`ABSENT` maps to Python -1 or C++ nullopt. Intervals are half-open unless stated otherwise.

## 10. Dry Run

Input `[-6,-3,0,0,0,0,3,6,9]`, target `0`.

| lower | upper | first, second | Values | Action |
| ---: | ---: | --- | --- | --- |
| 0 | 9 | 3,5 | 0,0 | First pivot is not smaller; upper=3 |
| 0 | 3 | 1,1 | -3,-3 | Second pivot is smaller; lower=2 |
| 2 | 3 | 2,2 | 0,0 | First pivot is not smaller; upper=2 |

Converged position **2** is equivalent and precedes the other zeros. Coincident pivots in short intervals are safe. Target 6 returns 7; target 7 converges to index 8 whose value 9 is greater, hence returns -1. Empty input performs no probes.

## 11. Time Complexity

Let `n` be the number of elements. The table assumes constant-cost element comparisons and indexing.

| Mode / case | Time | Explanation |
| --- | --- | --- |
| Unchecked best/average/worst for growing n | Θ(log(n+1)) | This lower-bound variant keeps narrowing even after equality |
| Default checked API | Θ(n), n>=2 | Adjacent validation dominates |
| Empty / singleton | Θ(1) | Constant-size work |

There are at most two pivot comparisons per iteration and one final equivalence check. The interval shrinks to about one third; rounding is handled for tiny lengths. A smaller shrink ratio is not automatically faster: two comparisons per step can exceed Binary Search's comparison budget. No constant-time equality-hit best case is claimed for this particular boundary variant.

Big integers, strings, and user-defined comparisons can cost more than O(1). CLI parsing/formatting depends on text length and is separate from these API bounds.

## 12. Space Complexity

The iterative API uses **O(1) auxiliary element/index slots**, allocates no copied input or subarrays, and has no recursion stack. The result is one index or an absence marker. The caller owns the O(n) input storage. C++ passes elements and target by const reference. Python stores references; large integer payloads may increase byte costs. The standalone CLI buffers parsed values and text, using O(n) value slots plus storage proportional to input text; this is not a constant-memory process claim.

## 13. Python Implementation

[python/solution.py](python/solution.py) exposes `ternary_search(values, target, *, validate=True)`.

The implementation uses two integer indices and only <; it never sorts, slices, or delegates to Binary Search. The loop handles one-, two-, and three-element ranges directly without a separate recursive base case. Default validation and the unchecked search share identical narrowing logic.

The main guard keeps imports silent. Python requires 3.11+ and no runtime dependency. Integer CLI parsing uses signed ASCII decimal grammar and disables the interpreter decimal digit cap, subject to available resources. The `validate` switch must be exactly a bool, even for empty input; invalid switches raise TypeError, descending data raises ValueError.

## 14. C++ Implementation

[cpp/solution.cpp](cpp/solution.cpp) exposes `algorithm_atlas::ternary_search`.

The template uses size_t half-open bounds. first=lower+(upper-lower)/3 stays below upper. The nonempty guard ensures upper-1 exists, and third<=upper-lower-1 makes upper-1-third safe. Updates to first+1 or second+1 remain at most upper. No sum of both bounds, signed midpoint narrowing, or recursive stack is used. The result is optional size_t.

Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a driver. Normal compilation supplies a standalone integer CLI. Standard headers and C++17/C++20 are supported. CLI conversion uses grammar validation plus `std::from_chars`, rejecting overflow before producing output. Descending data throws `std::invalid_argument` in the default checked API.

## 15. Input and Output Examples

From the repository root, **the target comes first**, followed by zero or more values. There is no length prefix.

```sh
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | .venv/bin/python dsa/searching/ternary-search/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/searching/ternary-search/cpp/solution.cpp -o /tmp/atlas-ternary-search
printf '%s\n' '-4 -9 -4 -4 0 2 2 8' | /tmp/atlas-ternary-search
```

Both print exactly `1` followed by a newline. Target `1` with those same values prints `-1`. Input `7` means an empty sequence searched for 7 and prints `-1`; empty stdin is an error because the target is missing. Whitespace may span lines. Replace c++17 with c++20 for the other supported standard.

```sh
.venv/bin/python -m pytest --require-cpp dsa/searching/ternary-search/tests
```

## 16. Edge Cases

Duplicates may span both pivots; equality keeps the earlier region. Lengths around powers of three, coincident pivots at tiny lengths, empty/singleton sequences, and absent keys in every region are tested. Default validation rejects descending input. A unimodal but unsorted sequence is not valid lookup input, even if another algorithm called ternary search could optimize a function over it.

CLI syntax rejects bare signs, decimal points, underscores, non-ASCII digits, and trailing junk. C++ CLI keys must fit signed `long long` (64 bits on the tested platform); Python keys can be arbitrarily large within resources. No partial result is printed on validation errors. API comparison/equality failures propagate, and input is left unchanged unless user-supplied operators themselves have side effects.

## 17. Advantages

Direct example of two-pivot boundary elimination; deterministic logarithmic unchecked cost; first-duplicate semantics; constant auxiliary space and no recursion.

## 18. Disadvantages and Limitations

Usually more comparisons and branching than Binary Search for ordinary lookup. Default validation costs O(n). Requires random access and sorted order. Does not compute extrema, handle arbitrary unimodal callbacks, or approximate a continuous optimum.

## 19. When to Use It

Use to study multi-pivot sorted lookup or to compare carefully measured implementations with matching contracts. Treat its two-pivot policy as an educational alternative, not a default performance recommendation.

## 20. When Not to Use It

Use Binary Search for routine sorted-key lookup unless measurements justify otherwise. Do not pass a unimodal function or unsorted samples to this API; optimization needs a separately specified contract and assumptions.

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

1. Why is the equal first pivot excluded from the working interval but still a possible returned boundary?
2. Why can the middle branch not execute when both pivots coincide?
3. How do comparisons per iteration affect the comparison with Binary Search?
4. What fundamentally different assumption permits ternary optimization on functions?

## 23. Practice Problems

1. Trace target 7 in the nine-item example.
2. Enumerate every target outcome for arrays of lengths 1,2,3.
3. Test duplicate plateaus crossing both pivot positions.
4. Explain why a function that is not unimodal invalidates numerical ternary optimization; do not conflate that with this lookup implementation.

## 24. References

- [NIST DADS: binary search](https://xlinux.nist.gov/dads/HTML/binarySearch.html), for the related ordered interval-elimination setting.
- [CP-Algorithms: ternary search](https://cp-algorithms.com/num_methods/ternary_search.html), describing the distinct unimodal optimization setting; it is not the API implemented here.

References describe the underlying methods; repository-specific first-match, validation, return-type, and CLI contracts are defined by this lesson and executable tests.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. See [CONTRIBUTING.md](../../../CONTRIBUTING.md) and the [MIT License](../../../LICENSE). This lesson and its implementations are part of the authorized Searching category.
