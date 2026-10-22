# N-Queens

## 1. Algorithm Name

N-Queens

## 2. Overview

Enumerate all placements of n nonattacking queens on an n×n board by assigning one column per row. Reflections and rotations remain separate placements.

## 3. Problem Statement

Input is a native nonnegative integer n. Output rows are column-index vectors: placement[r] gives the zero-based column of row r’s queen. Return every solution in lexicographic order, trying columns 0..n-1 in each row. n=0 has one empty placement `[[]]`; n=1 gives `[[0]]`; n=2 and n=3 give `[]`.

## 4. Why Do We Need This Algorithm?

The unconstrained board has many placements. Assigning one row at a time removes row conflicts by construction, while column and diagonal occupancy reject impossible prefixes before filling the board.

## 5. Real-World Applications

- Teach constraint satisfaction with local conflict checks.
- Generate small nonattacking placement puzzles and exhaustive regression fixtures.
- Study how pruning changes a combinatorial search tree; this code is an educational baseline, not an industrial placement optimizer.

## 6. Core Intuition

Rows are implicit in recursion depth. Two queens share a descending diagonal when row+column agrees, or an ascending diagonal when row+(n-1-column) agrees. Three occupancy arrays make each candidate check constant time.

## 7. Prerequisites

Understand recursion, a base case, depth-first traversal, and the difference between copying a result and retaining a mutable working path. Read the [development guide](../../../docs/development.md) for the shared API and test conventions.

## 8. Step-by-Step Working Process

1. Reject negative/noninteger n, then allocate local column and diagonal flags.
2. At row n, copy the column path to output.
3. At each earlier row, try columns in ascending order.
4. Skip any occupied column or diagonal. Otherwise mark all three flags and append the column.
5. Recurse to the next row, then pop and clear exactly the flags just set. The prefix invariant guarantees nonattacking queens; every valid complete placement has exactly one sequence of row choices, proving no omission or positional duplicate.

## 9. Pseudocode

```text
place(row):
  if row = n: output copy(path); return
  for col = 0 .. n-1:
    d = row+col; a = row+(n-1-col)
    if column[col] or diagonal[d] or anti[a]: continue
    mark col,d,a; append col
    place(row+1)
    pop; unmark col,d,a
place(0); return output
```

## 10. Dry Run

For n=4, row0=0 eventually fails: row1=2 leaves no legal row2; row1=3 followed by row2=1 cannot finish row3. Undo that entire branch. With row0=1, row1=3, row2=0, row3=2 is valid, so emit `[1,3,0,2]`. Restore all flags, then the row0=2 branch emits `[2,0,3,1]`. Row0=3 has no completion. For n=0, the first call immediately copies the empty path without accessing diagonal arrays.

## 11. Time Complexity

Let n be board size and S the number of returned placements. A safe upper bound is O(n·n! + n·S + 1): each partial column permutation scans n candidates, and each result copies n indices. Diagonal pruning improves actual work but does not create a polynomial bound. Best/worst observed costs depend on n; no probabilistic average is asserted. n=0 is Θ(1), initialization Θ(n).

## 12. Space Complexity

Auxiliary storage is O(n): n column flags, two arrays of 2n-1 diagonal flags, a length-n path, and O(n) recursion frames. Output uses Θ((n+1)·S) slots including row headers. CLI text and serialization are additional.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `n_queens(n) -> list[list[int]]`. Functions have no import-time demonstrations and keep working state local to each call. Integer fields require native Python integers; bools, floats, strings, and int subclasses in those fields raise TypeError. Boolean flags follow their separately documented contract. Value/domain errors raise ValueError. Sequence arguments must be finite and indexable, not one-shot iterators. Python integers have arbitrary precision.

The CLI accepts whitespace-separated ASCII signed decimal integers and prints one compact JSON value plus a newline. It rejects malformed tokens before running the algorithm. No third-party runtime dependencies are required.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). The same function lives in namespace `algorithm_atlas`; define `ALGORITHM_ATLAS_NO_MAIN` before including the file in a driver. C++17 and C++20 are supported. Integer values and CLI tokens use signed `long long`; out-of-range tokens are rejected. Invalid domain/shape inputs throw `std::invalid_argument`. Inputs are const references and returned containers own their data. Indices use `std::size_t`, with bounds checked before subtraction or conversion. The standalone CLI reports invalid input on stderr, exits nonzero, and emits no result. Resource exhaustion is an error, never an impossible-problem answer.

## 15. Input and Output Examples

Run from this algorithm folder:

```sh
printf '4\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-n-queens
printf '4\n' | /tmp/atlas-n-queens
```

Both commands print:

```json
[[1,3,0,2],[2,0,3,1]]
```

CLI grammar: exactly one nonnegative board size n.

Run both language test suites from the repository root:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/recursion-and-backtracking/n-queens/tests
```

## 16. Edge Cases

Zero, one, and unsatisfiable sizes 2/3 have distinct documented outputs. Negative n is invalid. Python rejects bool/int subclasses. C++ checks the safe index range before doubling n for diagonal storage; impossible allocations remain resource errors. Tests verify counts 1,1,0,0,2,10,4,40,92 for n=0..8 and compare every placement and its order against independent permutation filtering. Returned rows own their data.

## 17. Advantages

Constant-time conflict checks avoid repeatedly scanning the partial board. Row vectors are compact and lexicographic ordering is reproducible.

## 18. Disadvantages and Limitations

Enumeration remains combinatorial, stores all solutions, and does not identify symmetry-equivalent boards. Large n can exhaust memory, recursion depth, or the C++ stack. No constructive single-solution, bit-mask acceleration, parallelism, or streaming API is included.

## 19. When to Use It

Use it to examine every placement on small boards or to study exact constraint propagation through occupancy arrays.

## 20. When Not to Use It

Avoid it when only one large-board placement, a symmetry-reduced count, or interactive resource guarantees are needed.

## 21. Comparison With Related Algorithms

| Problem | Constraint state | Result policy |
| --- | --- | --- |
| N-Queens | Columns and two diagonals | All placements |
| [Sudoku Solver](../sudoku-solver/README.md) | Digits in rows, columns, boxes | First completion |
| [Permutations](../permutations/README.md) | Used positions only | Every ordering |

## 22. Interview Questions

1. Why is no row occupancy array necessary?
2. Prove both diagonal formulas.
3. Why must a successful leaf still unwind and restore state?
4. How does symmetry reduction change the output contract?

## 23. Practice Problems

1. Draw the two n=4 results.
2. Instrument rejected candidates for n=5..8.
3. Design a separate count-only variant and discuss output-space savings.

## 24. References

- [Cornell CS4700 lecture on constraint satisfaction, including N-Queens](https://www.cs.cornell.edu/courses/cs4700/2020sp/Lectures/Lecture13.pdf).
- [NIST backtracking](https://xlinux.nist.gov/dads/HTML/backtrack.html).

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE) and [contribution guidelines](../../../CONTRIBUTING.md). This lesson belongs to the catalog’s Recursion and Backtracking category. Implementation/testing completion does not imply owner review or phase approval.
