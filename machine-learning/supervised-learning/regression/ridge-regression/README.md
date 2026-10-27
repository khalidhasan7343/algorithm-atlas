# Ridge Regression

## 1. Algorithm Name

**Ridge Regression** — dense, single-output educational regression. The canonical topic is `ridge-regression` in B1 Supervised Learning — Regression, Phase 13.

## 2. Overview

Ridge Regression fits a linear predictor while discouraging large coefficients through an L2 penalty. This dense single-output implementation solves an augmented least-squares system. It does not explicitly invert a Gram matrix, and an optional intercept is never penalized.

## 3. Problem Statement

For X∈Rⁿˣᵖ and y∈Rⁿ, minimize J(w,b)=½||Xw+b1−y||²+α||w||²/2 with α≥0. The loss is a sum, not a mean; this normalization matches scikit-learn Ridge. `fit_intercept=False` fixes b=0. Positive α makes the coefficient subproblem strictly convex. At α=0, choose the centered minimum-norm OLS solution under the numerical rank cutoff.

## 4. Why Do We Need This Algorithm?

Nearly collinear columns can let OLS fit the same data using very different large weights. Penalizing weight length trades some training fit for a more stable solution. Alpha is a hyperparameter to select with training/validation data; improved test performance is a possibility, not a guarantee.

## 5. Real-World Applications

Applications include regularized baselines for correlated sensor measurements or many related numerical predictors. Standardizing features with training-fitted scales can make the coefficient penalty more comparable across units. The model remains associational and does not by itself handle distribution shift or causal confounding.

## 6. Core Intuition

For an SVD A=UΣVᵀ of the centered design, ridge replaces the unstable reciprocal 1/σ by σ/(σ²+α). Small singular directions are shrunk most strongly. Instead of forming AᵀA, stack √αI below A and zeros below the target: ordinary least squares on that augmented system minimizes exactly the penalized objective.

## 7. Prerequisites

Understand OLS, vector norms, convex quadratic objectives and singular values. Read [Linear Regression](../linear-regression/README.md) for intercept elimination, and [Elastic Net](../elastic-net/README.md) for combined L1/L2 penalties. Ridge's α uses a summed residual loss; Elastic Net uses a mean loss, so the same numeric α has a different meaning.

## 8. Step-by-Step Working Process

1. Validate α, `fit_intercept`, input dtypes/shapes and resource limits.
2. Compute training means and center only if an intercept is fitted.
3. Form B=[A;√αI] and d=[c;0]. Because ||Bw−d||²=||Aw−c||²+α||w||², the augmentation preserves the objective.
4. Use a rank-revealing least-squares primitive to solve for w and recover b=μy−μxᵀw.
5. Check finite state and commit only after the fit succeeds; inference evaluates Qw+b.

In exact arithmetic, the positive-α optimum is unique in w. Extremely weak α relative to feature scale can still fall below floating-point numerical rank resolution; finite precision does not provide an unlimited conditioning guarantee.

## 9. Pseudocode

```text
FIT(X,y,alpha):
  validate alpha >= 0; center using training offsets when requested
  B = vertical_stack(centered_X, sqrt(alpha) * identity(p))
  d = concatenate(centered_y, zeros(p))
  w = LEAST_SQUARES(B,d)
  b = y_offset - X_offset dot w
  check finite results; commit model
```

## 10. Dry Run

Take X=[−1,0,1]ᵀ, y=[−2,0,2]ᵀ, α=2. Both means are zero. The scalar stationarity equation is (XᵀX+α)w=Xᵀy: (2+2)w=4, hence w=1 and b=0. Training residuals are [1,0,−1], so J=½·2+(2/2)·1²=2. Query x=2 predicts 2. Adding 10 to every target changes only the fitted intercept to 10.

## 11. Time Complexity

The augmented matrix has (n+p) rows and p columns. Dense least squares takes O((n+p)p²) work, including O(p³) regularization-row cost; centering/copying adds O(np). Prediction uses O(mp). This educational solver favors numerical clarity over specialized primal/dual choices for very wide problems.

## 12. Space Complexity

The copied design and augmented solve require O(np+p²+n) storage plus decomposition workspace of the same asymptotic order. Fitted coefficients use O(p) and singular diagnostics O(p). Query validation/copy plus predictions require O(mp+m). No training matrix or optimization history is retained after fitting.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `RidgeRegression(alpha=1.0, fit_intercept=True)`. Alpha is finite in [0,10¹²]. Fit returns self; predict returns a 1D float64 array; score returns R². `coef_`, `intercept_`, `rank_`, `singular_values_`, `objective_`, `training_mse_`, `n_iter_=1` and `converged_` describe the successful solve. `loss_gradient` returns the summed objective and gradients Xᵀr+αw and 1ᵀr.

## 14. C++ Implementation

C++ is optional for classical ML and **not implemented** for this topic. There is no dummy C++ source or C++ test. The catalog keeps `cpp_status: planned` as an honest optional deliverable; Python/numerical completion is independent of it. DSA retains mandatory Python/C++ and both C++17/C++20 gates. See the [track policy](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install runtime dependencies with `python -m pip install -r requirements-ml.txt`, then run:

```sh
.venv/bin/python machine-learning/supervised-learning/regression/ridge-regression/python/example.py
```

Expected rounded prediction:

```text
[2.0]
```

The example fits the small training dataset from the dry run and predicts a separate query. Equivalent API code is:

```python
import numpy as np
from solution import RidgeRegression  # run from this topic's python/ directory
X = [[-1.0], [0.0], [1.0]]
y = [-2.0, 0.0, 2.0]
model = RidgeRegression(alpha=2.0).fit(X, y)
print(np.round(model.predict([[2.0]]), 6).tolist())
```

The standalone `solution.py` also accepts one JSON object with `X`, `y`, `predict` and an optional constructor `parameters` object, and returns `{"predictions":[...]}` at full float64 precision. Invalid data or non-convergence produces stderr and exit 2, with no successful prediction JSON. Run tests with `python -m pytest machine-learning/supervised-learning/regression/ridge-regression -q` after installing `requirements-ml-test.txt`.

## 16. Edge Cases

Alpha zero is supported as minimum-norm OLS; duplicate columns are valid. Positive α shrinks a zero-information column to zero. With one observation and a fitted intercept, all coefficients are zero and the intercept equals the target. Negative/nonfinite alpha and non-boolean intercept flags are invalid. Constant features, signed targets and singular designs are tested. Common dimension, magnitude, empty-query and invalid-data behavior is defined by the [ML standard](../../../../docs/ml-development.md).

## 17. Advantages

The objective is convex, predictions are deterministic, and augmented least squares avoids explicit matrix inversion. Regularization can reduce coefficient sensitivity while keeping training/prediction simple. Intercept handling and loss normalization are visible rather than hidden defaults.

## 18. Disadvantages and Limitations

Ridge generally keeps all coefficients nonzero, so it is not a sparse feature selector. The penalty depends on feature units and can introduce bias. Extremely ill-conditioned scales may exceed rank resolution despite positive α. The local reference investigation records why an α=0 rank-deficient scikit-learn Ridge SVD result is not used as a unique off-manifold oracle; minimum-norm OLS is the stated convention. No automatic standardization, weights, multiple outputs or uncertainty estimates are included.

## 19. When to Use It

Use ridge when a linear model is appropriate but correlated predictors or weak singular directions make OLS coefficients unstable. Choose alpha using validation data and report test MSE/MAE/R² separately from training metrics. If scaling is needed, learn its means and scales from training observations alone.

## 20. When Not to Use It

Avoid interpreting a ridge coefficient as a causal effect or treating a larger alpha as universally better. Use Lasso for a sparse coefficient objective, Polynomial Regression for an explicit nonlinear basis, or a tree when piecewise partitions are justified. This implementation is unsuitable for extremely large dense decompositions.

## 21. Comparison With Related Algorithms

| Alternative | Difference |
| --- | --- |
| OLS | No penalty; minimum-norm convention resolves numerical rank deficiency |
| Lasso | L1 penalty, possible exact zeros; mean residual-loss normalization |
| Elastic Net with ratio=0 | Equivalent coefficient objective when Ridge α=n·ElasticNet α |
| Normal-equation inverse | Same symbolic stationary equation, worse conditioning and unnecessary inversion |

## 22. Interview Questions

Why is the intercept unpenalized? Derive the augmented matrix. Explain the effect of feature units. Why can positive alpha still be numerically negligible? How must alpha change when comparing this sum-loss objective with a mean-loss implementation?

## 23. Practice Problems

1. Compute a one-feature ridge solution for two alpha values.
2. Duplicate a column and verify the penalty selects equal weights when appropriate.
3. Use a fixed-seed training/validation/test split to choose alpha without fitting the scaler or hyperparameter on test data.

## 24. References

- [scikit-learn Ridge formulation](https://scikit-learn.org/1.8/modules/linear_model.html#ridge-regression-and-classification).
- [NumPy least squares and numerical rank](https://numpy.org/doc/2.3/reference/generated/numpy.linalg.lstsq.html).

Tests compare positive-alpha predictions with Ridge and use an OLS minimum-norm reference for alpha zero, with the numerical-cutoff discrepancy retained as evidence.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). See [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 13 owner review is pending; implementation and test evidence do not imply owner approval.
