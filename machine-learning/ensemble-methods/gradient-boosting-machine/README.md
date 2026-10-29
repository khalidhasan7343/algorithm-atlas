# Gradient Boosting Machine — squared-error regression

## 1. Algorithm Name

Gradient Boosting Machine — squared-error regression

## 2. Overview

Build an additive scalar regression model by fitting shallow trees to negative gradients of half squared loss. Initialization is the training-target mean and every accepted stage is shrunk by a fixed learning rate. This lesson implements squared-error regression only.

## 3. Problem Statement

Input X has shape (n,p), y shape (n,). Numeric fitting is bounded to 512 rows and 32 features; CatBoost has its stricter 64-row/8-feature limits. Regression is finite scalar float64. Classifiers preserve sorted homogeneous int64/string labels. Empty prediction matrices are supported; empty fitting data is rejected. See the complete [shared contracts](../../../docs/ensemble-methods-conventions.md) for exact ranges, atomic fit state, seed behavior, factory protocols and metric conventions.

Public model(s): `GradientBoostingRegressor`. Fitting constructs an ensemble; inference predicts one scalar or original class label per query row. Supported classification probabilities have one column per fitted sorted class.

## 4. Why Do We Need This Algorithm?

A shallow tree can leave systematic residual structure. Additive correction can increase capacity gradually while learning rate and depth control the scale and complexity of each stage. Later stages fit what the current model has not explained, rather than independent copies of the original target.

## 5. Real-World Applications

For small scalar prediction exercises such as synthetic demand or energy measurements, additive trees can represent step changes and nonlinear interactions left by an initial mean. Residual histories show what each stage explains. The implemented IID split experiment is not a temporal validation or a forecasting guarantee.

## 6. Core Intuition

For L=1/2*sum_i(y_i-F_i)^2, derivative with respect to F_i is F_i-y_i. The negative gradient is the ordinary residual r_i=y_i-F_i. A squared-error tree approximates this residual; F_next=F+eta*h. Mean-leaf fitting is the least-squares projection on a chosen tree partition.

The mean minimizes constant half squared loss. On a fixed partition, a residual mean minimizes each leaf quadratic. For an exact least-squares projection h and eta in (0,1], this correction cannot increase the training quadratic in exact arithmetic. Float64 roundoff and bounded greedy structure limit numerical claims; test error has no monotonicity guarantee.

## 7. Prerequisites

Required: NumPy arrays, training versus test separation, probability/means, decision-tree partitions and finite-precision arithmetic. Read [ML development](../../../docs/ml-development.md), [Regression metrics](../../../docs/regression-evaluation.md) and [Classification contracts](../../../docs/classification-conventions.md). Algorithm-specific prerequisites include gradients and loss minimization.

## 8. Step-by-Step Working Process

1. Validate numeric single-output data and bounded tree/round/learning-rate parameters.
2. Initialize F0=mean(y), preserving exactly constant targets without rounded-mean artifacts.
3. Compute residual vector r=y-F before each stage; stop if every residual is exactly zero.
4. Fit a fresh squared-error tree to r, subject to depth and leaf constraints.
5. Add eta*h(X) to the training prediction and verify finite values.
6. Record residual and training MSE histories. Publish all fitted trees and the fitted learning rate transactionally.
7. At inference start with F0 and apply the same trees in order; staged_predict yields copies after each tree.

The stored state follows the prediction formula above. All training is bounded, uses local RNGs and publishes fitted attributes only on successful completion.

## 9. Pseudocode

```text
F <- constant mean(y)
for t in 1..T:
    r <- y-F
    if every r == 0: stop
    h[t] <- squared_error_tree.fit(X,r)
    F <- F+eta*h[t](X)
predict(query) <- mean(y)+eta*sum_t h[t](query)
```

## 10. Dry Run

With X=[0,1,2,3], y=[0,0,4,4], depth=1, eta=1/2 and three rounds,
F0=[2,2,2,2]. Residuals [-2,-2,2,2] are represented exactly by a split at 1.5.
The endpoint predictions progress [1,3], [0.5,3.5], [0.25,3.75]. The executed
example prints [0.25,3.75]. This arithmetic is also checked by an independent
stage oracle and finite differences of the stated loss.

## 11. Time Complexity

With T rounds, n rows, p features, depth d and q query rows, exhaustive residual-tree fitting has conservative O(T*p*n²*d) time; residual updates add O(Tn). Inference costs O(T*q*d). A constant target stops before fitting any tree. No histogram optimization or stochastic subsampling is implemented. Best/average runtime depends on early stops and data-dependent partitions; no universal average-case speed or wall-clock bound is asserted.

## 12. Space Complexity

Tree storage is O(T*min(n,2^d)); retained residual history adds O(Tn), and loss history O(T). A staged prediction needs O(q) mutable work and returns a fresh O(q) vector. Recursion is bounded by d.

## 13. Python Implementation

The working from-scratch source is [python/solution.py](python/solution.py); [python/example.py](python/example.py) is executable. Public APIs are `GradientBoostingRegressor`, with fit/predict/score and the task-specific methods above. Core training uses NumPy/local code, never scikit-learn. B3 [support](../support.py) reuses canonical B1/B2 contracts and metrics; [tree.py](../tree.py) is explicit ensemble infrastructure. Factory defaults reuse canonical models rather than copying their solvers. Runtime dependencies come from [requirements-ml.txt](../../../requirements-ml.txt).

## 14. C++ Implementation

Classical ML uses the Python-first policy: optional C++ is **not implemented** for this topic. There are no dummy C++ source/test files. Existing DSA Python/C++ and C++17/C++20 requirements remain mandatory and unchanged.

## 15. Input and Output Examples

From the repository root with the ML test environment installed:

```sh
python machine-learning/ensemble-methods/gradient-boosting-machine/python/example.py
```

The dataset, hyperparameters, seed and executed output are explained in the dry run. The same reusable API can be called as:

```python
# From this topic's python directory
from solution import GradientBoostingRegressor
model = GradientBoostingRegressor(**{'n_estimators': 3, 'learning_rate': 0.5, 'max_depth': 1, 'random_state': 0})
model.fit([[0], [1], [2], [3]], [0, 0, 4, 4])
predictions = model.predict([[0], [3]])
```

The JSON CLI accepts X, y, predict and optional parameters. It prints a predictions object; invalid input exits 2 with stderr and no prediction JSON. Factory callables are Python API configuration, not JSON-serializable CLI parameters.

## 16. Edge Cases

A constant target produces only the exact constant initializer and an empty stage iterator. Constant features produce constant residual leaves. Tiny target units are normalized locally inside tree split scoring. Bad learning rates, nonfinite data and incompatible query features fail; previous fitted state survives a failed refit.

Do not mutate public parameters during inference. Caller arrays and global RNG state are preserved. Unsupported sample weights raise TypeError except where explicitly supported. Nonfinite/ambiguous shapes and predict-before-fit raise clear errors; extreme unresolved float64 operations fail rather than returning a fabricated success.

## 17. Advantages

Directly connects functional-gradient descent to residual fitting, with simple inspectable training loss and stage histories. Shrinkage and shallow trees give clear capacity controls.

## 18. Disadvantages and Limitations

Only scalar squared loss is supported: no classification, logistic updates, sample weights, early-stopping validation or missing/sparse data. Bounded stage count can underfit, large capacity can overfit, and greedy trees do not extrapolate smoothly outside observed ranges.

The [shared contracts](../../../docs/ensemble-methods-conventions.md) state numerical/resource limits and exact unsupported features. Scores and probability outputs are educational model quantities, not calibrated guarantees. A larger ensemble need not improve held-out error.

## 19. When to Use It

Use for controlled tabular regression examples where residual structure is nonlinear and additive stage behavior is the learning objective.

## 20. When Not to Use It

Avoid for discrete classification labels requiring a classification loss, sparse/missing data, production-scale throughput or linear extrapolation requirements.

## 21. Comparison With Related Algorithms

| Method | Training signal / tree objective |
| --- | --- |
| GBM here | First-order residuals, squared-error leaves |
| XGBoost here | Gradients/Hessians, regularized Newton leaves and split gain |
| AdaBoost | Weighted misclassification error and class votes |

## 22. Interview Questions

1. Differentiate half squared loss with respect to a prediction.
2. Why is the optimal constant initialization the mean?
3. Why does shrinkage change the stage trajectory?
4. Why does training improvement not prove test improvement?

## 23. Practice Problems

1. Reproduce the three-stage endpoint predictions by hand.
2. Replace the target with a constant and explain the empty stage iterator.
3. Use a fixed held-out split to compare depths one and three without tuning on test data.

For validation run:

```sh
python -m pytest machine-learning/ensemble-methods/gradient-boosting-machine -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
```

The independent oracles use hand calculations, exhaustive candidates or separately fitted references. Marker selections overlap; do not sum them as disjoint counts. Seeds, small datasets and explicit tolerances make failures reproducible. Full DSA regression also runs with `--require-cpp`.

## 24. References

[Friedman, Greedy Function Approximation (2001)](https://doi.org/10.1214/aos/1013203451); [scikit-learn gradient boosting](https://scikit-learn.org/1.8/modules/ensemble.html#gradient-boosting).

These primary references identify the mathematical method; the exact implemented subset and limits are stated here. External implementations may differ in split ties, random stream consumption, optimization or supported features; reference tests align compatible settings rather than asserting universal equivalence.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE) · [Contribution guidance](../../../CONTRIBUTING.md). This lesson belongs to authorized Phase 15 B3; its new review approval remains pending.
