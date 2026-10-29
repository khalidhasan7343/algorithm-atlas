# AdaBoost — discrete multiclass SAMME

## 1. Algorithm Name

AdaBoost — discrete multiclass SAMME

## 2. Overview

A sequential classifier that fits weighted weak trees, measures weighted classification errors and increases the relative importance of misclassified examples. The implemented variant is discrete multiclass SAMME with a finite perfect-learner convention and log-domain example weights.

## 3. Problem Statement

Input X has shape (n,p), y shape (n,). Numeric fitting is bounded to 512 rows and 32 features; CatBoost has its stricter 64-row/8-feature limits. Regression is finite scalar float64. Classifiers preserve sorted homogeneous int64/string labels. Empty prediction matrices are supported; empty fitting data is rejected. See the complete [shared contracts](../../../docs/ensemble-methods-conventions.md) for exact ranges, atomic fit state, seed behavior, factory protocols and metric conventions.

Public model(s): `AdaBoostClassifier`. Fitting constructs an ensemble; inference predicts one scalar or original class label per query row. Supported classification probabilities have one column per fitted sorted class.

## 4. Why Do We Need This Algorithm?

Unweighted shallow trees may repeatedly neglect difficult observations. AdaBoost directs later learners toward errors of previous rounds while retaining a weighted vote over all accepted learners. This is a different source of diversity from independent bootstrap sampling.

## 5. Real-World Applications

A tabular multiclass recognition exercise can use shallow trees as weak rules and inspect which misclassified observations gain weight across rounds. This is useful for studying margins and sensitivity to corrupted labels. Treat any application with noisy labels as a separate held-out robustness study; sequential reweighting does not certify reliable deployment.

## 6. Core Intuition

For K classes and normalized weights w, compute e=sum_i w_i*1[h(x_i)!=y_i]. For 0<e<1-1/K, choose alpha=eta*(log((1-e)/e)+log(K-1)). Add alpha to the log weight of every misclassified example, subtract a common offset and normalize before fitting the next tree.

For multiclass SAMME the chance boundary is 1-1/K. The score-softmax output here is softmax(v_k/((K-1)*sum(alpha))), with v_k the weighted vote. It preserves the vote argmax but is an uncalibrated score transform. For binary unshrunk rounds alpha=log((1-e)/e); the equivalent signed-classifier coefficient uses half that value because only errors are upweighted in this formulation.

## 7. Prerequisites

Required: NumPy arrays, training versus test separation, probability/means, decision-tree partitions and finite-precision arithmetic. Read [ML development](../../../docs/ml-development.md), [Regression metrics](../../../docs/regression-evaluation.md) and [Classification contracts](../../../docs/classification-conventions.md). Algorithm-specific prerequisites include sampling, weighted counts and deterministic class ordering.

## 8. Step-by-Step Working Process

1. Validate at least two sorted classes, eta in (0,1], tree depth 1..4, round count and optional sample weights.
2. Scale finite nonnegative weights by their maximum, then normalize; preserve zeros as negative-infinite log weights.
3. Fit a fresh weighted-Gini weak tree and compute weighted error using the current normalized weights.
4. Reject a first learner at/worse than chance with ValueError; after accepted rounds, stop without adding the chance learner.
5. If e=0, append the learner with alpha=1 and stop, avoiding log(0).
6. Otherwise compute SAMME alpha with log1p(-e)-log(e), record the pre-round weights and reweight errors in log space.
7. Predict by weighted class votes; expose every accepted prefix through staged_predict.

The stored state follows the prediction formula above. All training is bounded, uses local RNGs and publishes fitted attributes only on successful completion.

## 9. Pseudocode

```text
log_w <- log(normalized positive input weights), zeros=-infinity
for round in 1..T:
    w <- normalized exp(log_w-max(log_w))
    h <- weighted_tree.fit(X, y, w)
    e <- weighted misclassification error
    if e >= 1-1/K: reject first learner or stop later
    if e == 0: append(h,1); stop
    alpha <- eta*(log1p(-e)-log(e)+log(K-1))
    append(h,alpha); log_w[wrong] += alpha
    log_w -= max(log_w)
predict <- largest accumulated class vote
```

## 10. Dry Run

For X=[0,1,2,3] and labels=[cold,cold,warm,warm], uniform weights are 1/4.
A depth-one weighted tree splits at 1.5 and has e=0. The implementation retains
it with finite alpha=1 and stops after one learner. Queries [0,3] return
["cold","warm"]. In the independent nonperfect four-row oracle, e=1/4 gives
alpha=eta*log(3); multiplying only wrong-example weights by exp(alpha) reproduces
the stored next-round normalization.

## 11. Time Complexity

For T accepted rounds, n rows, p features, d weak depth and K classes, the exhaustive weighted-tree bound is O(T*p*n²*d), with O(Tn) reweighting. Prediction costs O(T*q*d+T*q*K) for q queries. Stopping early at perfect/chance learners reduces executed rounds; there is no universal convergence-rate promise. Best/average runtime depends on early stops and data-dependent partitions; no universal average-case speed or wall-clock bound is asserted.

## 12. Space Complexity

Stores O(T*min(n,2^d)*K) tree values and O(Tn) recorded weight history. Current log weights use O(n), class vote output O(qK), and recursion O(d). The diagnostics are intentionally retained for mathematical review.

## 13. Python Implementation

The working from-scratch source is [python/solution.py](python/solution.py); [python/example.py](python/example.py) is executable. Public APIs are `AdaBoostClassifier`, with fit/predict/score and the task-specific methods above. Core training uses NumPy/local code, never scikit-learn. B3 [support](../support.py) reuses canonical B1/B2 contracts and metrics; [tree.py](../tree.py) is explicit ensemble infrastructure. Factory defaults reuse canonical models rather than copying their solvers. Runtime dependencies come from [requirements-ml.txt](../../../requirements-ml.txt).

## 14. C++ Implementation

Classical ML uses the Python-first policy: optional C++ is **not implemented** for this topic. There are no dummy C++ source/test files. Existing DSA Python/C++ and C++17/C++20 requirements remain mandatory and unchanged.

## 15. Input and Output Examples

From the repository root with the ML test environment installed:

```sh
python machine-learning/ensemble-methods/adaboost/python/example.py
```

The dataset, hyperparameters, seed and executed output are explained in the dry run. The same reusable API can be called as:

```python
# From this topic's python directory
from solution import AdaBoostClassifier
model = AdaBoostClassifier(**{'n_estimators': 3, 'random_state': 0})
model.fit([[0], [1], [2], [3]], ['cold', 'cold', 'warm', 'warm'])
predictions = model.predict([[0], [3]])
```

The JSON CLI accepts X, y, predict and optional parameters. It prints a predictions object; invalid input exits 2 with stderr and no prediction JSON. Factory callables are Python API configuration, not JSON-serializable CLI parameters.

## 16. Edge Cases

Zero sample weights remain zero; all-zero, negative, infinite and NaN weights fail. Extreme finite weight sums are normalized safely by scaling first. Chance guard uses 10^-14 tolerance. A perfect learner never receives infinite weight. If no weak learner beats chance, fitting fails transactionally; later chance failure leaves accepted rounds as a fitted ensemble.

Do not mutate public parameters during inference. Caller arrays and global RNG state are preserved. Unsupported sample weights raise TypeError except where explicitly supported. Nonfinite/ambiguous shapes and predict-before-fit raise clear errors; extreme unresolved float64 operations fail rather than returning a fabricated success.

## 17. Advantages

Shows how sequential weighting changes the training objective seen by a weak learner; accepted errors, alphas, weights and staged outputs are inspectable. Multiclass labels retain original identities.

## 18. Disadvantages and Limitations

Sensitive to label noise and outliers repeatedly misclassified. Bounded rounds do not ensure generalization. Extremely small normalized weights can underflow to zero. No SAMME.R, calibrated probabilities, arbitrary weak-learner injection or regression variant is claimed. A perfect learner has the explicit finite-weight convention rather than an infinite theoretical limit.

The [shared contracts](../../../docs/ensemble-methods-conventions.md) state numerical/resource limits and exact unsupported features. Scores and probability outputs are educational model quantities, not calibrated guarantees. A larger ensemble need not improve held-out error.

## 19. When to Use It

Use for compact discrete multiclass demonstrations where shallow weighted trees beat chance and round-by-round error emphasis can be inspected.

## 20. When Not to Use It

Avoid if weak learners cannot beat chance, labels are heavily corrupted, calibrated probabilities are required or class/feature counts exceed documented caps.

## 21. Comparison With Related Algorithms

| Method | Update |
| --- | --- |
| AdaBoost SAMME | Reweight examples; weighted classifier votes |
| GBM squared loss | Fit negative-gradient residual values |
| Bagging | Independent bootstrap fits; no sequential weights |

## 22. Interview Questions

1. Why does multiclass SAMME include log(K-1)?
2. What happens at zero error and at chance error?
3. Derive the error-only weight update from a binary signed update.
4. Why do normalized score probabilities need not be calibrated?

## 23. Practice Problems

1. Hand-compute one round with e=1/4 and eta=1/2.
2. Show why zero weights remain zero under log updates.
3. Inspect staged training accuracy and compare it with held-out accuracy without assuming monotonicity.

For validation run:

```sh
python -m pytest machine-learning/ensemble-methods/adaboost -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
```

The independent oracles use hand calculations, exhaustive candidates or separately fitted references. Marker selections overlap; do not sum them as disjoint counts. Seeds, small datasets and explicit tolerances make failures reproducible. Full DSA regression also runs with `--require-cpp`.

## 24. References

[Zhu et al., Multi-class AdaBoost (2009)](https://doi.org/10.4310/SII.2009.v2.n3.a8); [scikit-learn AdaBoost](https://scikit-learn.org/1.8/modules/ensemble.html#adaboost).

These primary references identify the mathematical method; the exact implemented subset and limits are stated here. External implementations may differ in split ties, random stream consumption, optimization or supported features; reference tests align compatible settings rather than asserting universal equivalence.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE) · [Contribution guidance](../../../CONTRIBUTING.md). This lesson belongs to authorized Phase 15 B3; its new review approval remains pending.
