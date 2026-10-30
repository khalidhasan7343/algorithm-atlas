# Principal Component Analysis (PCA)

## 1. Algorithm Name

Principal Component Analysis (PCA)

## 2. Overview

Learn orthogonal directions of maximum training-data variance and project centered observations into them.

## 3. Problem Statement

Given X(n,p), n>=2, and 1<=k<=min(n,p), return centered scores Z=(X-mean) V_k.T, directions, singular values and sample explained variances.

## 4. Why Do We Need This Algorithm?

Correlated measured features can be summarized with fewer linear coordinates while minimizing squared reconstruction error over rank-k centered projections.

## 5. Real-World Applications

Exploratory feature compression, visualization of small numeric tables, and denoising under a low-rank signal assumption; scale choices determine what variance means.

## 6. Core Intuition

Find the direction with largest centered squared length, then the next orthogonal direction. SVD supplies all such directions without building covariance explicitly.

A=X-mean=U diag(s)V. Covariance C=A.T A/(n-1)=V.T diag(s²/(n-1))V. The Rayleigh quotient v.T C v is maximized by the leading eigenvector for ||v||=1; successive orthogonal restrictions give the rest. Reconstruction is Z V_k+mean and residual Frobenius²=sum discarded s². Ratios use all r scaled singular squares, with an all-zero variance table defined to have zero ratios.

## 7. Prerequisites

Vectors, inner products, matrix multiplication, derivatives where optimization is used, and floating-point tolerances. Read the [B5 contracts](../../../../docs/dimensionality-reduction-conventions.md) and linked comparisons below.

## 8. Step-by-Step Working Process

Compute an anchor-centered training mean, subtract it, call the single canonical Jacobi SVD, retain k rows of V and singular values, and compute variance/ratios. Queries use the retained mean. There is no automatic standardization, whitening, label use or test-set fitting.

## 9. Pseudocode

```text
mean = training feature mean
A = X-mean
U,s,V = canonical reduced Jacobi SVD(A)
components = V[:k]; variance=s[:k]²/(n-1)
ratio = scaled_s[:k]² / sum(scaled_s²), or zero
transform query: (query-mean) components.T
```

## 10. Dry Run

X=[(8,20),(10,21),(12,20),(10,19)], k=1. Mean=(10,20); sample covariance=diag(8/3,2/3). First direction is (1,0); scores=(-2,0,2,0); explained ratio=0.8. Reconstruction discards second-coordinate deviations, squared error=2.

## 11. Time Complexity

With r=min(n,p), m=max(n,p) and S Jacobi sweeps, fit O(S*m*r²) through canonical SVD; centering O(n*p). Query projection and reconstruction O(q*p*k).

## 12. Space Complexity

O(n*p+r²) fit auxiliary storage; stored mean/directions/variance O(p*k+p+k). No recursion or covariance inversion.

## 13. Python Implementation

[PCA source](python/solution.py) implements the stated mechanism using NumPy primitives and shared bounded contracts; no reference estimator is imported. [Executable example](python/example.py); [tests](tests/test_python.py). Fit copies caller data and installs state only after successful validation/computation. Queries validate fitted feature dimensions.

Validation derives diag(8/3,2/3) covariance by hand, checks the0.8 variance ratio/reconstruction error2, compares NumPy/sklearn subspaces rather than signs, and covers constant/tiny/rank-deficient data and dimensions.

## 14. C++ Implementation

C++ is optional for this authorized Python/NumPy scope and is absent; no placeholder source or test is provided. DSA still requires actual Python/C++17/C++20 checks.

## 15. Input and Output Examples

From repository root, with requirements-ml-test.txt installed:

```sh
python machine-learning/unsupervised-learning/dimensionality-reduction/principal-component-analysis/python/example.py
```

The example uses the dry-run input and prints a JSON embedding. The solution also accepts a JSON object with X, optional parameters and y for supervised LDA on stdin. Actual example/CLI outputs are retained in the Phase 17 evidence. Numeric coordinates are sign/rotation dependent where explained; objectives and subspaces are the comparison contract.

## 16. Edge Cases

Constant features and duplicate rows are valid. Entirely constant training data returns zero scores, variances and ratios. Rank-deficient trailing directions are arbitrary orthogonal null directions. Variance units may underflow for extremely tiny input; normalized explained ratios remain meaningful. SVD sign ambiguity does not change reconstruction.

Reject nonfinite/nonreal arrays, invalid dimensions and unsupported resource limits before fitting. Invalid refits preserve previous fitted arrays. Random methods use a local generator and never modify global RNG state.

## 17. Advantages

Orthogonal components, an exact least-squares rank-k interpretation, and reusable mean/projection for new observations.

## 18. Disadvantages and Limitations

Only linear variance is optimized. A large-variance nuisance may dominate a useful low-variance feature. Samples are equally weighted; no sparse input, automatic feature scaling or probabilistic noise model. Same dense numeric bounds as SVD.

## 19. When to Use It

Use for a small linear compression problem where squared error and variance in the chosen units are meaningful.

## 20. When Not to Use It

Use supervised LDA for class-separation objectives or an explicit nonlinear representation when linear structure is inadequate.

## 21. Comparison With Related Algorithms

PCA ignores labels; LDA projection optimizes between/within scatter and needs labels. SVD is its uncentered numerical building block. Nonlinear autoencoders have nonconvex reconstruction objectives and are not guaranteed to improve on PCA.

## 22. Interview Questions

Why center? To separate variation from the coordinate origin. Is standardization inherent? No: it changes the covariance objective. Why use sign-invariant reference comparisons? Flipping a component and its score preserves reconstruction.

## 23. Practice Problems

Derive the covariance eigenvalues for the dry run. Verify discarded variance equals reconstruction error/(n-1). Rescale one feature and explain how the selected direction changes.

## 24. References

[scikit-learn PCA documentation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html); [NumPy independent SVD oracle](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). This lesson is part of Phase 17 B5; owner review is pending.
