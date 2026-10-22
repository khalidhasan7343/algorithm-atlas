# Permutations

## 1. Algorithm Name

Permutations

## 2. Overview

Enumerate every ordering of input positions using a used-position array and a recursive path. This is enumeration, not random shuffling or sorting.

## 3. Problem Statement

Given n integer values, return a list of all n! positional permutations as value lists. Choices follow original indices in ascending order at every depth. Equal values at different positions are distinct choices and deliberately produce repeated value rows. The caller’s sequence is untouched; empty input returns `[[]]`.

## 4. Why Do We Need This Algorithm?

Trying complete orderings gives a simple exhaustive baseline when every item must be used exactly once. A partial prefix lets a later application reject invalid arrangements early, although this implementation intentionally enumerates all arrangements.

## 5. Real-World Applications

- Explore small job-order candidates before evaluating a scheduling cost.
- Generate exhaustive test inputs for order-sensitive interfaces.
- Enumerate short route orderings as a baseline for optimization; distance evaluation and pruning are outside this enumerator.

## 6. Core Intuition

Choose an unused position, explore every completion, then undo that choice. The used array distinguishes positions even when their values compare equal.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Validate all values and create empty output/path and n unused flags.
2. If the path has n values, append a copy and return.
3. Scan original indices from 0 through n-1; skip used indices.
4. Mark one index, append its value, recurse, pop the value, and clear the flag.
5. Return all copied rows. The invariant is that the path contains exactly the marked positions once each. Every full index ordering has a unique root-to-leaf choice sequence, proving completeness and positional uniqueness.

## 9. Pseudocode

```text
visit():
  if length(path) = n: append copy(path) to output; return
  for i = 0 .. n-1:
    if not used[i]:
      used[i] = true; append values[i] to path
      visit()
      pop path; used[i] = false
visit(); return output
```

## 10. Dry Run

For `[2,1,1]`, label positions A,B,C. Start A: AB→ABC emits `[2,1,1]`; undo C,B, then AC→ACB emits the same values from different positions. Start B: BA→BAC emits `[1,2,1]`, then BC→BCA emits `[1,1,2]`. Start C emits those last two rows again. There are six rows, not three unique-value arrangements. Each return clears its used flag, so the next sibling can reuse that position.

## 11. Time Complexity

Let n be the number of positions. For n≥1, time is Θ(n·n!), including copying each complete row and scanning candidates. Empty input takes Θ(1). Best and worst cases depend only on n, not values; no distributional average is assumed. Python additionally validates n values. JSON serialization has the same number of values but costs extra digits for large integers.

## 12. Space Complexity

Auxiliary space is O(n) for used flags, path, and recursion frames, excluding output. Retained output is Θ((n+1)·n!) container/value slots, including the one empty row for n=0. CLI token/JSON buffers add input/output text storage.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `permutations(values) -> list[list[int]]`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '1 2\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-permutations
printf '1 2\n' | /tmp/atlas-permutations
```

Both commands print:

```json
[[1,2],[2,1]]
```

CLI grammar: zero or more values; empty stdin is a valid empty sequence.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/permutations/tests
```

## 16. Edge Cases

Empty returns `[[]]`; one value returns one row. Negative/extreme values are payloads, not indices. `[5,5]` returns `[[5,5],[5,5]]`. All rows are independent copies: modifying one result cannot change another row or the input. Tests compare itertools’ positional oracle, cover duplicate-heavy exhaustive cases, repeat calls, and execute both CLIs.

## 17. Advantages

The traversal is deterministic, direct, and easy to extend with prefix constraints. It needs only linear working storage apart from its explicitly materialized result.

## 18. Disadvantages and Limitations

Factorial output becomes impractical quickly: 10 positions already mean 3,628,800 rows. Duplicate values do not reduce work. Deep recursion can hit Python’s recursion limit or exhaust the C++ stack; allocation can fail. No arbitrary size cap or lazy iterator is provided.

## 19. When to Use It

Use it for exhaustive small positional arrangements where order matters and all elements must appear.

## 20. When Not to Use It

Avoid it for a single random ordering, large optimization instances, or unique multiset permutations without repeated rows.

## 21. Comparison With Related Algorithms

| Method | Choice structure | Output |
| --- | --- | --- |
| Permutations | Ordered unused positions | n! rows |
| [Combinations](../combinations/README.md) | Increasing selected positions | C(n,k) rows |
| [Power Set Generation](../power-set-generation/README.md) | Include/exclude each position | 2^n rows |

## 22. Interview Questions

1. Why must the used flag be cleared after returning?
2. Why do equal values still produce n! rows?
3. Why does copying a leaf path matter?
4. How would you generate only distinct multiset permutations without changing this API silently?

## 23. Practice Problems

1. Trace all index choices for three positions.
2. Add a separate streaming variant and compare peak memory.
3. Build a distinct-value variant using a frequency map and prove its output count. These exercises are not additional implemented catalog topics.

## 24. References

- [Python itertools permutations contract](https://docs.python.org/3/library/itertools.html#itertools.permutations), a positional-output reference used by tests.
- [NIST Dictionary: backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
