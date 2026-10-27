# Elastic Net

## 1. Algorithm Name

**Elastic Net** — dense, single-output educational regression. The canonical topic is `elastic-net` in B1 Supervised Learning — Regression, Phase 13.

## 2. Overview

Elastic Net combines L1 sparsity and L2 shrinkage in a linear regression objective. This implementation uses cyclic coordinate minimization with an explicit denominator contribution from the L2 term. It exposes objective history and KKT diagnostics rather than reporting success merely because an iteration budget ended.

## 3. Problem Statement

For X∈Rⁿˣᵖ, y∈Rⁿ, α≥0 and mixing ratio η∈[0,1], minimize J(w,b)=||Xw+b1−y||²/(2n)+αη||w||₁+α(1−η)||w||²/2. The optional intercept b is unpenalized. η=1 is Lasso; η=0 is pure L2 with mean-loss normalization. If α(1−η)>0, the coefficient objective is strongly convex; otherwise coefficients can be nonunique.

## 4. Why Do We Need This Algorithm?

Lasso can select one of several similar predictors, while Ridge spreads weight without inducing exact zeros. Elastic Net offers a tunable compromise. Alpha controls total penalty strength and η controls the mixture; selecting them requires validation and does not guarantee a better test score than either endpoint.

## 5. Real-World Applications

Examples include modest regressions with correlated numerical feature groups or sparse baselines where both support size and coefficient stability matter. Comparable feature units are important because the penalties act on raw coefficients. The learned support remains sensitive to the dataset and objective, not a certified causal explanation.

## 6. Core Intuition

Set λ₁=αη and λ₂=α(1−η). A coordinate with partial correlation qⱼ and data curvature zⱼ has minimizer S(qⱼ,λ₁)/(zⱼ+λ₂). The numerator creates zeros; the extra denominator shrinks active weights and adds curvature. These are separate effects, so changing η is not equivalent to changing only alpha in Lasso.

## 7. Prerequisites

Know [Lasso Regression](../lasso-regression/README.md), absolute-value subgradients and [Ridge Regression](../ridge-regression/README.md). Be careful with loss scaling: this implementation's η=0 corresponds to the Ridge implementation's alpha equal to n·α. Both solve convex objectives, but use different algorithms.

## 8. Step-by-Step Working Process

1. Validate input and hyperparameters, copy observations and center only using training means.
2. Start from zero coefficients, precompute zⱼ=||Aⱼ||²/n, and retain residual c−Aw.
3. For each coordinate, restore its old residual contribution and calculate qⱼ. Divide the soft-thresholded qⱼ by zⱼ+λ₂. A zero denominator means no data or penalty curvature; keep that initialized coefficient zero.
4. Refresh the full residual and compute J at the end of each cycle.
5. With g=Aᵀ(Aw−c)/n+λ₂w, check active residual |gⱼ+λ₁sign(wⱼ)| and inactive violation max(|gⱼ|−λ₁,0).
6. Stop when their maximum is ≤tol·max(1,||Aᵀc/n||∞); recover the intercept and commit. Otherwise raise ConvergenceError at max_iter.

Exact coordinate steps decrease the convex objective. Stored tolerances are approximate stationarity checks; no unconditional finite-iteration or statistical generalization guarantee is asserted.

## 9. Pseudocode

```text
lambda1 = alpha * l1_ratio
lambda2 = alpha * (1 - l1_ratio)
w = zeros(p); r = centered_y
for cycle in 1..max_iter:
  for feature j:
    denominator = mean(column[j] ** 2) + lambda2
    if denominator == 0: continue
    partial = r + column[j] * w[j]
    w[j] = soft_threshold(mean(column[j] * partial), lambda1) / denominator
    r = partial - column[j] * w[j]
  recompute residual, objective and KKT residual
  if KKT residual <= scaled tolerance: commit and return
raise ConvergenceError
```

## 10. Dry Run

Use X=[−1,0,1]ᵀ, y=[−2,0,2]ᵀ, α=1/2 and η=1/2. Then λ₁=λ₂=1/4, z=2/3 and q=4/3. The coefficient is (4/3−1/4)/(2/3+1/4)=(13/12)/(11/12)=13/11. The intercept is zero, and x=2 predicts 26/11≈2.363636. The active stationarity equation z·w−q+λ₂w+λ₁=0 confirms the update independently.

## 11. Time Complexity

For T coordinate cycles on an n×p dense design, each cycle costs O(np), including residual refresh and KKT/objective evaluation. Total O(Tnp+np); prediction O(mp). The data, penalty, mixing ratio and tolerance influence T. A configured max_iter bounds attempted work but does not guarantee successful convergence for every allowed dataset.

## 12. Space Complexity

Training uses O(np+n+p+T) space for copied/centered data, residuals, coefficients, curvatures and recorded cycle losses. Successful fitted state stores O(p+T), with no training matrix. Inference's checked query copy and output cost O(mp+m). No optimizer recursion or external training service is involved.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `ElasticNetRegression(alpha=1.0, l1_ratio=0.5, fit_intercept=True, tol=1e-7, max_iter=10000)`. The ratio is in [0,1], alpha in [0,10¹²], tol in (0,1], and max_iter in 1..100000. Fit returns self after KKT success. Inspect `coef_`, `intercept_`, `objective_`, `loss_history_`, `n_iter_`, `kkt_violation_`, `stopping_threshold_`, `training_mse_` and `converged_`. Prediction and R² shapes match the other affine estimators.

## 14. C++ Implementation

C++ is optional for classical ML and **not implemented** for this topic. There is no dummy C++ source or C++ test. The catalog keeps `cpp_status: planned` as an honest optional deliverable; Python/numerical completion is independent of it. DSA retains mandatory Python/C++ and both C++17/C++20 gates. See the [track policy](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install runtime dependencies with `python -m pip install -r requirements-ml.txt`, then run:

```sh
.venv/bin/python machine-learning/supervised-learning/regression/elastic-net/python/example.py
```

Expected rounded prediction:

```text
[2.363636]
```

The example fits the small training dataset from the dry run and predicts a separate query. Equivalent API code is:

```python
import numpy as np
from solution import ElasticNetRegression  # run from this topic's python/ directory
X = [[-1.0], [0.0], [1.0]]
y = [-2.0, 0.0, 2.0]
model = ElasticNetRegression(alpha=0.5, l1_ratio=0.5).fit(X, y)
print(np.round(model.predict([[2.0]]), 6).tolist())
```

The standalone `solution.py` also accepts one JSON object with `X`, `y`, `predict` and an optional constructor `parameters` object, and returns `{"predictions":[...]}` at full float64 precision. Invalid data or non-convergence produces stderr and exit 2, with no successful prediction JSON. Run tests with `python -m pytest machine-learning/supervised-learning/regression/elastic-net -q` after installing `requirements-ml-test.txt`.

## 16. Edge Cases

Both mixing endpoints are supported and independently cross-checked. Alpha zero removes both penalties and uses coordinate descent; it does not impose the direct OLS solver's minimum-norm coefficient convention. Constant centered columns stay zero, and duplicate columns are permitted. Positive L2 curvature makes the exact coefficient optimum unique, but very small penalties relative to scale remain a finite-precision limitation. Invalid ratios, nonfinite data, wrong shapes and exhausted iteration budgets fail explicitly; a failed refit leaves prior successful state intact.

## 17. Advantages

A visible bridge between Lasso and Ridge with deterministic updates, explicit sparsity, objective history and testable optimality residuals. The L2 term can stabilize correlated directions while retaining an L1 component. No hidden scaling, stochastic coordinate order or third-party estimator is used.

## 18. Disadvantages and Limitations

Two hyperparameters increase model-selection work. Penalties depend on feature units and can increase bias. Small L2 curvature does not guarantee fast coordinate convergence; a KKT threshold is not a universal coefficient-error bound. This dense implementation omits screening paths, warm starts, sparse matrices, weights and multi-output regression. Validate hyperparameters without inspecting test-set targets.

## 19. When to Use It

Use it for a moderate linear problem where sparsity and correlated-feature shrinkage are both relevant. Fit any scaling solely on training rows; compare validation objectives and held-out prediction metrics with Lasso and Ridge. Report iteration and KKT diagnostics alongside scores.

## 20. When Not to Use It

Avoid treating η=0 as the same numeric alpha as Ridge without multiplying by n. Do not force a strict iteration budget to stand in for convergence. A nonlinear response or huge dense feature space may require a different representation or solver, outside this lesson's educational scope.

## 21. Comparison With Related Algorithms

| Endpoint or alternative | Exact relationship |
| --- | --- |
| η=1 | Lasso objective with the same alpha and mean-loss normalization |
| η=0 | Ridge objective after mapping Ridge alpha=n·alpha |
| α=0 | Unpenalized least squares objective, possibly nonunique coordinate solution |
| Polynomial Regression | Changes the basis; this model only changes coefficient regularization |

## 22. Interview Questions

Derive the coordinate denominator and threshold. When is the coefficient optimum unique? How does the Ridge alpha mapping follow from multiplying the objective by n? Why are coefficients alone a poor comparison on nonunique problems? What diagnostics distinguish early convergence from an exhausted iteration budget?

## 23. Practice Problems

1. Verify the one-coordinate dry run for three mixing ratios.
2. Duplicate a feature and compare Lasso versus a positive-L2 Elastic Net solution.
3. Use a fixed-seed split to tune alpha and ratio on validation data, then evaluate once on a held-out test set, retaining objective/KKT histories.

## 24. References

- [scikit-learn Elastic Net formulation](https://scikit-learn.org/1.8/modules/linear_model.html#elastic-net).
- [Coordinate descent for regularized models, Friedman et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC2929880/).

Reference tests align objective normalization and intercept handling and compare predictions where duplicate features make endpoint coefficients nonunique.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). See [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 13 owner review is pending; implementation and test evidence do not imply owner approval.
