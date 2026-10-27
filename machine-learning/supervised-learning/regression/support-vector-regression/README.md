# Support Vector Regression

## 1. Algorithm Name

**Support Vector Regression** — dense, single-output educational regression. The canonical topic is `support-vector-regression` in B1 Supervised Learning — Regression, Phase 13.

## 2. Overview

Epsilon-SVR fits a function whose deviations inside an epsilon-wide tube incur no loss. Deviations outside it incur linear loss, while a squared function-norm penalty controls complexity. This implementation explicitly solves the convex kernel dual with bounded alternating direction method of multipliers (ADMM); it supports linear and radial-basis-function kernels without delegating to an external estimator.

## 3. Problem Statement

Let X∈Rⁿˣᵖ contain training rows xᵢ, y∈Rⁿ contain real targets, φ be the chosen feature map and Kᵢⱼ=⟨φ(xᵢ),φ(xⱼ)⟩. The primal minimizes P(w,b)=||w||²/2+CΣᵢmax(|⟨w,φ(xᵢ)⟩+b−yᵢ|−ε,0), with C>0 and ε≥0. The dual maximizes D(β)=yᵀβ−βᵀKβ/2−ε||β||₁ subject to Σβᵢ=0 and |βᵢ|≤C. Predict f(x)=Σᵢβᵢk(x,xᵢ)+b. This is summed epsilon-insensitive loss, not squared error or a mean-loss normalization.

## 4. Why Do We Need This Algorithm?

A squared-error fit penalizes every residual and can favor a more complex response to small measurement noise. SVR explicitly trades a tolerance tube against function complexity. Kernels allow a nonlinear predictor without explicitly enumerating its feature map. C, epsilon and kernel scale determine different aspects of that trade-off and require validation.

## 5. Real-World Applications

Examples include a smooth sensor calibration curve or a compact nonlinear baseline on a modest dataset. Linear loss outside the tube differs from squared-error sensitivity, but does not make the estimator immune to outliers or dataset bias. Dense kernel storage and repeated matrix products limit this educational solver to small training sets.

## 6. Core Intuition

Introduce β=α−α* from the upper/lower tube multipliers. Minimizing over the unpenalized intercept gives 1ᵀβ=0; multiplier bounds yield −C≤β≤C. For each β, the least possible α+α* gives |β|, producing the L1 term ε||β||₁. Thus nonsmoothness belongs to the dual even though the kernel quadratic is differentiable. A positive-semidefinite K makes the minimization of −D convex.

## 7. Prerequisites

Know convex quadratic functions, Lagrange multipliers, primal/dual bounds and [Lasso soft thresholding](../lasso-regression/README.md). Linear kernels use xᵀz; RBF uses exp(−γ||x−z||²), with γ>0. NumPy's symmetric eigendecomposition is a numerical primitive for repeated quadratic solves; it does not implement the SVR objective, constraints, threshold update or stopping certificate.

## 8. Step-by-Step Working Process

1. Validate and copy data. Center targets by their training mean; equality 1ᵀβ=0 makes that translation leave the dual problem unchanged. Compute K and its eigendecomposition. Materially negative eigenvalues fail; roundoff-sized negatives are clamped to zero only in the inverse solve.
2. Split β=z. Place the quadratic and equality constraint in β's subproblem and the L1/box terms in z's subproblem. Initialize z=u=0 and choose ADMM penalty ρ>0.
3. Let H=K+ρI, v=H⁻¹(y_centered+ρ(z−u)) and a=H⁻¹1. Set β=v−a(1ᵀv)/(1ᵀa). Inverse application uses eigenvectors/eigenvalues, without forming H⁻¹.
4. Set z=clip(S(β+u,ε/ρ),−C,C), with soft threshold S, then u←u+β−z.
5. Check r=||β−z||₂ and s=ρ||z−z_old||₂ against tol(√n+max(||β||₂,||z||₂)) and tol(√n+||ρu||₂). On passing, project z onto the box/equality intersection by 80-step scalar bisection.
6. For feasible projected coefficients compute residual breakpoints (y_centered−Kβ)±ε. Any intercept in the interval between their two central ordered values minimizes the tube loss; choose its midpoint. Compute primal and dual objectives and require P−D≤tol(1+|P|+|D|). A substantially negative gap is a numerical error. Commit only after all checks, otherwise continue up to max_iter and raise ConvergenceError.

For an exact feasible dual and exact arithmetic, the gap bounds primal suboptimality of this convex problem. Floating-point feasibility, kernel conditioning and approximate solves limit that interpretation. ADMM's convex convergence theory is not a guarantee that every permitted input meets a finite iteration budget.

## 9. Pseudocode

```text
K = kernel(training_X, training_X)
factorize K + rho*I; z = u = zeros(n)
repeat at most max_iter times:
  beta = equality_constrained_quadratic_solve(K, y, z-u, rho)
  old_z = z
  z = clip(soft_threshold(beta+u, epsilon/rho), -C, C)
  u += beta-z
  if primal_and_dual_residuals_small:
    feasible = project_box_and_zero_sum(z)
    b = midpoint_of_central_residual_breakpoints(feasible)
    if numerical_primal_dual_gap_small: commit; return self
raise ConvergenceError
```

## 10. Dry Run

Take x=[−1,0,1], y=[−1,0,1], linear kernel, C=10 and ε=0.1. Symmetry permits b=0. For slopes between zero and 0.9, P(w)=w²/2+20(0.9−w), decreasing up to w=0.9; for w≥0.9 near the optimum the tube loss is zero and the norm grows. Thus w=0.9. A feasible dual β=[−0.45,0,0.45] has zero sum, produces w=Σβᵢxᵢ=0.9 and D=0.9−0.405−0.09=0.405. P=0.405 as well. Query x=2 predicts 1.8. The finite-tolerance numerical test checks this result and its gap independently.

## 11. Time Complexity

Kernel construction costs O(n²p). Dense eigendecomposition costs O(n³); each of T ADMM iterations costs O(n²), and each certificate/projection adds O(n²+n) with a fixed 80 bisection steps. Total O(n²p+n³+Tn²). Query inference costs O(mnp) for either implemented kernel; the code retains every dual coefficient rather than dropping small ones. Linear coef_ is diagnostic and not used to change inference behavior.

## 12. Space Complexity

Training stores O(n²+np) for the kernel, factorization and owned training observations, plus O(n) solver vectors. RBF differences are computed in blocks bounded by the shared cell budget. Fitted state is O(np+n); the factorization is temporary. Prediction blocks queries in groups of 128 and bounds its RBF intermediate. No support-vector binary checkpoint or external dataset is stored.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `SupportVectorRegression(C=1.0, epsilon=0.1, kernel="rbf", gamma=None, rho=1.0, tol=1e-7, max_iter=10000)`. Supported bounds: 0<C≤10⁶, 0≤epsilon≤10¹², gamma None or (0,10¹²], 0<rho≤10⁶, 0<tol≤0.01 and native-integer max_iter in 1..100000. Gamma None means 1/p, not a data-variance heuristic. Fit accepts n≤256, p≤128; predict accepts (m,p), with m≤10000 and the shared cell budget. Inputs are copied float64, finite and |value|≤10¹². Fit returns self. Predict returns shape (m,); score returns R² with constant-target convention 1 for perfect predictions, otherwise 0. There is no random state or automatic scaling.

Inspect full-length `dual_coef_`, scalar `intercept_`, `support_` (indices with |β|>tol, informational only), `n_iter_`, `primal_objective_`, `dual_objective_`, `duality_gap_`, residual diagnostics, `training_mse_` and, for the linear kernel, `coef_`. `smooth_dual_gradient_` is only Kβ−y_centered, excluding nonsmooth terms/constraints. Fitted kernel parameters are captured independently of later constructor-attribute changes.

## 14. C++ Implementation

C++ is optional for classical ML and **not implemented** for this topic. There is no dummy C++ source or C++ test. The catalog keeps `cpp_status: planned` as an honest optional deliverable; Python/numerical completion is independent of it. DSA retains mandatory Python/C++ and both C++17/C++20 gates. See the [track policy](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install runtime dependencies with `python -m pip install -r requirements-ml.txt`, then run:

```sh
.venv/bin/python machine-learning/supervised-learning/regression/support-vector-regression/python/example.py
```

Expected rounded prediction:

```text
[1.8]
```

The example fits the small training dataset from the dry run and predicts a separate query. Equivalent API code is:

```python
import numpy as np
from solution import SupportVectorRegression  # run from this topic's python/ directory
X = [[-1.0], [0.0], [1.0]]
y = [-1.0, 0.0, 1.0]
model = SupportVectorRegression(C=10.0, epsilon=0.1, kernel="linear", tol=1e-9).fit(X, y)
print(np.round(model.predict([[2.0]]), 6).tolist())
```

The standalone `solution.py` also accepts one JSON object with `X`, `y`, `predict` and an optional constructor `parameters` object, and returns `{"predictions":[...]}` at full float64 precision. Invalid data or non-convergence produces stderr and exit 2, with no successful prediction JSON. Run tests with `python -m pytest machine-learning/supervised-learning/regression/support-vector-regression -q` after installing `requirements-ml-test.txt`.

## 16. Edge Cases

Single observations and constant targets can fit an intercept with zero dual coefficients. Duplicate observations are allowed. A sufficiently wide tube can yield zero weights with a nonunique optimal intercept. Empty shaped queries return an empty vector; empty training data fail. Wrong dimensions, nonnumeric/bool/complex values, NaN/Inf, invalid hyperparameters or exceeded budgets raise ValueError. Exhausting iterations raises ConvergenceError and preserves an earlier successful fitted model. RBF squared distances use explicit differences to avoid cancellation at large coordinate offsets; exp of a large negative value legitimately rounds to zero. Overflow, invalid arithmetic, unresolved equality solves and inconsistent certificates fail explicitly.

## 17. Advantages

The essential optimization and constraint logic are visible. Residuals, equality feasibility and a primal/dual objective check provide evidence beyond prediction similarity. Linear and RBF models share the same supervised API, and independent tests compare against analytical solutions and LIBSVM through scikit-learn.

## 18. Disadvantages and Limitations

Dense O(n²) storage and O(n³) factorization are inappropriate for large n. A fixed rho and bounded ADMM can converge slowly on poorly scaled or extreme inputs; rescale or choose a sensible budget rather than accepting a failed fit. Equality projection and the gap are floating-point checks, not interval-arithmetic proofs. Individual dual coefficients and intercepts can be nonunique, so reference tests compare predictions/objectives on suitable data. Only two kernels, no sample weights and no sparse matrices are supported. Kernel scale/C/epsilon selected using test targets would leak evaluation information.

## 19. When to Use It

Use this lesson to study epsilon-insensitive convex regression on small, scaled numerical data. Fit scaling on training rows only; choose C, epsilon and gamma with validation, then report held-out MSE/MAE/R² plus iteration/gap diagnostics. Treat timing as an environment-specific observation.

## 20. When Not to Use It

Do not use the dense solver for a large dataset or assume all allowed magnitudes yield an accurately resolved kernel. A high RBF gamma can nearly isolate samples; a tiny gamma can make the kernel almost constant. Neither a low training loss nor a small duality gap establishes generalization. If the affine baseline is adequate, its direct solve is less expensive.

## 21. Comparison With Related Algorithms

| Alternative | Difference |
| --- | --- |
| Linear Regression | Squared residual loss, direct least squares, no epsilon tube |
| Ridge | Squared loss plus coefficient shrinkage; no L1 dual term |
| RBF versus linear SVR | Changes the feature geometry and inference cost, not the epsilon loss |
| CART Regression | Greedy discontinuous partitions; no convex primal/dual certificate |

## 22. Interview Questions

Derive why a free intercept requires zero-sum dual coefficients. What is the role of epsilon in the z update? Why are ADMM residual checks accompanied by an objective gap? Why can two correct solvers return different intercepts? Explain the difference between a numerical gap and a test-error estimate.

## 23. Practice Problems

1. Verify the dry run's primal and dual values by hand.
2. Keep a fixed synthetic dataset and compare linear/RBF prediction and gap diagnostics over a few gamma values.
3. Standardize a fixed training split, select hyperparameters on validation data and evaluate once on a held-out set. Report non-convergence rather than substituting a partial model.

## 24. References

- [scikit-learn SVR formulation and kernel discussion](https://scikit-learn.org/1.8/modules/svm.html#regression).
- [Boyd et al.: Distributed Optimization and Statistical Learning via ADMM](https://web.stanford.edu/~boyd/papers/admm_distr_stats.html).

Reference predictions align C, epsilon, kernel and numeric gamma; ADMM and LIBSVM need not have identical iterations or dual coefficients. Finite differences test only the differentiable dual quadratic; feasibility and gap tests cover the nonsmooth constrained solution.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). See [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 13 owner review is pending; implementation and test evidence do not imply owner approval.
