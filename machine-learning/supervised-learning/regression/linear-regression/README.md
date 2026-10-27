# Linear Regression

## 1. Algorithm Name

**Linear Regression** — dense, single-output educational regression. The canonical topic is `linear-regression` in B1 Supervised Learning — Regression, Phase 13.

## 2. Overview

Ordinary least squares (OLS) estimates a continuous target as an affine function of numerical features. This implementation handles dense, single-output data and uses a rank-revealing least-squares primitive rather than forming an inverse. Learning the model means choosing coefficients from the training observations; inference then evaluates the fitted affine function on new rows.

## 3. Problem Statement

Let X be an n×p real design matrix, y an n-vector, w a p-vector and b an intercept. Minimize J(w,b)=||Xw+b1−y||²/(2n). `fit_intercept=True` leaves b free; False fixes b=0. Return a fitted estimator, with `coef_.shape==(p,)`, scalar `intercept_`, and `predict(X_new).shape==(m,)`. The least-squares answer need not interpolate noisy data. If centered columns are dependent, choose minimum-norm coefficients under NumPy's numerical rank cutoff; this is not the minimum norm of the combined (b,w) vector.

## 4. Why Do We Need This Algorithm?

A fitted line gives a compact numerical baseline, separates training from prediction and makes residual structure visible. It provides an interpretable reference before regularization or nonlinear expansion. A low training error alone does not establish that the relationship will generalize; a held-out error and the collection process still matter.

## 5. Real-World Applications

Examples include estimating a physical response over a restricted operating range, explaining associations among measured variables, or building a baseline for demand prediction. A coefficient is conditional on the supplied features and units. Observational regression does not by itself establish causation, and extrapolation beyond the observed range may be poor.

## 6. Core Intuition

The residual r=Xw+b1−y measures each prediction error. At a smooth optimum, Xᵀr=0 and, when an intercept is fitted, 1ᵀr=0. The prediction vector is the projection onto the affine model space. Collinear columns can produce many coefficient vectors with the same fitted predictions; selecting a minimum-norm representative makes the choice deterministic within numerical precision.

## 7. Prerequisites

Understand vectors, matrix multiplication, derivatives of quadratic functions, rank, singular values, and training/test separation. [Ridge Regression](../ridge-regression/README.md) adds a coefficient penalty; [Polynomial Regression](../polynomial-regression/README.md) changes the feature basis. Python needs NumPy; scikit-learn is used only by independent tests.

## 8. Step-by-Step Working Process

1. Validate two-dimensional X and one-dimensional y without guessing reshapes.
2. If fitting b, compute training means μx and μy, then A=X−1μxᵀ and c=y−μy1. Otherwise use zero offsets.
3. Solve min ||Aw−c||² with `numpy.linalg.lstsq(A,c,rcond=None)`. Its decomposition and rank cutoff are numerical linear algebra primitives; centering, objective, state and prediction are model logic here.
4. Recover b=μy−μxᵀw. Verify finite coefficients and training predictions before updating estimator state.
5. Retain rank and singular-value diagnostics. Predict using the fitted coefficients and intercept, without refitting on query rows.

The quadratic is convex. Exact-arithmetic least squares has a global optimum; floating-point rank decisions and ill conditioning limit numerical coefficient accuracy. An iterative convergence claim is unnecessary because this fit is a direct solve.

## 9. Pseudocode

```text
FIT(X,y):
  validate dense real arrays and dimensions
  offsets = training means if fitting intercept, otherwise zero
  A = X - X_offset; c = y - y_offset
  w, rank, singular_values = LEAST_SQUARES(A,c)
  b = y_offset - X_offset dot w
  check finite parameters/predictions; commit owned fitted state
PREDICT(Q): validate columns; return Q dot w + b
```

## 10. Dry Run

For X=[0,1,2]ᵀ and y=[1,3,5]ᵀ, μx=1 and μy=3. Centering gives A=[−1,0,1]ᵀ and c=[−2,0,2]ᵀ. AᵀA=2 and Aᵀc=4, so w=2; recover b=3−1·2=1. A query x=3 predicts 7, while training residuals and training MSE are zero. These scalar normal-equation calculations explain the answer; the production solver does not invert AᵀA.

## 11. Time Complexity

For n samples and p features, dense rank-revealing least squares costs O(np·min(n,p)) arithmetic work; centering and training predictions cost O(np). Prediction costs O(mp) for m new rows. Validation and copying also scan the arrays. No iteration-count bound is involved. These are dense floating-point operation bounds, not a constant-cost claim for arbitrary data sizes.

## 12. Space Complexity

Training owns O(np+n) copied/centered input and the decomposition requires O(np+min(n,p)²) workspace up to the numerical library's implementation. Fitted model storage is O(p), plus O(min(n,p)) singular diagnostics. Prediction uses O(mp+m) including its validated copy and returned values. Training data are not retained by the fitted linear estimator.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `LinearRegression(fit_intercept=True)`, `fit`, `predict` and `score` (R²). Fit returns self. Attributes include `coef_`, `intercept_`, `rank_`, `singular_values_`, `condition_number_`, `training_mse_`, `n_iter_=1` and `converged_=True` after a successful direct solve. An infinite condition diagnostic marks deficient numerical rank, not a nonfinite prediction. `loss_gradient` returns half mean squared loss, its coefficient gradient and intercept gradient for mathematical inspection.

## 14. C++ Implementation

C++ is optional for classical ML and **not implemented** for this topic. There is no dummy C++ source or C++ test. The catalog keeps `cpp_status: planned` as an honest optional deliverable; Python/numerical completion is independent of it. DSA retains mandatory Python/C++ and both C++17/C++20 gates. See the [track policy](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install runtime dependencies with `python -m pip install -r requirements-ml.txt`, then run:

```sh
.venv/bin/python machine-learning/supervised-learning/regression/linear-regression/python/example.py
```

Expected rounded prediction:

```text
[7.0]
```

The example fits the small training dataset from the dry run and predicts a separate query. Equivalent API code is:

```python
import numpy as np
from solution import LinearRegression  # run from this topic's python/ directory
X = [[0.0], [1.0], [2.0]]
y = [1.0, 3.0, 5.0]
model = LinearRegression().fit(X, y)
print(np.round(model.predict([[3.0]]), 6).tolist())
```

The standalone `solution.py` also accepts one JSON object with `X`, `y`, `predict` and an optional constructor `parameters` object, and returns `{"predictions":[...]}` at full float64 precision. Invalid data or non-convergence produces stderr and exit 2, with no successful prediction JSON. Run tests with `python -m pytest machine-learning/supervised-learning/regression/linear-regression -q` after installing `requirements-ml-test.txt`.

## 16. Edge Cases

A single observation with a fitted intercept produces zero coefficients and that observation's target as intercept. Constant centered columns receive zero minimum-norm coefficients. Duplicate columns are allowed; coefficients are not uniquely identifiable before the numerical convention is chosen. Underdetermined systems are valid. Predict-before-fit, ambiguous shapes, mismatched columns, complex/bool/string arrays, NaN/Inf and resource-limit violations raise ValueError. Empty query arrays with shape (0,p) return an empty vector; empty training data are invalid.

## 17. Advantages

A direct, deterministic numerical baseline with no learning rate or random seed to tune. The intercept is unpenalized, rank deficiency is explicit, and SVD-based least squares avoids squaring the condition number as normal-equation inversion would. Coefficients and residual orthogonality can be checked independently.

## 18. Disadvantages and Limitations

OLS does not enforce sparsity, monotonicity, causality or robustness to outliers. Weak singular directions can make coefficients sensitive even when predictions on observed data are stable. Centering helps offsets but cannot recover information already lost when large, nearly equal values were rounded. Feature magnitude/resource caps and checked numerical failure are documented in the [ML standard](../../../../docs/ml-development.md). There is no automatic scaling, imputation or statistical inference interval.

## 19. When to Use It

Use it as a supervised continuous-target baseline when an affine relationship is plausible and residual analysis is meaningful. Keep a held-out set for evaluation; fit any scaling on training data only. Investigate rank diagnostics before interpreting a coefficient as an independent effect.

## 20. When Not to Use It

Do not use this estimator for categorical prediction, missing-data imputation, a nonlinear boundary without an appropriate basis, or claims of causal identification. If correlated features cause unstable weights, examine Ridge; if a low-degree polynomial is justified, compare Polynomial Regression on held-out data.

## 21. Comparison With Related Algorithms

| Method | Change relative to OLS |
| --- | --- |
| Ridge | Penalizes squared coefficients, stabilizing small singular directions |
| Lasso | Uses an L1 penalty that can set coefficients exactly to zero |
| Polynomial Regression | Expands features, then reuses this OLS model |
| Decision Tree Regression | Learns piecewise-constant partitions instead of one affine function |

## 22. Interview Questions

Why does centering let us avoid penalizing an intercept? When are coefficients unique? Why can two correct solvers disagree on collinear coefficients? Why is a small residual not a generalization guarantee? Explain why normal-equation inversion can be less stable than a decomposition.

## 23. Practice Problems

1. Derive the fitted slope and intercept for three non-collinear one-feature observations.
2. Duplicate a feature and verify identical predictions but nonunique mathematical coefficients.
3. Create a fixed-seed train/test split with irrelevant columns, compare held-out MSE, and explain any increase without looking at test targets during fitting.

## 24. References

- [NumPy least-squares primitive and rank convention](https://numpy.org/doc/2.3/reference/generated/numpy.linalg.lstsq.html).
- [scikit-learn Linear Models: OLS formulation and limitations](https://scikit-learn.org/1.8/modules/linear_model.html#ordinary-least-squares).
- [NumPy numerical condition number](https://numpy.org/doc/2.3/reference/generated/numpy.linalg.cond.html).

The implementation uses NumPy linear algebra, not scikit-learn fitting. Reference tests align intercept and minimum-norm conventions.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). See [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 13 owner review is pending; implementation and test evidence do not imply owner approval.
