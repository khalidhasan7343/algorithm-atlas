# Power Set Generation

## 1. Algorithm Name

Power Set Generation

## 2. Overview

Enumerate every subset of input positions through a binary recursion tree. The empty subset and the full selection are both included.

## 3. Problem Statement

Return 2^n positional subsets as value lists. At each original index, explore exclusion before inclusion. Rows retain original input order. Output order is lexicographic order of 0/1 decision vectors with index 0 as the slowest-changing bit. Equal values may produce repeated rows; input is unchanged.

## 4. Why Do We Need This Algorithm?

A yes/no decision per item models optional selections directly. Unlike fixed-size combinations, the recursion covers every possible selection size in a single traversal.

## 5. Real-World Applications

- Exhaustive small feature inclusion experiments.
- Enumerate optional configuration choices for testing.
- Build candidate item selections before applying feasibility rules; this enumerator itself does no constraint filtering.

## 6. Core Intuition

Each position contributes one binary choice. Every root-to-leaf bit vector is unique, so there are exactly 2^n leaves even when payload values are equal.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Validate values and initialize empty path/output.
2. At index n, copy the current path to output.
3. Otherwise recurse to index+1 without appending (exclude).
4. Append the current value, recurse (include), then pop.
5. On return the path equals its state at entry. Inductively, both branches cover disjoint positional subsets and together cover every subset of the remaining positions.

## 9. Pseudocode

```text
visit(index):
  if index = n: append copy(path); return
  visit(index+1)           // exclude
  append values[index]
  visit(index+1)           // include
  pop path
visit(0); return output
```

## 10. Dry Run

For `[1,2]`: exclude index 0, exclude index 1 → `[]`; include index 1 → `[2]`; pop 2. Include index 0, exclude index 1 → `[1]`; include index 1 → `[1,2]`; pop 2 then 1. Result is `[[],[2],[1],[1,2]]`. This is neither size order nor integer-mask order with index 0 as the least significant bit.

## 11. Time Complexity

Time is Θ((n+1)·2^n), including row copies; for n≥1 this is Θ(n·2^n). Each position appears in half the rows, so exactly n·2^(n-1) payload entries are copied. Empty input is constant time. Payload values do not affect the traversal; no separate distributional average is assumed.

## 12. Space Complexity

Auxiliary space is O(n) for recursion and the longest path. Materialized output takes Θ((n+1)·2^n) slots, including container overhead for the empty subset. CLI parsing/serialization adds text buffers.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `power_set_generation(values) -> list[list[int]]`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '1 2\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-power-set-generation
printf '1 2\n' | /tmp/atlas-power-set-generation
```

Both commands print:

```json
[[],[2],[1],[1,2]]
```

CLI grammar: zero or more values; empty stdin is a valid empty sequence.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/power-set-generation/tests
```

## 16. Edge Cases

Empty input returns `[[]]`. One value gives `[[],[value]]`. `[7,7]` gives `[[],[7],[7],[7,7]]`; the repeated singleton rows select different positions. Negative integers are ordinary payloads. Tests compare independent bit-vector enumeration, exercise invalid tokens/types, signed extremes, repeated calls, and mutation isolation.

## 17. Advantages

The structure matches independent binary decisions and makes completeness easy to prove. Output order is deterministic and no sorting or bit-width-dependent mask arithmetic is required.

## 18. Disadvantages and Limitations

The mathematical power set of distinct values differs from these positional selections when duplicate values occur. Output is exponential: 20 inputs already produce 1,048,576 rows. Recursion depth, allocation, and output size limit practical input sizes. No streaming or deduplication mode is supplied.

## 19. When to Use It

Use it for small unrestricted subsets where every input position is an independent choice.

## 20. When Not to Use It

Avoid it when only one feasible subset, a fixed size, or merely the count 2^n is required.

## 21. Comparison With Related Algorithms

| Method | Returned selections |
| --- | --- |
| Power set | Every size, exclude-first DFS |
| [Combinations](../combinations/README.md) | Exactly k positions |
| [Subset Sum using Backtracking](../subset-sum-backtracking/README.md) | First selection meeting a target |

## 22. Interview Questions

1. Why are there 2^n leaves?
2. Why does a duplicated value produce repeated singleton rows?
3. Derive the total number of copied payload values.
4. What changes if include is explored first?

## 23. Practice Problems

1. Trace the eight subsets of three positions.
2. Group output rows by size and compare counts with C(n,k).
3. Design a lazy generator and explain how it reduces retained memory without reducing total output work.

## 24. References

- [NIST Dictionary: backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).
- [Python itertools product](https://docs.python.org/3/library/itertools.html#itertools.product), used to generate independent decision-vector expectations in tests.

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
