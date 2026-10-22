# Combinations

## 1. Algorithm Name

Combinations

## 2. Overview

Select exactly k positions while preserving their input order. The recursive start index prevents selecting a position twice or emitting different orders of the same positional selection.

## 3. Problem Statement

Return all k-element positional combinations, in lexicographic order of increasing original-index tuples. Equal values at different indices remain distinct choices and can produce equal value rows. k must be a native nonnegative integer. k=0 returns `[[]]`, k>n returns `[]`. Input is never sorted or mutated.

## 4. Why Do We Need This Algorithm?

Many tasks need fixed-size selections without caring about the order in which members were chosen. Increasing indices remove the k! redundant permutations of each selection.

## 5. Real-World Applications

- Enumerate small fixed-size committees from individually identified candidates.
- Try feature subsets of a fixed size for small experiments.
- Generate pairwise or triple-wise test groupings. Identical payload values do not imply identical participants.

## 6. Core Intuition

After selecting index i, all future indices must be greater than i. Stop the loop early when too few positions would remain to finish k selections.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Validate k and all values; return no rows if k>n.
2. Recurse with start=0 and an empty path.
3. Copy a path when it reaches k elements.
4. Otherwise choose i from start through n-(k-path_length).
5. Append values[i], recurse from i+1, then pop. Every path has strictly increasing indices; every valid k-index tuple begins with one of these choices and leaves enough positions for its suffix.

## 9. Pseudocode

```text
visit(start):
  if length(path) = k: append copy(path); return
  last = n - (k - length(path))
  for i = start .. last:
    append values[i]
    visit(i+1)
    pop path
if k > n: return []
visit(0); return output
```

## 10. Dry Run

For values `[3,1,3]`, k=2, start=0 permits i=0 or 1. Choose index 0 (value 3): choose 1 emits `[3,1]`, undo, choose 2 emits `[3,3]`. Undo index 0. Choose index 1 (value 1), then 2 emits `[1,3]`. Output order follows index tuples (0,1),(0,2),(1,2), not sorted values. With k=0, the initial empty path is already a complete selection.

## 11. Time Complexity

For 0≤k≤n, the generation core costs Θ(1+k·C(n,k)), including copying all rows. Python’s upfront value validation adds Θ(n), even when k=0 or k>n; the statically typed C++ API has no element-type scan. C++ k>n returns in O(1). Counts depend on n,k rather than payload values; an input-distribution average is not assumed. CLI parsing still scans all tokens.

## 12. Space Complexity

Auxiliary memory is O(k+1) for the path and recursion stack for valid k≤n. Output uses Θ((k+1)·C(n,k)) slots including row overhead. k>n needs constant API working memory beyond Python’s validation iterator. CLI text buffers are additional.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `combinations(values, k) -> list[list[int]]`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '2 3 1 3\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-combinations
printf '2 3 1 3\n' | /tmp/atlas-combinations
```

Both commands print:

```json
[[3,1],[3,3],[1,3]]
```

CLI grammar: `k value1 value2 ...`; k is required, values may be empty.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/combinations/tests
```

## 16. Edge Cases

Empty values with k=0 return `[[]]`; empty with k>0 return `[]`. Negative k is invalid, not an empty answer. Large k>n returns immediately after Python value validation. Repeated values intentionally preserve positional multiplicity. Tests sweep all k from 0 through n+1, reject bool/subclass/type errors in Python, test C++ negative k, signed payload extremes, and verify repeated calls and input preservation.

## 17. Advantages

Avoids permutation redundancy and prunes incomplete suffixes early. Output order is predictable without sorting the caller’s data.

## 18. Disadvantages and Limitations

C(n,k) can be enormous near k=n/2. Results are eagerly stored; no count-only, streaming, or deduplicated-value mode exists. Deep k can exhaust recursion resources even when output count is small. C++ k and payload values use long long.

## 19. When to Use It

Use it when exactly k distinct positions are needed and the selected positions’ order should follow the input.

## 20. When Not to Use It

Avoid it when the selection size is unrestricted, repeated use of one position is allowed, or only the binomial count is needed.

## 21. Comparison With Related Algorithms

| Method | Size restriction | Ordering |
| --- | --- | --- |
| Combinations | Exactly k | Increasing indices |
| [Permutations](../permutations/README.md) | All n | Every ordering |
| [Power Set Generation](../power-set-generation/README.md) | Any size | Binary-decision DFS |

## 22. Interview Questions

1. Why does recursion start at i+1?
2. Derive the last candidate n-(k-path_length).
3. Explain the one empty combination.
4. How would selection with replacement change the invariant?

## 23. Practice Problems

1. Trace n=4,k=2 by index tuples.
2. Count outputs and verify Pascal’s identity.
3. Design an iterative or lazy variant and preserve the documented ordering.

## 24. References

- [Python itertools combinations contract](https://docs.python.org/3/library/itertools.html#itertools.combinations), including positional identity.
- [NIST Dictionary: backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
