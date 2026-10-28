# Logistic Regression

## 1. Algorithm Name

**Logistic Regression**, canonical `logistic-regression` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

Logistic Regression is a binary probabilistic classifier with an affine log-odds model. It estimates a probability through the sigmoid, then applies an explicit threshold to choose one of the original labels. This implementation teaches stable cross-entropy, its gradient/Hessian and Newton optimization with bounded backtracking; it does not call an external estimator.

## 3. Problem Statement

Let X∈Rⁿˣᵖ, let tᵢ∈{0,1} encode two sorted original classes, and let zᵢ=xᵢᵀw+b. Define σ(z)=1/(1+exp(−z)). Minimize J(w,b)=Σᵢlog(1+exp(−(2tᵢ−1)zᵢ))/n+α||w||²/2, α≥0. The optional intercept is unpenalized. Predict the second sorted class when z≥0 (equivalently probability≥0.5), including exact ties. Only binary classification is implemented; no one-vs-rest or softmax multiclass claim is made.

## 4. Why Do We Need This Algorithm?

A continuous regression prediction is not automatically a valid class probability. The sigmoid maps an affine score into [0,1], and binary cross-entropy corresponds to a Bernoulli likelihood. A regularized linear baseline can be easier to inspect and evaluate than a nonlinear model, although the assumed log-odds relationship and the dataset still constrain its usefulness.

## 5. Real-World Applications

Examples include a baseline for a two-outcome measured response or studying how numerical features change conditional class odds. Probabilities allow log-loss evaluation in addition to accuracy, but a fitted logistic model is not automatically well calibrated on a changed population. Correlated inputs, class imbalance and an unsuitable threshold can affect practical decisions.

## 6. Core Intuition

The derivative of mean cross-entropy is Xᵀ(σ(z)−t)/n and the intercept derivative is mean(σ(z)−t). Add αw only to the coefficient gradient. The Hessian is Aᵀdiag(σ(z)σ(−z))A/n+diag(penalty), with augmented A containing a bias column if needed. Nonnegative curvature makes the objective convex. Positive α regularizes coefficients, while unregularized separable data can lack a finite optimum.

## 7. Prerequisites

Know matrix products, binary cross-entropy, gradients, positive-semidefinite Hessians, Newton directions and train/test separation. [Linear Regression](../../regression/linear-regression/README.md) illustrates affine predictors with a different objective. [Support Vector Machines](../support-vector-machines/README.md) use margins and hinge loss rather than a probabilistic likelihood.

## 8. Step-by-Step Working Process

1. Validate/copy X and homogeneous labels; require exactly two classes. Encode the sorted classes as 0 and 1.
2. When fitting an intercept, center features by their training mean and append a column of ones. This is a reparameterization, not variance scaling. Initialize parameters at zero and leave the bias penalty zero.
3. Compute loss with logaddexp(0,−signed_target·logit). Evaluate σ separately for nonnegative and negative logits so exponentials never overflow. For positive targets use residual −σ(−z), avoiding cancellation in σ(z)−1.
4. If the infinity norm of the centered-coordinate gradient is ≤tol, recover the original-coordinate intercept and commit model state.
5. Solve H·direction≈gradient with NumPy least squares. This is a numerical linear-algebra primitive; the logistic objective, derivatives and optimization logic are implemented here. If the direction is not descending, use a normalized gradient direction.
6. Try step=1 and halve at most 60 times until Armijo decrease Jnew≤Jold−10⁻⁴·step·gradientᵀdirection holds. Record the accepted objective. Repeat up to max_iter; failure raises ConvergenceError without replacing a prior fit.

The gradient tolerance is measured in centered coordinates and is not an absolute coefficient-error or generalization bound. Convexity does not guarantee a particular finite iteration count on arbitrary scaling.

## 9. Pseudocode

```text
encode two sorted classes; make centered/augmented design A
parameters = zeros; history = [objective(parameters)]
for iteration in 0..max_iter:
  compute stable sigmoid residual, gradient and Hessian
  if max(abs(gradient)) <= tol: recover intercept; commit; return
  if iteration == max_iter: break
  direction = least_squares(Hessian, gradient)
  if not descent: direction = normalized_gradient
  backtrack at most 60 halvings until Armijo decrease
  accept parameters and append objective, otherwise fail
raise ConvergenceError
```

## 10. Dry Run

Consider a constant feature with 20 labels: 15 "no" and 5 "yes". Centering makes the coefficient zero. The intercept optimum has σ(b)=5/20=1/4, hence b=log((1/4)/(3/4))=log(1/3)≈−1.098612. The predicted probabilities are [0.75,0.25], and the selected class is "no". This is independently tested. The runnable example instead uses x=[−2,−1,1,2], labels [cold,cold,warm,warm] and α=0.1; symmetry yields intercept zero and a positive slope, so queries −3 and 3 predict cold and warm.

## 11. Time Complexity

For T accepted iterations and p features, building the Hessian costs O(np²) and a dense least-squares solve O(p³). Up to 60 bounded line-search evaluations add O(np) each. Total O(T(np²+p³)) with the fixed backtracking bound; inference costs O(mp). Computing a full Newton Hessian is intentionally limited to modest dense feature counts.

## 12. Space Complexity

Fit uses O(np+p²+n+T) space for copied/centered data, the Hessian, vectors and objective history. The fitted model retains O(p+T) and no training rows. Predict creates a checked O(mp) query copy plus O(m) scores or O(2m) probabilities. There is no recursion, dataset download or binary model artifact.

## 13. Python Implementation

`LogisticRegression(alpha=1.0, fit_intercept=True, tol=1e-8, max_iter=100)` exposes fit, decision_function, predict_proba, predict and accuracy score. Alpha is in [0,10⁶], tol in (0,0.01], and max_iter is a native integer in 1..10000. Boolean intercept control is strict. X has n≤2048, p≤128 and at most 262144 cells; queries have m≤10000 under the same cell limit. Values are finite real float64-compatible numbers with magnitude≤10¹². Labels are homogeneous int64-compatible integers or nonempty strings, never coerced mixed types; exactly two unique labels are required. Fitted classes_ determines probability columns, coef_ has shape(p,), intercept_ is scalar, decision_function returns(m,), predict_proba returns(m,2), predict returns original labels. Diagnostics include n_iter_, objective_, loss_history_, gradient_norm_ and converged_. No automatic variance scaling or sample weights.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/logistic-regression/python/example.py
```

Expected output:

```text
['cold', 'warm']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import LogisticRegression
X = [[-2.0], [-1.0], [1.0], [2.0]]
y = ["cold", "cold", "warm", "warm"]
model = LogisticRegression(alpha=0.1).fit(X, y)
print(model.predict([[-3.0], [3.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/logistic-regression -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

Constant features, class imbalance and repeated observations are permitted. Wrong shapes, one/three classes, bool/float/mixed labels, nonfinite values and budget violations raise ValueError. Empty shaped queries return empty outputs; score on empty labels is undefined and rejected. Predict-before-fit raises ValueError. Large logits can yield exact numerical probabilities zero/one without overflow. Exhausted iterations or backtracking raise ConvergenceError and preserve the previous model. External mutation of caller arrays does not change fitted coefficients.

## 17. Advantages

A compact linear probability model with a visible objective, independently checked derivatives, deterministic optimization and explicit convergence evidence. The intercept is unpenalized; centering helps large feature offsets. Probability-column order and the equality threshold are unambiguous.

## 18. Disadvantages and Limitations

Only binary, dense numerical data are supported. Newton steps cost more than simple gradient steps when p is large. Collinearity and poor scaling can slow or numerically destabilize fitting; alpha zero on separable data has no finite minimizer in general. A small gradient does not certify calibration, fairness or held-out accuracy. Coefficient penalties depend on feature units. Very large offsets can lose prediction precision when recovering an original-coordinate intercept.

## 19. When to Use It

Use it as a binary supervised baseline when affine log odds are plausible. Fit scaling only on training data; tune alpha and decision thresholds with validation data. Report held-out accuracy, class-ordered confusion matrix, precision/recall/F1 and log loss alongside convergence diagnostics. A class imbalance can make accuracy alone misleading.

## 20. When Not to Use It

Do not send multiclass labels to this binary estimator or treat its scores as causal effects. Do not select alpha on held-out test targets or accept an unconverged fit. If the response depends on sharply nonlinear regions, compare a permitted classifier with that representation; model choice is an empirical question on a defined evaluation protocol.

## 21. Comparison With Related Algorithms

| Related classifier | Difference |
| --- | --- |
| Linear SVM | Hinge loss and margins; no calibrated probability output here |
| KNN | Local stored-neighbor votes rather than learned affine log odds |
| Gaussian NB | Generative independent-feature Gaussian likelihoods |
| LDA | Shared-covariance Gaussian assumptions produce linear scores |

## 22. Interview Questions

Derive the sigmoid residual gradient and Hessian. Why is the intercept unpenalized? Explain why stable signed log-loss is preferable to taking logs of rounded probabilities. What happens to unregularized parameters on separable data? Why is the stopping tolerance coordinate-dependent?

## 23. Practice Problems

1. Derive the constant-feature intercept for three class ratios.
2. Finite-difference the smooth objective at a moderate random coefficient vector.
3. Use a fixed train/validation/test split to select alpha without test leakage, report class-specific metrics and inspect whether log-loss and accuracy favor the same choice.

## 24. References

- [scikit-learn Logistic Regression formulation](https://scikit-learn.org/1.8/modules/linear_model.html#logistic-regression).
- [NumPy logaddexp numerical primitive](https://numpy.org/doc/2.3/reference/generated/numpy.logaddexp.html).

Reference tests align summed-versus-mean penalty scaling with C=1/(n·alpha); alpha zero uses the reference's explicit unregularized convention. They compare probabilities, not optimizer iteration counts.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
