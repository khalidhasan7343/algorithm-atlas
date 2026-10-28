# Support Vector Machines

## 1. Algorithm Name

**Support Vector Machines**, canonical `support-vector-machines` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

A soft-margin SVM fits a separating hyperplane by trading squared coefficient norm against hinge loss. This implementation solves the binary linear C-SVM dual using bounded ADMM, checks dual feasibility and a primal/dual gap, and returns signed margins. It is not an SVR with thresholded predictions and does not produce calibrated probabilities.

## 3. Problem Statement

Encode the two sorted original classes as sᵢ∈{−1,+1}. For n×p X, coefficient w and free intercept b, minimize P(w,b)=||w||²/2+CΣᵢmax(0,1−sᵢ(xᵢᵀw+b)), C>0. The dual maximizes D(a)=Σaᵢ−½aᵀQa, with Qᵢⱼ=sᵢsⱼxᵢᵀxⱼ, 0≤aᵢ≤C and Σsᵢaᵢ=0. Recover w=Σaᵢsᵢxᵢ. Predict the second sorted class when margin xᵀw+b≥0, including exact ties. Only binary linear classification is supported; no kernel, multiclass or probability-calibration claim is made.

## 4. Why Do We Need This Algorithm?

A separating rule should account for both errors and geometric margin. Hinge loss penalizes observations with signed margin below one, while the coefficient norm controls hyperplane scale. The dual exposes which observations contribute to that rule and permits a meaningful numerical gap check instead of treating an iteration budget as convergence.

## 5. Real-World Applications

Examples include a small scaled-feature classification baseline or studying maximum-margin geometry on synthetic data. Linear margins are interpretable scores relative to a fitted hyperplane, not probabilities or universal confidence estimates. C and feature units influence the resulting boundary and require training/validation evaluation.

## 6. Core Intuition

Introducing slack for violated margins and minimizing the Lagrangian over the free intercept yields the signed zero-sum equality; minimizing over w yields the dual quadratic. Complementarity gives margin≥1 when a=0, margin=1 for 0<a<C, and margin≤1 when a=C, within numerical tolerance. These conditions differ from epsilon-SVR's tube and L1 dual term.

## 7. Prerequisites

Know convex quadratic objectives, hinge loss, Lagrange duality, support vectors and ADMM variable splitting. [Logistic Regression](../logistic-regression/README.md) uses a Bernoulli likelihood and probabilities. [SVR](../../regression/support-vector-regression/README.md) is a distinct regression objective, not the implementation of this classifier.

## 8. Step-by-Step Working Process

1. Validate/copy X and require exactly two classes. Center training features; the equality Σsᵢaᵢ=0 makes the recovered w invariant to this translation, while b is recovered afterward.
2. Form Q on centered features and eigendecompose it. Materially negative eigenvalues fail; roundoff-sized negatives are clamped only for repeated inverse application of H=Q+rho·I. NumPy supplies that numerical primitive; the SVM objective, constraint and updates remain explicit.
3. Split a=z. Let v=H⁻¹(1+rho(z−u)), q=H⁻¹s. The equality-constrained quadratic step is a=v−q(sᵀv)/(sᵀq). Update z=clip(a+u,0,C), then u←u+a−z.
4. Check ||a−z||₂≤tol(√n+max(||a||₂,||z||₂)) and rho||z−z_old||₂≤tol(√n+||rho·u||₂). On passing, project z onto the box/signed-equality intersection using 80 scalar bisection steps.
5. Recover w. For fixed w, hinge-loss breakpoints for b are sᵢ−xᵢᵀw. With nplus positive labels, choose the midpoint of sorted breakpoint positions nplus−1 and nplus (zero-based), which minimizes total hinge loss over b.
6. Calculate P,D and require P−D≤tol(1+|P|+|D|), rejecting a substantially negative numerical gap. Commit only after these checks. Otherwise continue to max_iter and raise ConvergenceError.

For exact feasible dual variables and exact arithmetic, the convex gap bounds primal suboptimality. Floating-point projection/conditioning limits this numerical certificate; ADMM theory does not promise a fixed finite iteration count for every allowed input.

## 9. Pseudocode

```text
encode signed labels; center X; form Q; factor Q+rho*I
z = u = zeros(n)
repeat up to max_iter:
  a = equality_constrained_quadratic_solve(Q, signed_labels, z-u)
  old_z = z; z = clip(a+u, 0, C); u += a-z
  if primal_and_dual_residuals_small:
    feasible_a = project_box_signed_equality(z)
    w = centered_X.T @ (signed_labels*feasible_a)
    b = central_hinge_breakpoint_interval_midpoint(w)
    if numerical_primal_dual_gap_small: recover original b; commit; return
raise ConvergenceError
```

## 10. Dry Run

Use x=[−2,−1,1,2], s=[−1,−1,+1,+1], C=1. The optimum has w=1,b=0 and signed margins [2,1,1,2]. Feasible dual a=[0,1/2,1/2,0] has signed sum zero and w=Σaᵢsᵢxᵢ=1. P=||w||²/2=1/2 because hinge loss is zero. D=Σaᵢ−||w||²/2=1−1/2=1/2, so the exact gap is zero. The two inner observations are support vectors. Queries −3 and 3 produce original labels −1 and +1.

## 11. Time Complexity

Forming Q costs O(n²p), dense eigendecomposition O(n³), and T ADMM iterations O(Tn²), including bounded projection/certificate work. Total O(n²p+n³+Tn²). Inference uses the recovered linear coefficients in O(mp), unlike a kernel classifier that sums over stored support vectors. Dense factorization is why training is capped at 256 rows.

## 12. Space Complexity

Training uses O(n²+np+n) for the quadratic, factorization, copied features and solver vectors. Fitted diagnostics retain O(n+p+sp) including full dual coefficients and s stored support-vector rows. Prediction needs O(mp+m), with no kernel matrix. No external model checkpoint or third-party classifier is loaded.

## 13. Python Implementation

`SupportVectorMachine(C=1.0, rho=1.0, tol=1e-7, max_iter=20000)` exposes fit, decision_function, predict and accuracy score. C/rho lie in (0,10⁶], tol in (0,0.01], max_iter is a native integer in 1..100000. Training limits: n≤256,p≤64; shared 262144-cell/|feature|≤10¹² limits and query m≤10000 apply. Labels are exactly two homogeneous int64-compatible integers or nonempty strings. classes_ maps negative/positive margins; coef_ is(p,), intercept_ scalar, margins(m,), original predictions(m,). Inspect alpha_, full-length dual_coef_=s*a, support_ (a>tol), support_vectors_, training_margin_, n_iter_, primal/dual objectives, duality_gap_, residuals and equality_residual_. Support thresholding is informational; w uses all feasible coefficients. There is deliberately no predict_proba.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/support-vector-machines/python/example.py
```

Expected output:

```text
[-1, 1]
```

Equivalent API code, run from this topic's python directory:

```python
from solution import SupportVectorMachine
X = [[-2.0], [-1.0], [1.0], [2.0]]
y = [-1, -1, 1, 1]
model = SupportVectorMachine().fit(X, y)
print(model.predict([[-3.0], [3.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/support-vector-machines -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

Constant features, contradictory duplicates and imbalanced classes are valid soft-margin problems; a free intercept can favor the majority. Nonunique optimal bias intervals can lead correct solvers to different margins. Empty shaped queries work. Wrong dimensions, more/fewer than two classes, bool/float/mixed labels, nonfinite input and exceeded budgets raise ValueError. Failed or exhausted refits preserve earlier successful state. Centering helps offsets but final original-coordinate prediction can still lose precision for extreme scales. Fixed-rho ADMM may require rescaling or a different configured iteration budget.

## 17. Advantages

A visible margin/hinge formulation with support-vector diagnostics, exact small-solution tests and both feasibility and gap evidence. Linear inference is compact and fast. Deterministic initialization and updates make experiments reproducible without global RNG mutation.

## 18. Disadvantages and Limitations

Binary linear models only, dense small-n factorization, no weights or calibration. Ill conditioning can weaken floating-point equality/gap interpretation or prevent convergence. Support coefficients and bias may be nonunique, so comparisons must align objective and account for ties. A small optimization gap is not a held-out error or fairness guarantee.

## 19. When to Use It

Use it to study soft margins on modest scaled numerical data. Fit scaling on training rows only, select C on validation data and evaluate accuracy/confusion/precision/recall/F1 on a held-out split. Report convergence and numerical gap along with classification metrics; do not invent log loss for this nonprobabilistic API.

## 20. When Not to Use It

Do not feed multiclass labels or expect nonlinear kernel behavior. Do not interpret a signed margin as a calibrated posterior. Avoid using a partially converged solution as a successful classifier or assuming a fixed C has the same meaning after changing feature units.

## 21. Comparison With Related Algorithms

| Model | Different objective/output |
| --- | --- |
| Logistic Regression | Mean cross-entropy, L2 alpha, meaningful modeled probabilities |
| SVR | Epsilon-insensitive regression tube and different dual |
| CART | Greedy partitions with empirical class frequencies |
| Kernel SVM | Nonlinear feature geometry; intentionally unsupported here |

## 22. Interview Questions

Derive the signed equality from the intercept. Explain each support-vector complementarity case. Why is residual stopping accompanied by a gap? How can the optimal intercept be nonunique? What is the difference between a margin, a duality gap and a held-out classification error?

## 23. Practice Problems

1. Verify the dry-run primal and dual values and identify free support vectors.
2. Add a contradictory duplicate observation and inspect which coefficients reach C.
3. Compare validation-selected Logistic/SVM models on a fixed split without requiring identical predictions or claiming universal superiority.

## 24. References

- [scikit-learn C-SVM primal/dual formulation](https://scikit-learn.org/1.8/modules/svm.html#mathematical-formulation).
- [Boyd et al., ADMM](https://web.stanford.edu/~boyd/papers/admm_distr_stats.html).

Reference tests match linear kernel, C and tight solver tolerance, compare suitable margins/predictions and separately check support/equality/box/gap conditions.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
