# Polynomial Regression

## 1. Algorithm Name

**Polynomial Regression** — dense, single-output educational regression. The canonical topic is `polynomial-regression` in B1 Supervised Learning — Regression, Phase 13.

## 2. Overview

Polynomial Regression is linear regression in a nonlinear feature basis. This implementation constructs all multivariate monomials of total degree 1 through d, then explicitly reuses the canonical Linear Regression estimator. The power enumeration and fitted basis belong here; the least-squares solver is not copied into a second canonical directory.

## 3. Problem Statement

For input x∈Rᵖ, construct φ(x) containing x₀,…,xₚ₋₁ and every product of total degree up to d. Fit f(x)=b+φ(x)ᵀw by ordinary least squares. A separate optional intercept supplies the degree-zero term; the expansion itself has no constant column. The number of expanded features is q=binom(p+d,d)−1. Dense single-target inputs and float64 predictions follow the shared ML contract.

## 4. Why Do We Need This Algorithm?

An affine model may underfit smooth curved relationships. A small polynomial basis can represent curvature and interactions while preserving a convex least-squares fit in the coefficients. Increasing degree creates capacity and conditioning costs; it is not an automatic improvement in held-out error.

## 5. Real-World Applications

Examples include a modest response-surface model or a controlled calibration curve over a bounded physical range. Interaction terms can represent how two measured inputs jointly affect a response. Extrapolating a high-degree polynomial outside the training range is particularly unreliable, even if training residuals are tiny.

## 6. Core Intuition

A curve in the original input can be a plane in feature space: one-feature degree-two regression uses [x,x²]. For two features, the deterministic order is [x₀,x₁,x₀²,x₀x₁,x₁²]. Enumerating combinations with replacement includes each monomial once; exponent vectors retained in `powers_` define exactly the same transformation at inference.

## 7. Prerequisites

Know [Linear Regression](../linear-regression/README.md), exponent rules, combinations with replacement, and the bias/variance tradeoff. The code uses NumPy numerical primitives and Python's combinatorial enumeration. It does not call scikit-learn PolynomialFeatures or a pipeline during fitting.

## 8. Step-by-Step Working Process

1. Validate p≤32, degree d in 1..8, numeric input and target shapes.
2. Compute q combinatorially before allocating the expanded matrix; reject q>512 or n·q>262144.
3. Enumerate index combinations in increasing total degree and lexicographic index order. Convert each into an exponent vector and evaluate its monomial.
4. Validate expanded values as finite and within the supported magnitude. Fit the canonical OLS model on the expanded training design.
5. Store an owned power matrix and fitted OLS state only after successful fitting. Transform and predict new rows with that stored basis; do not relearn a basis from query data.

The fit is convex in w after fixing the basis, although polynomial dependence on x is nonlinear. Choice of degree is a model-selection decision, not a convergence parameter.

## 9. Pseudocode

```text
FIT(X,y,d):
  q = binomial(p+d,d) - 1; reject excessive expansion
  powers = []
  for order in 1..d:
    for index_tuple in combinations_with_replacement(0..p-1, order):
      append counts(index_tuple) to powers
  Z[i,j] = product over k of X[i,k] ** powers[j,k]
  linear_model = canonical_OLS.fit(Z,y)
  store powers and linear_model
PREDICT(Q): return linear_model.predict(expand(Q, stored_powers))
```

## 10. Dry Run

With X=[−2,−1,0,1,2]ᵀ and y=[4,1,0,1,4]ᵀ, degree two creates rows [x,x²]. The two columns are [−2,−1,0,1,2]ᵀ and [4,1,0,1,4]ᵀ. OLS gives coefficients [0,1] and intercept 0, within rounding. Query x=3 expands to [3,9] and predicts 9. For two original features, `powers_` is [[1,0],[0,1],[2,0],[1,1],[0,2]].

## 11. Time Complexity

Let q=binom(p+d,d)−1. Straight exponent-vector evaluation costs O(nqp), counting each bounded-degree power as constant work; enumerating powers costs O(q(p+d)). The OLS fit adds O(nq·min(n,q)). Transforming m queries costs O(mqp), and linear evaluation adds O(mq). Combinatorial growth of q is the main practical limit. Resource checks precede expansion allocation.

## 12. Space Complexity

Training uses O(nq+qp+np) arrays plus the OLS decomposition workspace. Fitted storage includes O(qp) exponent vectors, O(q) coefficients and O(min(n,q)) diagnostics in the reused model. Prediction/transform return O(mq) expanded values and O(m) predictions; the cell budget also applies at inference. The original training observations are not retained.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `PolynomialRegression(degree=2, fit_intercept=True)`, `fit`, `transform`, `predict` and inherited R² `score`. `transform` requires a fitted model and returns the monomial matrix; it is not a standalone unfitted feature-generator API. State includes `powers_`, `n_features_in_`, `n_output_features_`, expanded-basis `coef_`, `intercept_`, numerical rank and condition diagnostics. `fit` returns self. Coefficients refer to the stored monomial order, not the original raw feature list.

## 14. C++ Implementation

C++ is optional for classical ML and **not implemented** for this topic. There is no dummy C++ source or C++ test. The catalog keeps `cpp_status: planned` as an honest optional deliverable; Python/numerical completion is independent of it. DSA retains mandatory Python/C++ and both C++17/C++20 gates. See the [track policy](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install runtime dependencies with `python -m pip install -r requirements-ml.txt`, then run:

```sh
.venv/bin/python machine-learning/supervised-learning/regression/polynomial-regression/python/example.py
```

Expected rounded prediction:

```text
[9.0]
```

The example fits the small training dataset from the dry run and predicts a separate query. Equivalent API code is:

```python
import numpy as np
from solution import PolynomialRegression  # run from this topic's python/ directory
X = [[-2.0], [-1.0], [0.0], [1.0], [2.0]]
y = [4.0, 1.0, 0.0, 1.0, 4.0]
model = PolynomialRegression(degree=2).fit(X, y)
print(np.round(model.predict([[3.0]]), 6).tolist())
```

The standalone `solution.py` also accepts one JSON object with `X`, `y`, `predict` and an optional constructor `parameters` object, and returns `{"predictions":[...]}` at full float64 precision. Invalid data or non-convergence produces stderr and exit 2, with no successful prediction JSON. Run tests with `python -m pytest machine-learning/supervised-learning/regression/polynomial-regression -q` after installing `requirements-ml-test.txt`.

## 16. Edge Cases

Degree one reduces to ordinary linear regression. Duplicate or constant inputs can make the expanded design singular; the reused minimum-norm convention applies. Empty queries with the correct original column count are valid. Invalid degree, unexpected feature count, nonfinite/magnitude-exceeding powers or a combinatorial expansion beyond the budget are rejected. A failed fit preserves a previously successful basis and predictions.

## 17. Advantages

Explicit, inspectable interaction terms; deterministic feature order; one canonical least-squares implementation; and a worked bridge between linear models and nonlinear inputs. A fixed basis preserves direct-solve behavior without stochastic optimization or a learning rate.

## 18. Disadvantages and Limitations

Monomials can become highly correlated and poorly scaled. Increasing degree can overfit and amplify noise or extrapolation error. This implementation does not automatically normalize features or regularize expanded coefficients. Input and expanded-feature magnitude are both capped at 10¹²; finite raw inputs are not a promise that every expansion is supported. Sparse expansion, splines and orthogonal polynomial bases are outside this lesson.

## 19. When to Use It

Use a low degree when curvature or interactions are justified and the feature count remains modest. Fit any original-feature scaling on training data, then use the same scaling for validation/test rows. Select degree using validation error and retain a separate test evaluation.

## 20. When Not to Use It

Do not keep raising degree to force interpolation on noisy data. Use a different basis for unstable extrapolation, a regularized model when coefficient variance dominates, or a tree for supported piecewise behavior. Avoid the dense combinatorial expansion for hundreds of raw columns.

## 21. Comparison With Related Algorithms

| Related model | Relationship |
| --- | --- |
| OLS | Exactly the fitting core reused after expansion |
| Ridge | Can regularize an expanded basis, but that variant is not silently substituted here |
| Kernel SVR | Defines nonlinear similarity without exposing these monomial coefficients |
| CART Regression | Learns axis-aligned partitions instead of a globally specified basis |

## 22. Interview Questions

Why is this model linear in its fitted parameters? Derive the feature-count formula. Why omit the bias column when fitting a separate intercept? Explain why preprocessing query data independently would change the intended model. What causes a Vandermonde-like basis to become ill-conditioned?

## 23. Practice Problems

1. Fit y=1+2x+x² on five training points and verify a held-out point.
2. For two features and degree three, list exponent vectors and verify their count.
3. Compare degrees on a fixed train/validation/test split, reporting training and test errors separately and explaining rank deficiency or overfitting.

## 24. References

- [scikit-learn polynomial regression explanation](https://scikit-learn.org/1.8/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions).
- [PolynomialFeatures ordering and feature count](https://scikit-learn.org/1.8/modules/generated/sklearn.preprocessing.PolynomialFeatures.html).
- [Canonical Linear Regression](../linear-regression/README.md), reused directly by this implementation.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). See [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 13 owner review is pending; implementation and test evidence do not imply owner approval.
