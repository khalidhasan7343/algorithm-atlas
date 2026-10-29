# XGBoost — exact regularized second-order regression

## 1. Algorithm Name

XGBoost — exact regularized second-order regression

## 2. Overview

An educational dense exact-split implementation of the regularized Newton tree objective used by XGBoost. It implements half squared regression loss, L2 leaf penalties, a per-split gamma cost, minimum Hessian mass, row subsampling and per-tree feature subsampling. It does not wrap the XGBoost package.

## 3. Problem Statement

Input X has shape (n,p), y shape (n,). Numeric fitting is bounded to 512 rows and 32 features; CatBoost has its stricter 64-row/8-feature limits. Regression is finite scalar float64. Classifiers preserve sorted homogeneous int64/string labels. Empty prediction matrices are supported; empty fitting data is rejected. See the complete [shared contracts](../../../docs/ensemble-methods-conventions.md) for exact ranges, atomic fit state, seed behavior, factory protocols and metric conventions.

Public model(s): `XGBoostRegressor`. Fitting constructs an ensemble; inference predicts one scalar or original class label per query row. Supported classification probabilities have one column per fitted sorted class.

## 4. Why Do We Need This Algorithm?

First-order residual fitting does not by itself express the regularized second-order tree objective. Explicit gradients, Hessians and a penalty on leaf scores provide a principled formula for optimal leaf values and whether an extra leaf is worthwhile.

## 5. Real-World Applications

A bounded numeric tabular regression experiment can study how L2 penalties shrink leaf adjustments and how gamma prevents weak splits. Inspecting Hessian mass and gain is useful when comparing regularized model capacity on synthetic noisy targets. This implementation teaches the objective rather than supplying production-scale distributed analytics.

## 6. Core Intuition

For a leaf with summed gradient G and Hessian H, minimize G*w+1/2*(H+lambda)*w². Setting its derivative to zero gives w*=-G/(H+lambda). Substituting yields -G²/(2*(H+lambda)). Compare parent and child scores and subtract gamma for the extra leaf. For the supported loss g=F-y and h=1.

Split gain is 1/2*[G_L²/(H_L+lambda)+G_R²/(H_R+lambda)-G²/(H+lambda)]-gamma. Lambda>=0 shrinks leaf scores; gamma>=0 discourages extra leaves. Child Hessian mass is sample count only for this squared-loss implementation. Shrinkage is applied after unshrunk surrogate split selection, so the reported gain is not a held-out performance guarantee.

## 7. Prerequisites

Required: NumPy arrays, training versus test separation, probability/means, decision-tree partitions and finite-precision arithmetic. Read [ML development](../../../docs/ml-development.md), [Regression metrics](../../../docs/regression-evaluation.md) and [Classification contracts](../../../docs/classification-conventions.md). Algorithm-specific prerequisites include gradients and loss minimization.

## 8. Step-by-Step Working Process

1. Validate finite numeric regression data, eta, lambda, gamma, child mass, depth and sampling fractions.
2. Initialize prediction with the training-target mean; exact constant targets require no trees.
3. Compute all current gradients F-y and Hessians one, then sample rows and tree-level columns without replacement.
4. At each node sum gradients/Hessians and compute the regularized leaf score.
5. Enumerate midpoint splits in the sampled tree columns; reject children with insufficient Hessian mass.
6. Pick the greatest resolved positive gain, recurse under the depth bound or retain the Newton leaf.
7. Add the shrunk tree output to every training row. Store gradients, row/column samples, losses and tree sufficient statistics.
8. Predict from the fitted mean plus the fitted learning rate times the ordered tree sum.

The stored state follows the prediction formula above. All training is bounded, uses local RNGs and publishes fitted attributes only on successful completion.

## 9. Pseudocode

```text
F <- mean(y)
for t in 1..T:
    g <- F-y; h <- ones(n)
    rows, columns <- seeded samples without replacement
    grow node with G=sum(g), H=sum(h):
        leaf_value <- -G/(H+lambda)
        split <- best positive regularized gain with child H>=minimum
        recurse if eligible and below depth limit
    F <- F+eta*tree[t](X)
predict <- initial_mean+eta*sum(tree outputs)
```

## 10. Dry Run

For y=[0,0,4,4], F0=2 gives g=[2,2,-2,-2]. At threshold 1.5,
G_L=4, G_R=-4 and H_L=H_R=2. With lambda=2, leaves are -1 and +1.
The unpenalized split gain is 1/2*(16/4+16/4)=4; gamma=1/4 leaves gain 3.75.
With eta=1/2, endpoint predictions become [1.5,2.5], matching the executable
example. Independent tests enumerate every candidate gain and finite-difference
the first and second prediction derivatives.

## 11. Time Complexity

Let T be rounds, n rows, p columns, r sampled rows, k sampled tree columns and d depth. Exhaustive partition evaluation gives conservative O(T*k*r²*d+T*n*d) fit time, including whole-training prediction updates. Query prediction costs O(T*q*d). This is exact midpoint search, not histogram/quantile/distributed XGBoost. Best/average runtime depends on early stops and data-dependent partitions; no universal average-case speed or wall-clock bound is asserted.

## 12. Space Complexity

Stores O(T*min(r,2^d)) Newton nodes, O(Tr) sampled indices, O(Tk) sampled columns and O(Tn) gradient history. Each node records G,H,gain and scalar value. Temporary gradients/Hessians require O(n); recursion O(d).

## 13. Python Implementation

The working from-scratch source is [python/solution.py](python/solution.py); [python/example.py](python/example.py) is executable. Public APIs are `XGBoostRegressor`, with fit/predict/score and the task-specific methods above. Core training uses NumPy/local code, never scikit-learn. B3 [support](../support.py) reuses canonical B1/B2 contracts and metrics; [tree.py](../tree.py) is explicit ensemble infrastructure. Factory defaults reuse canonical models rather than copying their solvers. Runtime dependencies come from [requirements-ml.txt](../../../requirements-ml.txt).

## 14. C++ Implementation

Classical ML uses the Python-first policy: optional C++ is **not implemented** for this topic. There are no dummy C++ source/test files. Existing DSA Python/C++ and C++17/C++20 requirements remain mandatory and unchanged.

## 15. Input and Output Examples

From the repository root with the ML test environment installed:

```sh
python machine-learning/ensemble-methods/xgboost/python/example.py
```

The dataset, hyperparameters, seed and executed output are explained in the dry run. The same reusable API can be called as:

```python
# From this topic's python directory
from solution import XGBoostRegressor
model = XGBoostRegressor(**{'n_estimators': 1, 'learning_rate': 0.5, 'max_depth': 1, 'reg_lambda': 2, 'random_state': 0})
model.fit([[0], [1], [2], [3]], [0, 0, 4, 4])
predictions = model.predict([[0], [3]])
```

The JSON CLI accepts X, y, predict and optional parameters. It prints a predictions object; invalid input exits 2 with stderr and no prediction JSON. Factory callables are Python API configuration, not JSON-serializable CLI parameters.

## 16. Edge Cases

No valid positive gain yields a Newton leaf rather than a fabricated split. Large gamma or child mass can prevent splitting. Exact constant targets stop before tree fitting. Row/column fractions in (0,1] use ceil and select at least one element. Extremely tiny gradient-square gains can underflow or be below the relative float64 threshold; such unresolved splits stop.

Do not mutate public parameters during inference. Caller arrays and global RNG state are preserved. Unsupported sample weights raise TypeError except where explicitly supported. Nonfinite/ambiguous shapes and predict-before-fit raise clear errors; extreme unresolved float64 operations fail rather than returning a fabricated success.

## 17. Advantages

Exposes regularization, second-order sufficient statistics and exact gains, making a central XGBoost mechanism independently checkable. Sampling and stage diagnostics are retained.

## 18. Disadvantages and Limitations

No L1 penalty, arbitrary loss, classification, ranking, sparse/default routing, missing values, histograms, GPU, DART, distributed training or production feature/API parity. Tiny split gains can be unresolved; half squared loss and unit Hessians are fixed. Model size and inference grow with rounds/depth.

The [shared contracts](../../../docs/ensemble-methods-conventions.md) state numerical/resource limits and exact unsupported features. Scores and probability outputs are educational model quantities, not calibrated guarantees. A larger ensemble need not improve held-out error.

## 19. When to Use It

Use to study Newton leaves, regularized gain and sampling on small scalar-regression examples.

## 20. When Not to Use It

Avoid when the full production framework, categorical processing, classification/ranking loss, missing-value routing or large data are needed.

## 21. Comparison With Related Algorithms

| Method | Leaf update / split criterion |
| --- | --- |
| GBM squared loss | Residual means, unregularized SSE |
| XGBoost here | -G/(H+lambda), regularized second-order gain |
| CatBoost here | Ordered prefix residuals, symmetric trees, ordered categorical statistics |

## 22. Interview Questions

1. Derive the optimal regularized leaf value.
2. Why is one extra gamma subtracted for a binary split?
3. Why is min_child_weight not generally the same as row count?
4. How do shrinkage and the unshrunk split objective differ?

## 23. Practice Problems

1. Recalculate the worked split for lambda=0 and lambda=10.
2. Choose gamma large enough to block it.
3. At lambda=gamma=0 and full sampling, compare predictions with a compatible external squared-loss GBM.

For validation run:

```sh
python -m pytest machine-learning/ensemble-methods/xgboost -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
```

The independent oracles use hand calculations, exhaustive candidates or separately fitted references. Marker selections overlap; do not sum them as disjoint counts. Seeds, small datasets and explicit tolerances make failures reproducible. Full DSA regression also runs with `--require-cpp`.

## 24. References

[Chen and Guestrin, XGBoost (2016)](https://arxiv.org/abs/1603.02754); [official tree objective tutorial](https://xgboost.readthedocs.io/en/stable/tutorials/model.html).

These primary references identify the mathematical method; the exact implemented subset and limits are stated here. External implementations may differ in split ties, random stream consumption, optimization or supported features; reference tests align compatible settings rather than asserting universal equivalence.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE) · [Contribution guidance](../../../CONTRIBUTING.md). This lesson belongs to authorized Phase 15 B3; its new review approval remains pending.
