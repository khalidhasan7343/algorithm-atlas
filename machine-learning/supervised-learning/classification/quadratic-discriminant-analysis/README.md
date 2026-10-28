# Quadratic Discriminant Analysis

## 1. Algorithm Name

**Quadratic Discriminant Analysis**, canonical `quadratic-discriminant-analysis` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

QDA models each class by a Gaussian with its own full covariance. Class-dependent quadratic terms remain in the log score, allowing quadratic decision boundaries. This implementation estimates sample covariances, applies explicit identity shrinkage, checks numerical resolution and uses Cholesky solves/log determinants without matrix inversion.

## 3. Problem Statement

For class k with nk≥2 observations, mean μk and sample covariance Sk=Σ(xᵢ−μk)(xᵢ−μk)ᵀ/(nk−1), define Σk=(1−reg_param)Sk+reg_param·I, reg_param∈[0,1]. Score δk(x)=logπk−½logdetΣk−½(x−μk)ᵀΣk⁻¹(x−μk). The common −p/2 log(2π) is omitted. Empirical priors default to nk/n, or use supplied positive priors summing to one. Predict the first maximum in sorted class order; normalize shifted log scores for posterior columns.

## 4. Why Do We Need This Algorithm?

When class covariance shapes differ, a shared-covariance LDA boundary can be too restrictive. QDA keeps those different quadratic distance and determinant terms. The extra flexibility requires more covariance parameters and enough per-class data, so explicit regularization and failure handling are part of a trustworthy implementation.

## 5. Real-World Applications

Examples include small Gaussian clusters with different dispersions or studying why broad and narrow classes can dominate different regions despite the same mean. This is a modeling exercise, not a guarantee that real class-conditional densities are Gaussian or that the resulting probabilities are calibrated.

## 6. Core Intuition

The Gaussian determinant term penalizes diffuse class densities near the mean, while the covariance-scaled quadratic controls tail decay and directionality. With different Σk, the pairwise quadratic terms no longer cancel. Equal covariance assumptions recover linear boundaries, but finite-sample covariance conventions can still differ from LDA's pooled population estimator.

## 7. Prerequisites

Know covariance, multivariate Gaussians, positive-definite matrices, triangular solves and log determinants. [LDA](../linear-discriminant-analysis/README.md) shares covariance; [Gaussian NB](../gaussian-naive-bayes/README.md) uses diagonal conditional variances. Understand the distinction between population denominator nk and this topic's sample denominator nk−1.

## 8. Step-by-Step Working Process

1. Validate/copy dense numerical X and labels; require at least two classes and two rows in every class. Validate empirical or supplied priors.
2. Center by a common training offset to reduce large-origin arithmetic, then compute each class mean and residual scatter.
3. Divide scatter by nk−1 and apply (1−reg_param)Sk+reg_param·I. Priors change score terms, not these per-class covariance estimates.
4. Check each covariance eigenvalue: λmin must exceed machine_epsilon·p·max(λmax,smallest_normal_float). Reject singular or unresolved directions even if rounded Cholesky would return a tiny positive diagonal.
5. Factor Σk=LkLkᵀ. Compute logdetΣk=2Σlog(diag(Lk)), avoiding determinant underflow/overflow and explicit inverses. Commit only after all classes succeed.
6. For each class, solve Lk·z=(x−μk), and use ||z||² for the quadratic form. Add log prior and log determinant, then predict/normalize shifted log scores.

There is no iterative optimizer. Regularization is a fixed modeling/numerical policy, not a learned convergence process or a proof of correct density assumptions.

## 9. Pseudocode

```text
encode classes; require every class count >= 2; validate priors
for class k:
  mean[k] = training class mean
  sample_cov = residual.T @ residual/(n_k-1)
  covariance[k] = (1-reg_param)*sample_cov + reg_param*I
  reject unresolved eigenvalues; L[k] = cholesky(covariance[k])
  logdet[k] = 2*sum(log(diag(L[k])))
for class k and query rows:
  whitened = solve(L[k], (query-mean[k]).T)
  score[:,k] = log(prior[k]) - .5*(logdet[k]+sum(whitened**2))
predict first maximum; normalize shifted scores for posterior
```

## 10. Dry Run

Take two classes with mean zero. Train narrow on [−sqrt(1/2),+sqrt(1/2)] and wide on [−sqrt(2),+sqrt(2)]. Unbiased sample variances are 1 and 4. With equal priors and reg_param=0, δwide−δnarrow=−log2+(3/8)x². Thus narrow wins at zero, and wide wins for |x|>sqrt((8/3)log2)≈1.35956; queries [−2,0,2] predict [wide,narrow,wide]. This independently checked two-boundary example demonstrates a quadratic rule. The runnable example instead uses means ±1.5 with equal sample variance 0.5, predicting left/right at −3,+3.

## 11. Time Complexity

Class covariance estimation totals O(np²), factorization/eigenvalue checks O(cp³), and mean/count preparation O(np+n log n). Query solves cost O(mcp²), with O(mc) normalization. Compared with LDA, separate factors increase both fitted-state and inference costs. Training p≤64 and c≤32 bound dense work.

## 12. Space Complexity

Fit uses O(np+cp²+cp+n) for checked/centered data, class covariances, factors and moments. Fitted state is O(cp²+cp+c), no retained observations. Query copying/one-class solve workspace and scores use O(mp+mc). No explicit inverse or model checkpoint is stored.

## 13. Python Implementation

`QuadraticDiscriminantAnalysis(reg_param=1e-6, priors=None)` exposes fit, decision_function, predict_proba, predict and accuracy score. reg_param is finite in [0,1]; one yields identity covariance for every class. Priors are positive and sum to one in sorted classes_ order. Fit n≤2048,p≤64, at least two classes and nk≥2; shared cell/magnitude/query caps apply. Labels are homogeneous int64-compatible integers or nonempty strings, at most 32 classes. Inspect means_, covariance_ (c,p,p), cholesky_ factors, log_det_, priors_, class_count_ and reg_param_. Scores/probabilities return(m,c), even binary; predicted original labels(m,). Fit returns self. There are no automatic shrinkage estimates, sample weights, transform or singular pseudodensity mode.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/quadratic-discriminant-analysis/python/example.py
```

Expected output:

```text
['left', 'right']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import QuadraticDiscriminantAnalysis
X = [[-2.0], [-1.0], [1.0], [2.0]]
y = ["left", "left", "right", "right"]
model = QuadraticDiscriminantAnalysis().fit(X, y)
print(model.predict([[-3.0], [3.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/quadratic-discriminant-analysis -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

Singular/unresolved unregularized covariance raises ValueError; regularization can resolve constant or nearly collinear features if sufficiently large relative to scale. One-row classes are rejected even with shrinkage because the sample-covariance contract requires nk−1>0. Repeated observations and unequal class populations are allowed otherwise. Empty shaped queries work. Nonfinite data, bad shapes/labels/priors and invalid bounds fail explicitly. A failed covariance in any class leaves a previous fitted model intact; inputs are not mutated. A large common feature origin is handled using training-centered residuals, without recovering information already rounded away.

## 17. Advantages

Authentic multiclass quadratic Gaussian scoring with visible class covariance and determinant diagnostics. Stable factor solves avoid inverse formation. Independent full-density calculations and matched reference covariances validate both the estimation convention and posterior normalization.

## 18. Disadvantages and Limitations

Class-specific covariance needs more data and can overfit small classes. Shrinkage toward identity depends on feature units and may bias boundaries. Gaussian assumptions, covariance resolution and held-out calibration are distinct issues. No missing values, sparse data, sample weighting or automatic shrinkage policy. Extremely poor scaling can remain unresolved despite positive regularization and will fail explicitly.

## 19. When to Use It

Use it as a small full-covariance generative baseline where different class shapes are plausible and each class has enough observations. Fit scaling on training only, select reg_param with validation and evaluate held-out class-specific metrics/log loss. Inspect class population and covariance conditioning when a result is unstable.

## 20. When Not to Use It

Do not claim that a successful Cholesky factor proves statistical reliability or that QDA always outperforms LDA. Do not compare posteriors across covariance-normalization conventions without aligning them. Avoid using a one-row class or silently applying a pseudoinverse to a singular density.

## 21. Comparison With Related Algorithms

| Model | Difference |
| --- | --- |
| LDA | Shared prior-weighted population covariance; linear pairwise rule |
| Gaussian NB | Diagonal conditional variances; fewer covariance parameters |
| QDA reg_param=1 | All covariances become identity, reducing pairwise quadratic terms to linear differences |
| CART | Greedy discontinuous partitions without Gaussian covariance assumptions |

## 22. Interview Questions

Why does a class-specific quadratic remain after expansion? Derive the equal-mean/different-variance dry run. Why compute log determinant from a factor? Explain the nk−1 requirement and identity shrinkage. When can LDA/QDA produce the same boundary without identical posterior probabilities?

## 23. Practice Problems

1. Verify the two symmetric decision boundaries in the dry run.
2. Duplicate a feature and test the documented failure/regularization behavior.
3. Compare validation-selected LDA/QDA on a fixed synthetic split with shared versus unequal covariance shapes, reporting uncertainty in a single-split result rather than universal model rankings.

## 24. References

- [scikit-learn QDA API, sample covariance and regularization](https://scikit-learn.org/1.8/modules/generated/sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis.html).
- [Official Gaussian discriminant formulation](https://scikit-learn.org/stable/modules/lda_qda.html).

Pinned 1.8 reference tests align priors, sample covariance and reg_param on full-rank per-class data with nk>p. Independent slogdet/linear-solve and exact one-dimensional tests cover mathematical scores and singular policy separately.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
