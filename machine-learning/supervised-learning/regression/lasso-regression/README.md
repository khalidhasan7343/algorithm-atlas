# Lasso Regression

## 1. Algorithm Name

**Lasso Regression** — dense, single-output educational regression. The canonical topic is `lasso-regression` in B1 Supervised Learning — Regression, Phase 13.

## 2. Overview

Lasso estimates a linear predictor with an L1 coefficient penalty. The penalty can make some coefficients exactly zero. This implementation teaches cyclic coordinate descent: minimize one coefficient subproblem at a time, maintain residuals and stop only when the documented optimality-residual test is satisfied.

## 3. Problem Statement

Given X∈Rⁿˣᵖ and y∈Rⁿ, minimize J(w,b)=||Xw+b1−y||²/(2n)+αΣⱼ|wⱼ|, with finite α≥0. The intercept is optional and unpenalized. This mean-loss normalization matches scikit-learn Lasso, and differs from Ridge's summed residual loss. Fit returns an estimator with p coefficients, one intercept and 1D predictions. The objective is convex, but coefficients can be nonunique when columns are dependent.

## 4. Why Do We Need This Algorithm?

A dense OLS solution may use every supplied feature, including weak or redundant predictors. L1 regularization trades training fit for smaller and possibly sparse weights. Sparsity is useful for interpretation or limited measurement budgets, but correlated features and sampling variation can make the selected feature set unstable.

## 5. Real-World Applications

Examples include a compact linear baseline with many candidate numerical predictors or examining whether a few feature groups explain most training variation. Standardize units using training-fitted scales when comparable penalization is desired. A zero coefficient is an optimization result under a chosen alpha, not proof that a variable has no real-world effect.

## 6. Core Intuition

For centered A and c, isolate coordinate j. Let rⱼ=c−Σₖ≠ⱼAₖwₖ, zⱼ=AⱼᵀAⱼ/n and qⱼ=Aⱼᵀrⱼ/n. Its scalar objective is zⱼwⱼ²/2−qⱼwⱼ+α|wⱼ| plus constants. The exact minimizer is S(qⱼ,α)/zⱼ, where S(q,t)=sign(q)max(|q|−t,0). The thresholding interval produces exact zeros; no differentiability at zero is assumed.

## 7. Prerequisites

Read [Linear Regression](../linear-regression/README.md) for centering and residuals. Know absolute-value subgradients, convex objectives and coordinate minimization. [Elastic Net](../elastic-net/README.md) adds L2 curvature and tests the Lasso endpoint explicitly. No gradient descent learning rate or stochastic seed is required by the deterministic solver.

## 8. Step-by-Step Working Process

1. Copy/validate X,y and compute training offsets if fitting an intercept.
2. Initialize w=0, residual r=c, and column curvatures zⱼ.
3. Visit features in original column order. Temporarily restore the old coordinate contribution, compute qⱼ, soft-threshold, and remove the new contribution. Zero-curvature columns stay zero.
4. Recompute r=c−Aw after every cycle to limit accumulated residual drift; append the full objective to `loss_history_`.
5. For g=Aᵀ(Aw−c)/n, active coordinates require gⱼ+αsign(wⱼ)=0; zero coordinates require |gⱼ|≤α. The maximum violation must be ≤tol·max(1,||Aᵀc/n||∞).
6. On success recover b=μy−μxᵀw and commit. Exhausting max_iter raises ConvergenceError without replacing a prior successful model.

Each exact coordinate minimization cannot increase the convex objective. The measured KKT tolerance establishes approximate stationarity, not an exact coefficient-error bound or a finite-iteration guarantee on arbitrary scaling.

## 9. Pseudocode

```text
w = zeros(p); r = centered_y
for cycle in 1..max_iter:
  for j in 0..p-1:
    if column_curvature[j] == 0: continue
    partial = r + column[j] * w[j]
    q = dot(column[j],partial) / n
    w[j] = soft_threshold(q,alpha) / column_curvature[j]
    r = partial - column[j] * w[j]
  recompute residual and objective
  if maximum_KKT_violation <= scaled_tolerance: commit and return
raise ConvergenceError
```

## 10. Dry Run

For X=[−1,0,1]ᵀ and y=[−2,0,2]ᵀ, means are zero, z=2/3 and q=4/3. With α=1/3, S(q,α)=1, giving w=1/(2/3)=3/2. Residuals y−Xw are [−1/2,0,1/2]. The objective is (1/2)/(2·3)+(1/3)(3/2)=7/12. The smooth gradient is −1/3, canceled by the active L1 subgradient +1/3. A query x=2 predicts 3. If α≥4/3 the optimum coefficient is zero.

## 11. Time Complexity

Let T be completed full coordinate cycles. Every coordinate scans n values, and residual refresh/KKT checks each cost O(np); total O(Tnp+np). Prediction costs O(mp). T is data-, tolerance- and scaling-dependent, and is bounded by the configured max_iter rather than promised to be small. A direct OLS solve is used nowhere in the coordinate loop.

## 12. Space Complexity

Training retains O(np+n+p) copied/centered arrays, residuals and coefficient/curvature vectors. History adds O(T) scalar losses. The fitted estimator keeps O(p+T) state and no training matrix. Prediction needs O(mp+m) including its checked copy. Iteration is explicit; there is no recursive optimizer or dataset download.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) provides `LassoRegression(alpha=1.0, fit_intercept=True, tol=1e-7, max_iter=10000)`. Alpha is in [0,10¹²], tolerance in (0,1], and max_iter in 1..100000. Fit returns self only after KKT success. Inspect `n_iter_`, `loss_history_`, `objective_`, `kkt_violation_`, `stopping_threshold_`, `coef_`, `intercept_` and `training_mse_`. Predict/score have the same shapes as OLS. There is no warm start, automatic feature scaling or random coordinate selection.

## 14. C++ Implementation

C++ is optional for classical ML and **not implemented** for this topic. There is no dummy C++ source or C++ test. The catalog keeps `cpp_status: planned` as an honest optional deliverable; Python/numerical completion is independent of it. DSA retains mandatory Python/C++ and both C++17/C++20 gates. See the [track policy](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install runtime dependencies with `python -m pip install -r requirements-ml.txt`, then run:

```sh
.venv/bin/python machine-learning/supervised-learning/regression/lasso-regression/python/example.py
```

Expected rounded prediction:

```text
[3.0]
```

The example fits the small training dataset from the dry run and predicts a separate query. Equivalent API code is:

```python
import numpy as np
from solution import LassoRegression  # run from this topic's python/ directory
X = [[-1.0], [0.0], [1.0]]
y = [-2.0, 0.0, 2.0]
model = LassoRegression(alpha=1.0 / 3.0).fit(X, y)
print(np.round(model.predict([[2.0]]), 6).tolist())
```

The standalone `solution.py` also accepts one JSON object with `X`, `y`, `predict` and an optional constructor `parameters` object, and returns `{"predictions":[...]}` at full float64 precision. Invalid data or non-convergence produces stderr and exit 2, with no successful prediction JSON. Run tests with `python -m pytest machine-learning/supervised-learning/regression/lasso-regression -q` after installing `requirements-ml-test.txt`.

## 16. Edge Cases

Constant centered columns remain zero, constant targets fit the mean, and duplicate columns are allowed. Deterministic feature order chooses one representative when weights are nonunique; compare predictions/objectives rather than requiring another solver's exact coefficients. Alpha zero is unregularized coordinate descent, still subject to the iteration bound, not a promise of minimum-norm coefficients. Invalid alpha/tol/iterations, wrong shapes, nonfinite inputs and unsupported magnitudes fail explicitly. Failed refits preserve successful state.

## 17. Advantages

Soft thresholding is directly visible and independently testable. The objective and KKT diagnostics expose what stopping means. The implementation is deterministic, supports sparse coefficients, keeps the intercept unpenalized and retains the original training arrays unchanged.

## 18. Disadvantages and Limitations

Feature units influence both the penalty and stopping scale. Correlation can slow coordinate convergence or make the selected feature set unstable. Absolute-gradient tolerance is not a generalization or exact parameter-accuracy certificate. Finite precision can under-resolve tiny curvatures; non-convergence is reported rather than silently accepted. This dense educational model lacks sample weights, screening rules, sparse matrices and statistical confidence intervals.

## 19. When to Use It

Use Lasso for an explicitly sparse linear objective on modest numerical data. Choose alpha with training/validation data, inspect active coefficients and held-out MSE/MAE/R², and verify whether a selected feature set is stable under sensible resampling. Fit any scaler solely on training observations.

## 20. When Not to Use It

Do not use Lasso as an automatic causal feature selector or expect stable individual weights from identical columns. If grouped correlated predictors should share weight, investigate Elastic Net. If all weights should shrink smoothly without sparsity, use Ridge. Avoid forcing a strict tolerance and tiny iteration budget on ill-scaled data.

## 21. Comparison With Related Algorithms

| Related model | Difference |
| --- | --- |
| OLS | No sparsity penalty; direct minimum-norm solver in its canonical implementation |
| Ridge | L2 penalty; usually dense coefficients and direct augmented solve |
| Elastic Net, l1_ratio=1 | Same objective and coordinate updates as this Lasso |
| Subset selection | Discrete combinatorial feature choice; Lasso is a convex relaxation with different behavior |

## 22. Interview Questions

Derive the soft-threshold update. What is the correct subgradient condition at zero? Why should we not require equal coefficients from two solvers on duplicate columns? Explain why changing feature units changes the penalty. What does the stored KKT tolerance guarantee, and what does it not guarantee?

## 23. Practice Problems

1. Solve a single-coordinate problem for increasing alpha, including the exact-zero threshold.
2. Build two identical columns and compare objective/predictions under different column orders.
3. Use a fixed-seed held-out experiment to compare validation-selected alpha values, recording support stability and numerical stopping diagnostics without test-set leakage.

## 24. References

- [scikit-learn Lasso objective and coordinate-descent discussion](https://scikit-learn.org/1.8/modules/linear_model.html#lasso).
- [Friedman, Hastie and Tibshirani: Regularization Paths for Generalized Linear Models via Coordinate Descent](https://pmc.ncbi.nlm.nih.gov/articles/PMC2929880/).

Gradient checks avoid zero coefficients and other nondifferentiable points; separate subgradient/KKT tests cover exact zeros.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). See [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 13 owner review is pending; implementation and test evidence do not imply owner approval.
