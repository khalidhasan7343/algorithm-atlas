# Subset Sum using Backtracking

## 1. Algorithm Name

Subset Sum using Backtracking

## 2. Overview

Find one subset of integer positions whose values sum exactly to a target, using include-before-exclude recursion. This is the catalog’s backtracking formulation, distinct from its planned dynamic-programming Subset Sum topic.

## 3. Problem Statement

Input is a finite sequence of native integers and a native integer target. Return increasing original indices for the first matching subset, or None/nullopt/null when no subset matches. Check the current sum before branching; target=0 therefore always returns []. Otherwise try including the next index before excluding it, and stop on the first matching prefix. Negative values, zeros, and duplicates are supported. Equal values at different indices are distinct selections. Input order is preserved and no caller values are changed.

## 4. Why Do We Need This Algorithm?

A witness must identify which occurrences were chosen, particularly when values repeat. Exact backtracking gives a simple correctness baseline without assuming positive weights or a small target range.

## 5. Real-World Applications

- Solve small exact selection fixtures involving credits and debits.
- Generate witnesses for balanced item-selection puzzles.
- Compare exact small-case answers against heuristic or dynamic-programming variants. Monetary production systems require their own units, precision, and validation policies.

## 6. Core Intuition

Every position is included once or skipped. Negative values can bring an oversized prefix back down, so neither total>target nor a negative remaining target is a valid general pruning rule here.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Validate native integer target and values.
2. Recurse with index 0, total 0, and an empty index path.
3. If the total matches, copy the path immediately, including the empty subset for target 0.
4. If no positions remain, fail. Otherwise append this index and recurse with its value added.
5. Pop the index even when the include branch succeeds. If it failed, try exclusion with the old total.
6. Return the copied first witness or no result. Include/exclude branches partition positional subsets; early success returns a valid witness without needing to enumerate its extensions.

## 9. Pseudocode

```text
visit(i,total):
  if total = target: answer = copy(indices); return true
  if i = n: return false
  append i
  found = visit(i+1, total+values[i])
  pop
  if found: return true
  return visit(i+1,total)
visit(0,0); return answer or null
```

## 10. Dry Run

For values `[4,-2,3]`, target 1: include 0 → total 4; include 1 → total 2; include 2 → total 5 (leaf failure). Exclude 2 → total 2 (failure). Undo 1; include 2 with 0 → total 7 (failure), then 0 alone also fails. Exclude 0; include 1 → -2; include 2 → 1, so return indices `[1,2]`. The values at those indices are -2 and 3. For `[1,0]`, target 1 returns `[0]` immediately, not `[0,1]`. This order does not promise the fewest selected positions.

## 11. Time Complexity

Let n be values. In fixed-word arithmetic the worst-case search is O(2^n), with O(1) incremental total updates and a single O(n) final path copy. C++ target 0 can succeed in O(1); Python validates all n values first, so its best case is Θ(n+1). No distributional average is claimed. Python big-integer additions/comparisons cost O(B+log(n+1)) bits for B-bit inputs/target, giving a safe O((n+2^n)·(B+log(n+1))) bit-operation upper bound.

## 12. Space Complexity

Auxiliary storage is O(n) recursion/path slots and at most n output indices. C++ totals use two fixed two-word magnitudes per recursive state. Python keeps immutable big-integer totals in frames, with a safe O(n·(B+log(n+1))) bit bound. CLI token and JSON text buffers are additional; no table indexed by target is allocated.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `subset_sum_backtracking(values, target) -> list[int] | None`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '1 4 -2 3\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-subset-sum-backtracking
printf '1 4 -2 3\n' | /tmp/atlas-subset-sum-backtracking
```

Both commands print:

```json
[1,2]
```

CLI grammar: `target value1 value2 ...`; target is required, values may be empty.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/subset-sum-backtracking/tests
```

## 16. Edge Cases

Empty values return [] for target 0 and null otherwise. Duplicate/negative/zero values are valid. Impossible sums return null; they are not invalid input. C++ prefix totals may exceed signed 64-bit range even when values and target fit it. The implementation accumulates positive and negative magnitudes separately with unsigned carry, then compares them after adding the target magnitude to the appropriate side. It never negates LLONG_MIN in signed arithmetic. Tests include multiple unsigned-word carries, cancellation after signed overflow boundaries, full-range seeded values, exhaustive small signed inputs, and independent ranking of all index subsets.

## 17. Advantages

Works with signed values and repeated occurrences, returns unambiguous indices, and uses linear working storage without a target-range table. Early witness success avoids unnecessary enumeration.

## 18. Disadvantages and Limitations

Exponential worst-case time and linear recursion depth remain practical limits. The first witness is traversal-specific, not minimum-size or unique-value canonicalization. Python accepts arbitrary-size integers; C++ requires 64-bit long long and size_t of at most 64 bits, checked by static_assert. No compiler-specific 128-bit extension or external big-integer library is used. Total magnitudes fit 128 bits because at most SIZE_MAX 64-bit values are accumulated; adding one target magnitude still fits. Extremely large recursion or allocations can exhaust resources.

## 19. When to Use It

Use it for small signed-input exact subset witnesses where a deterministic include-first answer is useful.

## 20. When Not to Use It

Avoid it for large n, all-solutions output, minimum-cardinality selection, or positive bounded targets where dynamic programming may offer a better tradeoff.

## 21. Comparison With Related Algorithms

| Approach | Assumptions and cost |
| --- | --- |
| This backtracking | Signed values, O(2^n) worst time, O(n) working slots |
| [Planned DP Subset Sum](../../dynamic-programming/subset-sum/README.md) | Different catalog formulation; target-range assumptions must be defined there |
| [Power Set Generation](../power-set-generation/README.md) | Materializes every positional subset, regardless of target |

## 22. Interview Questions

1. Why is total>target pruning wrong with negative values?
2. Why return indices instead of a set of values?
3. Explain why target 0 returns the empty subset first.
4. How does separate unsigned magnitude accumulation avoid LLONG_MIN negation and signed overflow?

## 23. Practice Problems

1. Trace `[4,-2,3]` with target 1.
2. Construct a case where the first answer uses more positions than another answer.
3. Design a separate all-witness API and specify duplicate/order semantics before implementing it.

## 24. References

- [University of Illinois CS/ECE 374 backtracking notes](https://courses.grainger.illinois.edu/CS374AL1/fa2026/lectures/backtracking.html), including a positive-input SubsetSum formulation; this lesson explicitly extends values to signed integers without positive-only pruning.
- [NIST backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
