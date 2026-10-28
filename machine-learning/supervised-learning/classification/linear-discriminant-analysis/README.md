# Linear Discriminant Analysis

## 1. Algorithm Name

**Linear Discriminant Analysis**, canonical `linear-discriminant-analysis` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

LDA classification assumes Gaussian class-conditional data with a common covariance matrix. The common quadratic part of the Gaussian log density cancels across classes, leaving linear discriminant scores. This implementation explicitly estimates class moments and a prior-weighted shared covariance, regularizes it and solves with Cholesky factors. It is a classifier, not a dimensionality-reduction API.

## 3. Problem Statement

For class k with nk observations, estimate mean μk and within-class population covariance Sk=Σ(xᵢ−μk)(xᵢ−μk)ᵀ/nk. Choose positive priors πk summing to one, empirical nk/n by default. Define Σ=ΣkπkSk+reg·I. With empirical priors this equals pooled within-class scatter divided by n. In centered coordinates z=x−offset and mk=μk−offset, score δk(z)=zᵀΣ⁻¹mk−½mkᵀΣ⁻¹mk+logπk. Class-independent terms are omitted. Predict the first largest score in sorted original class order; normalized exponentials give posterior columns.

## 4. Why Do We Need This Algorithm?

Estimating a separate covariance for every class can demand substantial data and yield unstable small-class matrices. Sharing covariance pools information and produces simpler linear boundaries. LDA provides a generative baseline with different assumptions from independent-feature Naive Bayes and discriminative Logistic Regression.

## 5. Real-World Applications

Examples include a modest measured-feature classification problem with roughly similar within-class covariance shapes, or studying how class priors move a linear Gaussian decision boundary. The shared Gaussian assumption should be evaluated, not accepted because the computation succeeds. Dataset bias and changing class prevalence can affect predictions.

## 6. Core Intuition

A multivariate Gaussian score contains −½(x−μk)ᵀΣ⁻¹(x−μk). Expanding yields a common −½xᵀΣ⁻¹x plus the class-dependent linear and constant terms. Dropping the common term preserves argmax and normalized posteriors, explaining linear pairwise boundaries. Regularization adds covariance curvature; it is not an explicit inverse or a coefficient L2 penalty.

## 7. Prerequisites

Know class-conditional Gaussians, covariance, positive-definite matrices, Cholesky factorization and Bayes' rule. [QDA](../quadratic-discriminant-analysis/README.md) permits different covariances and keeps class-specific quadratic terms. [Gaussian NB](../gaussian-naive-bayes/README.md) assumes diagonal conditional covariance, a different simplification.

## 8. Step-by-Step Working Process

1. Validate/copy X and labels; require at least two classes. Count class rows, validate empirical/supplied priors and center features by the overall training mean.
2. Compute each centered class mean and its population covariance with denominator nk. Combine covariances using πk, then add reg·I. With supplied priors, the weighting intentionally changes as well as the discriminant prior term.
3. Check covariance eigenvalues. Require λmin>machine_epsilon·p·max(λmax,smallest_normal_float); unresolved directions fail with a regularize/rescale error. This prevents Cholesky roundoff from accepting a mathematically singular covariance.
4. Factor Σ=L·Lᵀ and solve first L and then Lᵀ against all class means. These NumPy linear-algebra primitives perform numerical solves; the Gaussian estimation and discriminant logic are implemented here, without an explicit inverse.
5. Store centered linear coefficients and intercept terms, original-coordinate means, covariance/factor and training offset. Commit only after successful finite checks.
6. On query, subtract the fitted offset, calculate all class linear scores and normalize shifted log scores for probabilities. Ties choose the first sorted class.

No iterative optimizer or gradient convergence check is relevant. Positive-definiteness/resolution checks establish a usable numerical covariance under this policy, not that the Gaussian assumptions are true.

## 9. Pseudocode

```text
encode classes; validate priors; offset = training mean
for class k:
  centered_mean[k] = mean(X-offset for class k)
  population_cov[k] = centered_residual.T @ centered_residual / n_k
shared = sum(prior[k]*population_cov[k]) + reg*I
reject unresolved eigenvalues; L = cholesky(shared)
weights = solve(L.T, solve(L, centered_means.T)).T
bias[k] = -.5*dot(centered_mean[k],weights[k]) + log(prior[k])
score(query) = (query-offset) @ weights.T + bias
```

## 10. Dry Run

Class left has x=[−2,−1], class right x=[1,2], each prior 1/2. Their means are −1.5,+1.5 and population variances 0.25, so with reg=0 the shared covariance is 0.25. Scores are δleft(x)=−6x−4.5+log(1/2), δright(x)=6x−4.5+log(1/2). The equal-prior boundary is x=0; exact ties select left. Queries −3 and 3 predict left/right. At x=0, changing priors to [0.9,0.1] changes posterior to those priors because the class quadratic distances remain equal. The default example adds reg=10⁻⁶ without changing these label decisions.

## 11. Time Complexity

Computing means/scatters costs O(np²), shared covariance factor/eigenvalue checks O(p³), and class solves O(cp²). Total O(np²+p³+cp²); query scoring O(mpc), posterior normalization O(mc). p≤64 bounds dense covariance work. This implementation does not estimate a projection or an eigenvector-based LDA transform.

## 12. Space Complexity

Fit uses O(np+p²+cp+n), including copied centered data, covariance/factor and means. Fitted state retains O(p²+cp+c), not observations. Query copying/scores use O(mp+mc). Cholesky solves avoid storing a separately formed inverse but still require the dense covariance itself.

## 13. Python Implementation

`LinearDiscriminantAnalysis(reg=1e-6, priors=None)` supports multiclass fit, decision_function, predict_proba, predict and accuracy score. reg is finite in [0,10⁶] and adds absolute variance units to each covariance diagonal. Priors are optional positive values summing to one in sorted classes_ order. Fit n≤2048,p≤64 and at least two classes; classes with one sample are allowed if the regularized covariance is resolved. Shared 262144-cell, m≤10000 and finite |feature|≤10¹² bounds apply. Labels use homogeneous int64-compatible integers/nonempty strings, ≤32 classes. Inspect means_, covariance_, cholesky_, priors_, class_count_, condition_number_ and reg_. coef_/intercept_ represent centered discriminants: decision_function computes (X−_offset_)·coef_.T+intercept_. It returns(m,c), even for binary classification; scores can differ from another origin by a class-independent term. Predictions are original labels(m,), probability columns(m,c). No transform, automatic shrinkage, sample weights or pseudoinverse policy.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/linear-discriminant-analysis/python/example.py
```

Expected output:

```text
['left', 'right']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import LinearDiscriminantAnalysis
X = [[-2.0], [-1.0], [1.0], [2.0]]
y = ["left", "left", "right", "right"]
model = LinearDiscriminantAnalysis().fit(X, y)
print(model.predict([[-3.0], [3.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/linear-discriminant-analysis -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

Rank-deficient or numerically unresolved covariance at reg=0 raises ValueError, rather than inventing zero determinant densities. Positive regularization can resolve constant/near-collinear data; a very small reg relative to data scale can still be insufficient. Tiny classes are allowed, and priors affect both covariance weighting and score offsets. Empty shaped queries work. Invalid shapes/labels/priors/nonfinite data and budget violations fail. Failed refits preserve prior state; arrays are copied. Centering helps large offsets but cannot restore information already lost in float64 inputs.

## 17. Advantages

Multiclass Gaussian classification with compact shared state, linear query scores and explicit covariance/condition diagnostics. Stable factor solves, origin centering and resolution checks make numerical assumptions visible. Matched reference posterior tests cover both empirical and supplied priors.

## 18. Disadvantages and Limitations

Shared Gaussian covariance can underfit classes with different shapes. Priors and absolute diagonal regularization have modeling effects, and units matter. Numerical success is not calibration, fairness or generalization evidence. High-dimensional covariance estimates can be data-hungry even within resource caps. This classifier intentionally does not implement SVD projection, automatic shrinkage, singular pseudodensities, missing values or sample weights.

## 19. When to Use It

Use LDA as a modest-data shared-covariance baseline. Fit scaling only on training rows, choose regularization/priors using training and validation information, and evaluate held-out class metrics plus log loss. Inspect whether covariance sharing is plausible before interpreting the resulting linear boundary.

## 20. When Not to Use It

Do not claim quadratic boundaries or dimensionality reduction from this API. Do not accept an unresolved covariance by silently using an inverse/pseudoinverse. If class covariances differ substantially and populations support their estimation, compare the separately implemented QDA. Do not tune using final test labels.

## 21. Comparison With Related Algorithms

| Classifier | Covariance/objective assumption |
| --- | --- |
| LDA | One prior-weighted full covariance; linear pairwise boundaries |
| QDA | Separate class sample covariances; quadratic boundaries |
| Gaussian NB | Class-specific diagonal variances and feature independence |
| Logistic Regression | Binary discriminative cross-entropy, no Gaussian density assumption |

## 22. Interview Questions

Expand the Gaussian quadratic and identify the common term. What covariance denominator is used? How do supplied priors influence the estimate? Why check eigenvalue resolution before Cholesky? Explain why centered discriminant scores need not equal another solver's raw scores while posteriors agree.

## 23. Practice Problems

1. Derive the dry-run equal-prior boundary and its shift under unequal priors.
2. Duplicate a feature, observe the documented singular error and test explicit regularization.
3. Compare LDA/QDA boundaries on a fixed equal-covariance synthetic problem without requiring identical finite-sample posterior estimates.

## 24. References

- [scikit-learn LDA API and covariance estimators](https://scikit-learn.org/1.8/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html).
- [Official Gaussian discriminant formulation](https://scikit-learn.org/stable/modules/lda_qda.html).

Version-pinned 1.8 reference tests use the lsqr classifier with matching prior-weighted population covariance and reg=0 on full-rank data. Independent analytical/regularization tests cover the added diagonal policy and singular failure behavior.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
