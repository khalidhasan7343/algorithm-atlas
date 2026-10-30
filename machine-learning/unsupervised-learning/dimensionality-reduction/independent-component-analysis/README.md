# Independent Component Analysis — parallel tanh FastICA

## 1. Algorithm Name

Independent Component Analysis — parallel tanh FastICA

## 2. Overview

Separate a linear mixture into approximately independent non-Gaussian sources through whitening and simultaneous fixed-point contrast updates.

## 3. Problem Statement

Given centered linear mixtures X(n,p), choose k<=min(n-1,p) resolved covariance directions, learn an unmixing matrix and transform observations into k unit-population-variance components.

## 4. Why Do We Need This Algorithm?

Uncorrelated PCA coordinates need not be independent; a nonlinear non-Gaussian contrast can identify additional structure under an identifiable source model.

## 5. Real-World Applications

Small synthetic blind-source separation and educational signal-mixture experiments under a linear, sufficiently resolved mixing assumption.

## 6. Core Intuition

Whitening removes second-order dependence. An orthogonal rotation of the whitened coordinates then searches for non-Gaussian independent directions.

Center X and uniformly scale A. Eigendecompose E[A.T A]; K=diag(lambda^-1/2) V.T so Z=A K.T has population covariance I. For orthogonal W, U=Z W.T, g=tanh(U), proposal=E[g(U).T Z]-diag(E[1-g(U)^2])W. Symmetric decorrelation replaces proposal by (proposal proposal.T)^(-1/2) proposal. Stop when max_i ||<wnew_i,wold_i>|-1|<=tol.

## 7. Prerequisites

Vectors, inner products, matrix multiplication, derivatives where optimization is used, and floating-point tolerances. Read the [B5 contracts](../../../../docs/dimensionality-reduction-conventions.md) and linked comparisons below.

## 8. Step-by-Step Working Process

Validate k and rank; reject eigenvalues <=1e-12 of the largest retained covariance scale. Whiten, initialize W with a local seeded Gaussian matrix and decorrelate. Apply bounded fixed points and symmetric decorrelation until sign-invariant row alignment meets tolerance. Exhaustion raises ConvergenceError and preserves any earlier successful state. Retain mean, whitening, rotation, unmixing and pseudoinverse mixing; inverse_transform reconstructs only the retained subspace if k<p.

## 9. Pseudocode

```text
center/scale X; eig covariance; require k resolved directions
Z=whiten(X); W=decorrelate(seeded random matrix)
repeat <=max_iter:
  Wnew=decorrelate(mean(tanh(Z W.T)*Z)-mean(tanh derivative)*W)
  stop on sign-invariant row alignment
if exhausted: error; else retain unmixing and mixing
```

## 10. Dry Run

Four independent ±1 source combinations are mixed by [[1,0.5],[0.3,1.5]], giving X=[(-1.5,-1.8),(-0.5,1.2),(0.5,-1.2),(1.5,1.8)]. The mean is zero. Whitening makes Z.T Z/4=I; FastICA recovers the two binary sources up to sign/permutation, and inverse_transform reconstructs X. The executed evidence records the actual orientation rather than asserting an arbitrary source column order.

## 11. Time Complexity

Whitening O(n*p²+p³). T fixed-point iterations cost O(T*(n*k²+k³)); transformation O(q*p*k). T<=max_iter<=5000, default1000; no universal convergence guarantee.

## 12. Space Complexity

O(n*p+n*k+p²+k²) working arrays; O(p*k+k²+p) model state; no recursion.

## 13. Python Implementation

[FastICA source](python/solution.py) implements the stated mechanism using NumPy primitives and shared bounded contracts; no reference estimator is imported. [Executable example](python/example.py); [tests](tests/test_python.py). Fit copies caller data and installs state only after successful validation/computation. Queries validate fitted feature dimensions.

Validation checks whitening population covarianceI, centered recovered coordinates, inverse reconstruction and best-assignment absolute source correlation>0.97 on seeded uniform/Laplace mixtures. sklearn aligned recovery, rank rejection, deterministic seeds and exhausted iterations are tested.

## 14. C++ Implementation

C++ is optional for this authorized Python/NumPy scope and is absent; no placeholder source or test is provided. DSA still requires actual Python/C++17/C++20 checks.

## 15. Input and Output Examples

From repository root, with requirements-ml-test.txt installed:

```sh
python machine-learning/unsupervised-learning/dimensionality-reduction/independent-component-analysis/python/example.py
```

The example uses the dry-run input and prints a JSON embedding. The solution also accepts a JSON object with X, optional parameters and y for supervised LDA on stdin. Actual example/CLI outputs are retained in the Phase 17 evidence. Numeric coordinates are sign/rotation dependent where explained; objectives and subspaces are the comparison contract.

## 16. Edge Cases

Constant or requested rank-deficient mixtures fail explicitly; requesting fewer resolved directions is supported. Duplicate observations are allowed if covariance remains resolved. Near-degenerate mixing below the relative threshold is rejected. Compare sources by best permutation and absolute correlation; whitening uses population denominator n, not n-1.

Reject nonfinite/nonreal arrays, invalid dimensions and unsupported resource limits before fitting. Invalid refits preserve previous fitted arrays. Random methods use a local generator and never modify global RNG state.

## 17. Advantages

Genuine source-separation logic, explicit whitening and fixed points, deterministic local initialization, and diagnostic convergence delta.

## 18. Disadvantages and Limitations

Independent non-Gaussian sources and a linear mixing model are assumptions, not guarantees for arbitrary data. At most one Gaussian source is identifiable in the usual model; arbitrary multiple Gaussian sources cannot be uniquely separated. Sign, scale and permutation ambiguity remains. tol1e-12..1e-2 default1e-6; seed native integer0..2^32-1; no noise-aware or temporal ICA.

## 19. When to Use It

Use for small resolved linear mixtures when independent non-Gaussian source recovery is the intended lesson.

## 20. When Not to Use It

Use PCA for variance compression or when independence assumptions are unjustified. Use a noise/temporal model when the mixing process requires it.

## 21. Comparison With Related Algorithms

PCA decorrelates through covariance and has a variance ordering. ICA rotates whitened coordinates using higher-order contrast and has no intrinsic component order; low-variance directions discarded before ICA cannot be recovered.

## 22. Interview Questions

Why whiten first? To restrict the remaining mixing ambiguity to orthogonal rotations under the model. Why use absolute row alignment? Sign flips do not alter an independent direction. Why can two Gaussian sources be rotated without changing independence? Their isotropic whitened joint distribution is rotationally invariant.

## 23. Practice Problems

Check the four-source covariance analytically. Compare recovered columns using the best assignment of absolute correlations. Mix one source almost redundantly and determine when the rank guard rejects it.

## 24. References

[Hyvärinen author FastICA publications](https://www.cs.helsinki.fi/u/ahyvarin/papers/fastica.shtml); [scikit-learn FastICA reference](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). This lesson is part of Phase 17 B5; owner review is pending.
