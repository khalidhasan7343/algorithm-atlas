# Stacking — out-of-fold stacked generalization

## 1. Algorithm Name

Stacking — out-of-fold stacked generalization

## 2. Overview

Train a separate meta-estimator on out-of-fold predictions from independently fitted bases, then refit deployment bases on the full training data. Regression uses prediction columns; classification uses aligned class probability blocks. The meta-model never trains on the same bases' in-sample predictions.

## 3. Problem Statement

Input X has shape (n,p), y shape (n,). Numeric fitting is bounded to 512 rows and 32 features; CatBoost has its stricter 64-row/8-feature limits. Regression is finite scalar float64. Classifiers preserve sorted homogeneous int64/string labels. Empty prediction matrices are supported; empty fitting data is rejected. See the complete [shared contracts](../../../docs/ensemble-methods-conventions.md) for exact ranges, atomic fit state, seed behavior, factory protocols and metric conventions.

Public model(s): `StackingClassifier / StackingRegressor`. Fitting constructs an ensemble; inference predicts one scalar or original class label per query row. Supported classification probabilities have one column per fitted sorted class.

## 4. Why Do We Need This Algorithm?

A learned combination can use relationships among diverse predictions that a fixed vote misses. Training the combiner on in-sample predictions can instead reward memorization. Out-of-fold construction makes every meta-training row come from a base fit excluding that observation.

## 5. Real-World Applications

For an IID tabular prediction exercise with enough rows per class, combine linear/tree regressors or likelihood/tree classifiers using out-of-fold features. Row-membership diagnostics demonstrate that the meta-model did not see in-sample base predictions. Time-ordered or grouped applications require a suitable different fold design; the implemented shuffled/stratified folds are not such a design.

## 6. Core Intuition

Partition training rows into F folds. For each fold fit every base on its complement and write predictions only to held-out rows of the OOF matrix. After each row is written exactly once, train the meta-estimator on that matrix and original targets. Finally refit fresh base instances on all rows for inference.

Let z_i concatenate predictions h_b^(-fold(i))(x_i). The meta learner fits y from Z=[z_i], with each row excluded from the training of its generating bases. Inference uses newly fitted full-data bases to construct z(x). Defaults use canonical Ridge(alpha=1) for regression and regularized Gaussian NB for classification; the latter is a documented probabilistic meta-model, not logistic stacking.

## 7. Prerequisites

Required: NumPy arrays, training versus test separation, probability/means, decision-tree partitions and finite-precision arithmetic. Read [ML development](../../../docs/ml-development.md), [Regression metrics](../../../docs/regression-evaluation.md) and [Classification contracts](../../../docs/classification-conventions.md). Algorithm-specific prerequisites include cross-validation and a separately trained meta-estimator.

## 8. Step-by-Step Working Process

1. Validate two to eight folds, one to eight factories, targets and seed. Classification has at most eight classes with at least F observations each.
2. Shuffle each class independently into stratified folds, or shuffle regression rows into K-fold parts. Save held-out indices.
3. For each fold and base create a fresh seeded estimator; fit only complement rows and predict the held-out cohort.
4. Regression writes one column per base. Classification aligns all global probability columns and writes one K-column block per base.
5. Assert every row has exactly one held-out write; fit a new meta-estimator on copied OOF features and original labels/targets.
6. Fit fresh deployment bases on full training data. Retain fold models only as audit diagnostics.
7. At inference concatenate full-data base predictions in the identical block order and pass them to the fitted meta-estimator.

The stored state follows the prediction formula above. All training is bounded, uses local RNGs and publishes fitted attributes only on successful completion.

## 9. Pseudocode

```text
Z <- empty OOF matrix; count <- zeros(n)
for held_out in folds:
    train <- all rows except held_out
    for each base b:
        model <- fresh factory(seed).fit(X[train],y[train])
        Z[held_out, block(b)] <- aligned predictions on X[held_out]
    count[held_out] += 1
assert every count == 1
meta <- fresh final_factory(seed).fit(Z,y)
deployment_bases <- fresh factories fitted on all training rows
predict <- meta(concatenated deployment-base predictions)
```

## 10. Dry Run

For X=[0,1,2,3], y=[0,0,4,4], two folds and seed 0, held-out sets are
[0,2] and [1,3]. Default OLS/tree bases give OOF rows [-2,0], [2,0], [2,0],
[6,4]. Centering and Ridge(alpha=1) yield coefficients [80/173,8/173] and
intercept 178/173. Full-data bases predict [-0.4,0] and [4.4,4] at queries
0 and 3. Therefore meta predictions are 146/173 and 562/173, approximately
[0.8439306358381503,3.2485549132947975]. The example verifier uses these independently
derived rational values, not the implementation as its own oracle.

## 11. Time Complexity

With B bases, F folds and training cost C_b(n), fit time is sum_b[F*C_b(n*(F-1)/F)+C_b(n)] plus meta fitting on n by B (regression) or BK (classification) features. Query cost is the deployment base sum plus meta inference. Retained fold models are not used at deployment. The default exhaustive trees have their documented bounded cost. Best/average runtime depends on early stops and data-dependent partitions; no universal average-case speed or wall-clock bound is asserted.

## 12. Space Complexity

OOF storage is O(nB) or O(nBK). Retaining fold diagnostics uses F copies per base in addition to full-data deployment bases; total storage includes the fitted meta-model. Fold indices need O(n), transient copied training rows O(np). Classification blocks are bounded by B<=8,K<=8.

## 13. Python Implementation

The working from-scratch source is [python/solution.py](python/solution.py); [python/example.py](python/example.py) is executable. Public APIs are `StackingClassifier / StackingRegressor`, with fit/predict/score and the task-specific methods above. Core training uses NumPy/local code, never scikit-learn. B3 [support](../support.py) reuses canonical B1/B2 contracts and metrics; [tree.py](../tree.py) is explicit ensemble infrastructure. Factory defaults reuse canonical models rather than copying their solvers. Runtime dependencies come from [requirements-ml.txt](../../../requirements-ml.txt).

## 14. C++ Implementation

Classical ML uses the Python-first policy: optional C++ is **not implemented** for this topic. There are no dummy C++ source/test files. Existing DSA Python/C++ and C++17/C++20 requirements remain mandatory and unchanged.

## 15. Input and Output Examples

From the repository root with the ML test environment installed:

```sh
python machine-learning/ensemble-methods/stacking/python/example.py
```

The dataset, hyperparameters, seed and executed output are explained in the dry run. The same reusable API can be called as:

```python
# From this topic's python directory
from solution import StackingRegressor
model = StackingRegressor(**{'n_splits': 2, 'random_state': 0})
model.fit([[0], [1], [2], [3]], [0, 0, 4, 4])
predictions = model.predict([[0], [3]])
```

The JSON CLI accepts X, y, predict and optional parameters. It prints a predictions object; invalid input exits 2 with stderr and no prediction JSON. Factory callables are Python API configuration, not JSON-serializable CLI parameters.

## 16. Edge Cases

Classification folds require each class count>=F; a minority class is never silently omitted. Regression needs n>=F. Factories must return independent unfitted objects on every call. Invalid base probability protocols, sample mismatches and predict-before-fit fail. Failed refits retain the previous complete ensemble.

Do not mutate public parameters during inference. Caller arrays and global RNG state are preserved. Unsupported sample weights raise TypeError except where explicitly supported. Nonfinite/ambiguous shapes and predict-before-fit raise clear errors; extreme unresolved float64 operations fail rather than returning a fabricated success.

## 17. Advantages

Makes meta-learning and leakage control explicit, preserves auditable fold memberships/OOF outputs and supports both tasks using existing canonical meta-estimators.

## 18. Disadvantages and Limitations

More fits and retained diagnostics than voting. OOF training bases see less data than deployment bases, so feature-distribution shift can remain. Small classes restrict folds; Gaussian NB meta-probabilities assume conditional independence and need not be calibrated. No passthrough original features, prefit shortcut, nested hyperparameter search or arbitrary cross-validator API is implemented.

The [shared contracts](../../../docs/ensemble-methods-conventions.md) state numerical/resource limits and exact unsupported features. Scores and probability outputs are educational model quantities, not calibrated guarantees. A larger ensemble need not improve held-out error.

## 19. When to Use It

Use when there are enough training observations for reliable OOF predictions and a separately trained combination is useful.

## 20. When Not to Use It

Avoid for tiny minority classes, strict fit/storage budgets or situations where preprocessing/hyperparameter tuning already leaked held-out labels. Fit any supervised preprocessing separately inside each factory/fold.

## 21. Comparison With Related Algorithms

| Method | Meta-training | Leakage consideration |
| --- | --- | --- |
| Stacking | Learned from OOF prediction columns | Each row excluded from its generating base fit |
| Voting | None | Fixed weights still must not be tuned on final test |
| In-sample blending shortcut | Learns from training predictions | Can reward memorization; not implemented |

## 22. Interview Questions

1. Why are in-sample base predictions unsuitable for meta-training?
2. Why refit bases on full data after OOF generation?
3. What happens when a class has fewer observations than folds?
4. Where must supervised preprocessing be fitted?

## 23. Practice Problems

1. Reproduce the four OOF rows and Ridge normal equations in the dry run.
2. Use recorder bases to prove every held-out row is excluded.
3. Compare voting and stacking on the same external test split while keeping tuning within training data.

For validation run:

```sh
python -m pytest machine-learning/ensemble-methods/stacking -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
```

The independent oracles use hand calculations, exhaustive candidates or separately fitted references. Marker selections overlap; do not sum them as disjoint counts. Seeds, small datasets and explicit tolerances make failures reproducible. Full DSA regression also runs with `--require-cpp`.

## 24. References

[Wolpert, Stacked Generalization (1992)](https://doi.org/10.1016/S0893-6080(05)80023-1); [scikit-learn stacking guide](https://scikit-learn.org/1.8/modules/ensemble.html#stacked-generalization).

These primary references identify the mathematical method; the exact implemented subset and limits are stated here. External implementations may differ in split ties, random stream consumption, optimization or supported features; reference tests align compatible settings rather than asserting universal equivalence.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE) · [Contribution guidance](../../../CONTRIBUTING.md). This lesson belongs to authorized Phase 15 B3; its new review approval remains pending.
