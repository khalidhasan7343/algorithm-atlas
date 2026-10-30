# Linear Discriminant Analysis — supervised projection

## 1. Algorithm Name

Linear Discriminant Analysis — supervised projection

## 2. Overview

Use class labels to find linear coordinates with high between-class separation relative to within-class spread. This is a projection API, not the B2 LDA classifier.

## 3. Problem Statement

Given X(n,p), homogeneous integer or nonempty string labels y(n), C>=2 classes and 1<=k<=min(p,C-1), learn k Fisher directions and return centered projected observations.

## 4. Why Do We Need This Algorithm?

Variance alone can emphasize nuisance directions; labels let the projection prioritize differences between class means instead.

## 5. Real-World Applications

Supervised visualization and compression of small labeled measurement tables when class separation is approximately linear.

## 6. Core Intuition

Reward moving class centers apart, penalize directions where samples already spread within their own class.

Sw=sum_c sum_(i in c)(xi-mu_c)(xi-mu_c).T; Sb=sum_c n_c(mu_c-mu)(mu_c-mu).T. Maximize v.T Sb v / (v.T Sw v). Stationary directions solve Sb v=lambda Sw v. After global scaling, diagonalize M=Sw+reg I; H=M^(-1/2) and symmetric H Sb H yields ordinary eigenvectors u, then v=H u. Rank(Sb)<=C-1 explains the dimensional bound.

## 7. Prerequisites

Vectors, inner products, matrix multiplication, derivatives where optimization is used, and floating-point tolerances. Read the [B5 contracts](../../../../docs/dimensionality-reduction-conventions.md) and linked comparisons below.

## 8. Step-by-Step Working Process

Validate labels using preserved B2 rules, center/scale X uniformly, accumulate scatters, check positive resolved eigenvalues of regularized within scatter, whiten it and diagonalize the symmetric between scatter. Select largest eigenvalues, Euclidean-normalize directions and orient signs. Store class means/counts, both physical and normalized scatters and the training mean. Transform needs no new labels. No predict/predict_proba method is invented.

## 9. Pseudocode

```text
encode y; require C>=2 and k<=min(p,C-1)
A=(X-mean)/scale
accumulate Sw and Sb by class
H=inverse square root(Sw+reg I); fail if unresolved
u=eigenvectors of H Sb H for largest k eigenvalues
v=H u; normalize/sign orient
transform query=(query-mean) v
```

## 10. Dry Run

X=[(-2,-1),(-2,1),(2,-1),(2,1)], y=(0,0,1,1), reg=0.1. Mean=(0,0); physical Sw=diag(0,4), Sb=diag(16,0). Normalized X divides by 2, so normalized Sw=diag(0,1), Sb=diag(4,0). Regularization makes the denominator nonsingular; selected direction=(1,0), scores=(-2,-2,2,2).

## 11. Time Complexity

Fit O(n*p²+p³) for dense scatter accumulation and two eigendecompositions; class grouping O(C*n) here with C<=32. Query O(q*p*k). No iteration-count variability in the estimator.

## 12. Space Complexity

O(n*p+p²+C*p) fit memory and O(p*k+p²+C*p) retained diagnostics; no recursion.

## 13. Python Implementation

[LDAProjection source](python/solution.py) implements the stated mechanism using NumPy primitives and shared bounded contracts; no reference estimator is imported. [Executable example](python/example.py); [tests](tests/test_python.py). Fit copies caller data and installs state only after successful validation/computation. Queries validate fitted feature dimensions.

Validation independently accumulates multiclass scatter, checks generalized eigen residuals and SciPy/sklearn projection spaces; the analytical two-class fixture fixes direction(1,0). Singular/regularized/constant/label/dimensional cases are explicit.

## 14. C++ Implementation

C++ is optional for this authorized Python/NumPy scope and is absent; no placeholder source or test is provided. DSA still requires actual Python/C++17/C++20 checks.

## 15. Input and Output Examples

From repository root, with requirements-ml-test.txt installed:

```sh
python machine-learning/unsupervised-learning/dimensionality-reduction/linear-discriminant-analysis-projection/python/example.py
```

The example uses the dry-run input and prints a JSON embedding. The solution also accepts a JSON object with X, optional parameters and y for supervised LDA on stdin. Actual example/CLI outputs are retained in the Phase 17 evidence. Numeric coordinates are sign/rotation dependent where explained; objectives and subspaces are the comparison contract.

## 16. Edge Cases

One class, mixed/float/bool labels, mismatched target length and k>C-1 fail. Singular or relatively unresolved Sw fails at reg=0; positive reg may make the explicitly changed objective well-defined. Constant data with reg>0 is supported but has zero discriminating eigenvalues, not informative separation. Equal eigenvalues permit nonunique bases.

Reject nonfinite/nonreal arrays, invalid dimensions and unsupported resource limits before fitting. Invalid refits preserve previous fitted arrays. Random methods use a local generator and never modify global RNG state.

## 17. Advantages

Label-aware, compact and interpretable scatter diagnostics with a reusable new-observation transform.

## 18. Disadvantages and Limitations

Supervision is required even though the syllabus places it under unsupervised-learning. reg is dimensionless in globally normalized scatter units, in [0,1], default0; it is not automatically chosen shrinkage. A class with one observation contributes zero within scatter. k is bounded by min(p,C-1), not a guarantee of k positive discriminant eigenvalues.

## 19. When to Use It

Use when labeled class-mean separation in a low-dimensional linear subspace is the desired objective.

## 20. When Not to Use It

Use PCA without labels; use the existing B2 LDA classifier when class predictions or posterior probabilities are needed.

## 21. Comparison With Related Algorithms

PCA maximizes total variance and ignores y. This LDA projection optimizes a scatter ratio and returns coordinates. B2 LDA uses related class moments to classify under a shared Gaussian covariance assumption; neither implementation replaces the other.

## 22. Interview Questions

Why C-1? Centered C class means satisfy a weighted zero-sum relation. Why whiten Sw? It turns a generalized symmetric eigenproblem into an ordinary one. Does regularization leave the objective unchanged? No, it modifies the denominator.

## 23. Practice Problems

Calculate all dry-run scatters by hand. Add a redundant feature and compare singular rejection versus positive reg. Compare projection column spaces with SciPy generalized eigh without requiring equal signs/scales.

## 24. References

[scikit-learn LDA mathematical guide](https://scikit-learn.org/stable/modules/lda_qda.html); [SciPy generalized eigh oracle](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh.html).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). This lesson is part of Phase 17 B5; owner review is pending.
