# Strassen's Matrix Multiplication

## 1. Algorithm Name

Strassen's Matrix Multiplication

## 2. Overview

Multiply equal-size square integer matrices with Strassen’s seven recursive block products, using zero padding for odd or non-power-of-two dimensions and cropping the exact result.

## 3. Problem Statement

Input is two same-size n×n matrices of native integers, 0<=n<=128, entries in [-1000,1000]. Return their exact n×n product without modifying either input. Empty times empty returns []; nonempty/ragged/rectangular or mismatched shapes are invalid, even when a matrix is all zero. Rectangular multiplication is explicitly unsupported. Python and C++ share the size/value bounds; the CLI prints an integer JSON matrix.

## 4. Why Do We Need This Algorithm?

Ordinary block multiplication needs eight half-size products. Strassen trades additional additions/subtractions for seven products, reducing the exponent when recursively applied to sufficiently large blocks.

## 5. Real-World Applications

- Teach algebraic reduction of recursive matrix products.
- Compare operation counts and allocation overhead against conventional multiplication on small exact integer matrices.
- Build deterministic fixtures for matrix-combination experiments. This educational implementation is not a tuned BLAS replacement.

## 6. Core Intuition

Partition A and B into four quadrants. Seven carefully chosen products contain enough information to reconstruct all four result quadrants; zero padding embeds an arbitrary square dimension into the same block algebra.

## 7. Prerequisites

Understand square matrix multiplication, block notation, distributivity, induction, padded dimensions, and recurrences. [Karatsuba](../karatsuba-multiplication/README.md) uses a related product-saving identity for integers but solves a different problem.

## 8. Step-by-Step Working Process

1. Validate both entire matrices, including shape, n bound, native integer fields, and value bounds.
2. Find the smallest power of two p>=n, copy A/B into zero-filled p×p matrices.
3. For a block of size <=2, use conventional multiplication as the fixed base case.
4. Split larger blocks into quadrants and compute the seven products in the pseudocode.
5. Reconstruct four C quadrants through additions/subtractions, join them, and return.
6. Crop to n rows/columns. Expanding each M formula yields the ordinary block product, giving correctness by induction from the conventional leaf. Padding contributes only zero products, so cropping preserves every original output entry.

## 9. Pseudocode

```text
M1=(A11+A22)(B11+B22)
M2=(A21+A22)B11
M3=A11(B12-B22)
M4=A22(B21-B11)
M5=(A11+A12)B22
M6=(A21-A11)(B11+B12)
M7=(A12-A22)(B21+B22)
C11=M1+M4-M5+M7; C12=M3+M5
C21=M2+M4; C22=M1-M2+M3+M6
Each product recursively uses these formulas for width>2.
For width<=2 use conventional multiplication.
Pad to power of two before recursion; crop after joining.
```

## 10. Dry Run

Algebra illustration A=[[1,2],[3,4]], B=[[5,6],[7,8]] gives M1=65, M2=35, M3=-2, M4=8, M5=24, M6=22, M7=-30. Reconstruct C11=65+8-24-30=19, C12=-2+24=22, C21=35+8=43, C22=65-35-2+22=50. Because the implemented threshold is 2, this size uses the conventional leaf; the identity becomes the actual recursive combine for 4×4 and larger padded blocks. A 3×3 input pads to 4×4, performs seven 2×2 products, joins a 4×4 result, then discards the fourth row/column. Tests exercise these actual recursive sizes, not just the scalar illustration.

## 11. Time Complexity

For padded size p>2, T(p)=7T(p/2)+Θ(p²), with constant-width conventional leaves, so Θ(p^log₂7) ≈ Θ(p^2.807) arithmetic work. For n>=1, n<=p<2n, preserving O(n^log₂7) for this algorithm family; p=1/2 are constant leaves. Validation/copy/cropping are O(n²)/O(p²). Zero and identity matrices deliberately take the same structural recursion, so best/average/worst order agrees at a fixed size; no sparsity shortcut is used. This recurrence describes the algorithm family; the supplied API intentionally caps n for bounded practical exact arithmetic.

## 12. Space Complexity

Auxiliary memory is O(p²) with O(log p) recursion frames. Several quadrants, seven products, and combination matrices are retained per active level, so constants are substantially larger than conventional multiplication. Child dimensions shrink geometrically; the simultaneously live depth-first allocations sum to O(p²). Output stores n² integers, and padding can approach four times the original entry count per matrix. CLI tokens are additional.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `strassen_multiply(a,b) -> list[list[int]]`. Integer fields require native int; bools, floats, strings, None, and int subclasses are invalid integer fields (TypeError). Domain/shape/range errors raise ValueError. Sequence inputs must be finite and indexable. Inputs are read only; outputs own their storage. The main guard prevents import-time demonstrations. No third-party runtime dependency is needed.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). API in namespace `algorithm_atlas`: `strassen_multiply(const Matrix&,const Matrix&) -> Matrix`. Define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. Supported standards are C++17 and C++20; only standard headers are used. Invalid input raises std::invalid_argument. Resource failures remain errors. Exact numeric representation and bounds are part of the contract above; there is no silent overflow or approximate-success fallback.

## 15. Input and Output Examples

Run from this algorithm directory:

```sh
printf '2 1 2 3 4 5 6 7 8\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-strassen-matrix-multiplication
printf '2 1 2 3 4 5 6 7 8\n' | /tmp/atlas-strassen-matrix-multiplication
```

Both commands print:

```json
[[19,22],[43,50]]
```

CLI grammar: n followed by n² row-major A entries and then n² row-major B entries; n in 0..128. Whitespace-separated ASCII signed decimal tokens only.
Output is one compact JSON value and newline. Invalid input exits nonzero,
writes stderr, and produces no result. Decimal strings in JSON preserve exact
integers without relying on a consumer's floating-point numeric precision.

From the repository root, run both language suites:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/divide-and-conquer/strassen-matrix-multiplication/tests
```


## 16. Edge Cases

Empty and 1×1, zero, identity, negative values, odd dimensions, powers of two, n=128, and input magnitude endpoints are tested. Independent conventional multiplication checks seeded random matrices. Both left/right identity and zero products are included. Invalid rectangular/ragged/mismatched shapes, n=129, ±1001 values, invalid native types, and malformed CLI counts are rejected; input preservation and fresh output rows are tested.

## 17. Advantages

Directly demonstrates a subcubic arithmetic recurrence and handles arbitrary supported square dimensions through explicit padding. Exact integer contracts avoid floating-point cancellation ambiguity.

## 18. Disadvantages and Limitations

Square matrices only, n<=128, entries in [-1000,1000], threshold fixed at 2. These limits are intentional practical/numeric constraints rather than claims of general matrix support. Floating-point inputs are rejected; floating Strassen variants can amplify rounding/cancellation error. Here all arithmetic is exact: a conservative bound on recursive/recombination intermediates is p^4·1000²<=128^4·1000²=268435456000000, far below signed 64-bit maximum. This bound includes expanded operand sums and up to four product terms per combine; validation precedes arithmetic. The ordinary fallback is confined to blocks <=2, so it cannot silently replace the main recursion. Allocations and small threshold make this slower than tuned conventional kernels for many supported sizes.

## 19. When to Use It

Use it for studying seven-product block identities, exact padded multiplication, and operation-count experiments within the shared bounds.

## 20. When Not to Use It

Avoid it for rectangular, floating/complex, large, sparse, or performance-critical production matrices without a separately designed numeric and memory policy.

## 21. Comparison With Related Algorithms

| Method | Arithmetic work | Tradeoff |
| --- | --- | --- |
| Conventional | Θ(n³) | Lower overhead, straightforward numeric behavior |
| This Strassen | O(p^log₂7) | Padding and many temporary matrices |
| [Karatsuba](../karatsuba-multiplication/README.md) | O(d^log₂3) digits | Product-saving identity for scalar integers |

## 22. Interview Questions

1. Expand M1+M4-M5+M7 and cancel terms.
2. Why does zero padding preserve the top-left product?
3. Why must the base threshold remain fixed in the recurrence?
4. How do numerical stability and exact overflow bounds differ?

## 23. Practice Problems

1. Verify all seven scalar products in the example.
2. Trace the block dimensions for n=5 padded to 8.
3. Measure allocation and arithmetic counts against conventional multiplication without changing the documented threshold.

## 24. References

- [University of Hawaii ICS311: divide/conquer, maximum subarray, and recurrences](https://courses.ics.hawaii.edu/ics311_f26/Notes/Topic-07.html).
- [Carnegie Mellon: deterministic closest-pair lecture and strip analysis](https://www.cs.cmu.edu/~15451-f18/lectures/lec23-closest-pair.pdf).
- [Carnegie Mellon algorithm notes](https://www.cs.cmu.edu/~avrim/451f11/lectures/lects1-10.pdf), including Karatsuba and Strassen algebra. Code and contract-specific proofs in this lesson are original educational implementations.

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md), and [development standards](../../../docs/development.md). This canonical A4 topic does not authorize implementing any other category. Passing tests does not imply owner review or phase approval.
