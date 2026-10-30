# Singular Value Decomposition (reduced one-sided Jacobi)

## 1. Algorithm Name

Singular Value Decomposition (reduced one-sided Jacobi)

## 2. Overview

Factor an uncentered rectangular matrix into orthonormal left/right directions and nonnegative strengths; optionally keep its first k directions.

## 3. Problem Statement

Given real X of shape n by p, compute U(n,r), s(r), V(r,p), r=min(n,p), with X≈U diag(s)V; retain k<=r components for projection.

## 4. Why Do We Need This Algorithm?

A low-rank factorization compresses correlated columns and exposes numerical rank without forming the Gram matrix, which squares the condition number.

## 5. Real-World Applications

Low-rank compression of small feature tables, rank diagnostics, and the decomposition foundation used by the canonical PCA lesson.

## 6. Core Intuition

Rotate pairs of columns until their inner products vanish. The resulting column lengths are singular values, and the accumulated rotations give right singular vectors.

B=X/scale, V=I. For pair i,j, alpha=<bi,bi>, beta=<bj,bj>, gamma=<bi,bj>. Set theta=atan2(2gamma,beta-alpha)/2; update bi=c*bi-s*bj, bj=s*bi+c*bj and rotate V identically. Thus B=(X/scale)V throughout. Orthogonal columns normalized give U. Wide inputs use the transpose and exchange factors.

## 7. Prerequisites

Vectors, inner products, matrix multiplication, derivatives where optimization is used, and floating-point tolerances. Read the [B5 contracts](../../../../docs/dimensionality-reduction-conventions.md) and linked comparisons below.

## 8. Step-by-Step Working Process

Sweep every column pair until |gamma|<=tol*sqrt(alpha)*sqrt(beta). Sort column norms descending, normalize resolved columns, and complete zero-singular-value U columns with twice-reorthogonalized coordinate vectors. Components below eps*max(n,p)*smax are treated as numerical nulls. Jointly flip U/V signs for a largest-entry-positive V convention. Exhausting max_sweeps raises ConvergenceError; no partial factorization is installed.

## 9. Pseudocode

```text
scale X; transpose if wide; B=X/scale; V=I
repeat bounded sweeps: orthogonalize each column pair by Jacobi rotation
if no rotations: stop; else exhausted: error
sort column norms; normalize columns; complete null basis
undo transpose; orient signs; retain first k
```

## 10. Dry Run

X=diag(3,1,2), k=2. All initial cross products are zero, so one sweep suffices. Sorted s=(3,2,1); V rows are e1,e3,e2. Transform gives rows (3,0),(0,0),(0,2); rank-2 reconstruction is diag(3,0,2), squared Frobenius error 1.

## 11. Time Complexity

Let r=min(n,p), m=max(n,p), S<=max_sweeps. Pair rotations cost O(m) and there are O(r²) per sweep: O(S*m*r²), plus O(m*r²) null completion. Already orthogonal data needs one sweep; no average-case sweep count is promised. Transform O(q*p*k).

## 12. Space Complexity

O(n*p+r²) working storage plus reduced factors; stored model O(n*k+k*p+r). No recursion. Input copies and full intermediate factors are bounded.

## 13. Python Implementation

[SVD source](python/solution.py) implements the stated mechanism using NumPy primitives and shared bounded contracts; no reference estimator is imported. [Executable example](python/example.py); [tests](tests/test_python.py). Fit copies caller data and installs state only after successful validation/computation. Queries validate fitted feature dimensions.

Validation uses independent NumPy singular values/projectors and discarded-energy identities; diagonal, wide/tall, zero, repeated-value and random rank-deficient matrices verify both factor orthogonalities. Uniform scales1e-200/1e12 and explicit sweep exhaustion test stability/failure.

## 14. C++ Implementation

C++ is optional for this authorized Python/NumPy scope and is absent; no placeholder source or test is provided. DSA still requires actual Python/C++17/C++20 checks.

## 15. Input and Output Examples

From repository root, with requirements-ml-test.txt installed:

```sh
python machine-learning/unsupervised-learning/dimensionality-reduction/singular-value-decomposition/python/example.py
```

The example uses the dry-run input and prints a JSON embedding. The solution also accepts a JSON object with X, optional parameters and y for supervised LDA on stdin. Actual example/CLI outputs are retained in the Phase 17 evidence. Numeric coordinates are sign/rotation dependent where explained; objectives and subspaces are the comparison contract.

## 16. Edge Cases

Zero and repeated singular values are supported. Repeated vectors are not unique; compare projectors, not arbitrary individual vectors. The numerical-rank threshold discards unresolved directions, so reconstruction is tolerance-based. Tiny uniformly scaled inputs are normalized before rotations; values already rounded away cannot be recovered.

Reject nonfinite/nonreal arrays, invalid dimensions and unsupported resource limits before fitting. Invalid refits preserve previous fitted arrays. Random methods use a local generator and never modify global RNG state.

## 17. Advantages

Explicit rotations teach the mechanism and avoid Gram-matrix conditioning; both tall and wide reduced factors have checked orthogonality.

## 18. Disadvantages and Limitations

Dense small matrices, p<=32, n<=512, |X|<=1e12; scalar Jacobi is slower than production LAPACK. This is reduced SVD, not full n by n U or a sparse randomized solver. Tol is 1e-15..1e-6; max_sweeps 1..1000. Truncation is by component count, not inferred semantic rank.

## 19. When to Use It

Use when a small, inspectable reduced factorization or optimal rank-k approximation is the lesson.

## 20. When Not to Use It

Use a production sparse/blocked solver for large matrices; use PCA when training-data centering is intended.

## 21. Comparison With Related Algorithms

SVD factors uncentered X; PCA first centers X and interprets s²/(n-1) as sample variances. Eigenvectors of X.T X give related directions but lose relative accuracy by squaring conditioning.

## 22. Interview Questions

Why rotate V with B? Because B=X V must remain true. Why can a null U column be chosen arbitrarily? Its singular coefficient is zero. Why compare subspaces for a repeated value? Any orthonormal rotation inside that eigenspace is valid.

## 23. Practice Problems

Prove each two-column rotation preserves B=X V. Derive the Frobenius error sum of discarded s². Extend tests with a repeated nonzero singular block and verify its projector.

## 24. References

[LAPACK Jacobi SVD documentation](https://netlib.org/lapack/explore-html/d9/deb/group__gesvj_ga7aec05d2a1523bbeee77ece21b12187c.html); [NumPy SVD reference oracle](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). This lesson is part of Phase 17 B5; owner review is pending.
