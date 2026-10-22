# Sudoku Solver

## 1. Algorithm Name

Sudoku Solver

## 2. Overview

Complete a standard 9×9 Sudoku through row-major recursive assignment, using digit occupancy masks to reject row, column, and 3×3-box conflicts.

## 3. Problem Statement

Input is exactly nine rows of nine native integers, 0 for blank and 1..9 for givens. Contradictory givens or invalid shape/range are errors. A consistent but unsatisfiable board returns None (C++ nullopt; CLI null). Otherwise return the lexicographically first row-major completed grid, choosing digits in ascending order. The caller’s board is unchanged; output rows are independent copies. This solver returns one solution and does not certify uniqueness.

## 4. Why Do We Need This Algorithm?

Local validity alone cannot guarantee that a partially filled board has a completion. Backtracking can retract an apparently valid digit when later constraints prove it impossible.

## 5. Real-World Applications

- Solve or validate completion feasibility for standard Sudoku puzzle tools.
- Generate one completion for a partially specified test fixture.
- Demonstrate constraint checking and reversible assignments. A puzzle generator needing uniqueness must add a separate solution-counting procedure.

## 6. Core Intuition

Maintain used-digit masks for each unit. Select the next blank in fixed row-major order; try all available digits. Copy a full completion, then undo assignments while propagating success.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Validate shape, cell types/ranges, and every given against row/column/box masks. Record blanks in row-major order.
2. Work on a private board copy. At the next blank, try digits 1..9.
3. Reject a digit already present in any of its three units.
4. Assign the digit and update masks; recurse.
5. Restore the blank and remove all three mask bits even on success, then return the success flag.
6. At the leaf, copy the solution. Each prefix respects all constraints; exhaustive ascending choices ensure completeness and the lexicographically first valid completion.

## 9. Pseudocode

```text
validate givens; build masks and ordered blanks
visit(i):
  if i = number_of_blanks: answer = deep_copy(work); return true
  (r,c) = blanks[i]; b = 3*(r div 3)+(c div 3)
  for digit = 1 .. 9:
    if digit absent from row[r], column[c], box[b]:
      assign digit; mark three masks
      found = visit(i+1)
      clear cell; undo three masks
      if found: return true
  return false
visit(0); return answer or null
```

## 10. Dry Run

Use the valid completed grid shown in the example, replacing its first two cells by 0. At (0,0), the row lacks {3,5}; column 0 and box 0 permit only 5, so assign 5. At (0,1), only 3 remains, so assign 3. Reaching the last blank copies the complete grid. Unwind: clear (0,1) and its mask bits, then (0,0), while retaining the copied answer. For a contradictory initial pair in one row, validation rejects before any search; a later dead end instead exhausts candidates and returns no solution.

## 11. Time Complexity

With E blanks (0≤E≤81), a safe search upper bound is O(9^E), with constant-time mask checks and fixed-size 81-cell validation/copy costs. A solved board costs Θ(81); failed branches or early success change actual work. No input-distribution average is claimed. The bound describes this fixed 9×9 solver, not a generalized n×n implementation.

## 12. Space Complexity

Working storage is O(81+E): private board, 27 fixed masks, blank list, and recursion frames. The returned solution stores 81 cells; only one completion is retained. For the fixed board these are bounded constants, but E explains recursion depth. CLI buffers add text storage.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `solve_sudoku(board) -> list[list[int]] | None`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '0 0 4 6 7 8 9 1 2 6 7 2 1 9 5 3 4 8 1 9 8 3 4 2 5 6 7 8 5 9 7 6 1 4 2 3 4 2 6 8 5 3 7 9 1 7 1 3 9 2 4 8 5 6 9 6 1 5 3 7 2 8 4 2 8 7 4 1 9 6 3 5 3 4 5 2 8 6 1 7 9\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-sudoku-solver
printf '0 0 4 6 7 8 9 1 2 6 7 2 1 9 5 3 4 8 1 9 8 3 4 2 5 6 7 8 5 9 7 6 1 4 2 3 4 2 6 8 5 3 7 9 1 7 1 3 9 2 4 8 5 6 9 6 1 5 3 7 2 8 4 2 8 7 4 1 9 6 3 5 3 4 5 2 8 6 1 7 9\n' | /tmp/atlas-sudoku-solver
```

Both commands print:

```json
[[5,3,4,6,7,8,9,1,2],[6,7,2,1,9,5,3,4,8],[1,9,8,3,4,2,5,6,7],[8,5,9,7,6,1,4,2,3],[4,2,6,8,5,3,7,9,1],[7,1,3,9,2,4,8,5,6],[9,6,1,5,3,7,2,8,4],[2,8,7,4,1,9,6,3,5],[3,4,5,2,8,6,1,7,9]]
```

CLI grammar: exactly 81 cells in row-major order, 0 for blank.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/sudoku-solver/tests
```

## 16. Edge Cases

An empty outer sequence or ragged board is invalid. An all-zero 9×9 board is valid and has multiple completions; deterministic traversal chooses one. Repeated nonzero values in a row, column, or box are invalid; repeated zeros are blanks. Tests isolate all three contradiction types, reject out-of-range cells, check a consistent impossible board, compare a classic puzzle and seeded near-complete boards with an independent MRV/set solver, verify givens/unit validity, and exercise all-zero repeated calls in both languages.

## 17. Advantages

Mask checks are constant time; a private board protects caller data. Fixed row-major traversal gives a clear deterministic first-solution contract.

## 18. Disadvantages and Limitations

Hard puzzles can require extensive exponential search because this variant does not use minimum-remaining-values ordering or constraint propagation beyond used-digit masks. It supports standard 9×9 Sudoku only, returns one solution, and offers no uniqueness certificate, deadline, or cancellation API.

## 19. When to Use It

Use it for small standard Sudoku completion and learning reversible constraint state.

## 20. When Not to Use It

Avoid it for generalized puzzle sizes, uniqueness proofs, or hard-instance latency guarantees. A dedicated CSP/exact-cover solver may be a better fit.

## 21. Comparison With Related Algorithms

| Variant | Candidate policy | Tradeoff |
| --- | --- | --- |
| This solver | Row-major, ascending digits | Predictable first solution |
| MRV search | Most constrained blank | Often fewer branches; different first-solution order |
| [N-Queens](../n-queens/README.md) | Next row, columns | Enumerates all placements |

## 22. Interview Questions

1. Why must initial givens be validated before the solved-board base case?
2. Why is a consistent board not necessarily solvable?
3. Why can mask bits safely be cleared after one trial?
4. How would stopping after two solutions establish nonuniqueness?

## 23. Practice Problems

1. Trace a board with two missing cells.
2. Compare node counts against MRV without changing this API.
3. Design a separate uniqueness checker with an explicit two-solution cutoff.

## 24. References

- [Peter Norvig, Solving Every Sudoku Puzzle](https://www.norvig.com/sudoku.html), for unit constraints and a more advanced propagation/search approach. This lesson uses a simpler row-major mask variant.
- [NIST backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
