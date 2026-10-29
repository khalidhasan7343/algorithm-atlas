# Bagging — Bootstrap Aggregating

## 1. Algorithm Name

Bagging — Bootstrap Aggregating

## 2. Overview

Train independent base estimators on datasets sampled with replacement, then aggregate their predictions. This lesson supports multiclass hard-vote classification and scalar regression averaging. A base estimator is supplied by a seed-taking factory; the default is the shared bounded weighted-tree primitive.

## 3. Problem Statement

Input X has shape (n,p), y shape (n,). Numeric fitting is bounded to 512 rows and 32 features; CatBoost has its stricter 64-row/8-feature limits. Regression is finite scalar float64. Classifiers preserve sorted homogeneous int64/string labels. Empty prediction matrices are supported; empty fitting data is rejected. See the complete [shared contracts](../../../docs/ensemble-methods-conventions.md) for exact ranges, atomic fit state, seed behavior, factory protocols and metric conventions.

Public model(s): `BaggingClassifier / BaggingRegressor`. Fitting constructs an ensemble; inference predicts one scalar or original class label per query row. Supported classification probabilities have one column per fitted sorted class.

## 4. Why Do We Need This Algorithm?

A high-variance learner can change substantially when a few observations change. Averaging partly independent errors can reduce variance: for equal-variance errors with pairwise correlation rho, Var(mean)=sigma²[rho+(1-rho)/T]. This identity explains why identical estimators bring little averaging benefit and why improvement is conditional, not guaranteed.

## 5. Real-World Applications

For a small numeric tabular classification or scalar-regression study, bootstrap fits can reveal how unstable tree decisions change under resampling. Repeated cohort fits and OOB coverage let learners inspect variance and row omission. Use an independent held-out cohort to assess whether averaging actually helped; OOB coverage alone is not deployment validation.

## 6. Core Intuition

Every bootstrap has m draws, not m unique observations. A training row is omitted with probability (1-1/n)^m. Separate bootstrap indices and estimator seeds are retained so the sampling can be inspected. Base models train independently; their predictions are never used to reweight later training rows.

For regression, f(x)=sum_t h_t(x)/T. For classification, p_k(x)=sum_t 1[h_t(x)=c_k]/T, and prediction is the first maximal p_k. These p values are hard-vote fractions rather than averaged leaf probabilities. Conditional on the fitted models, the aggregation code computes these definitions directly.

## 7. Prerequisites

Required: NumPy arrays, training versus test separation, probability/means, decision-tree partitions and finite-precision arithmetic. Read [ML development](../../../docs/ml-development.md), [Regression metrics](../../../docs/regression-evaluation.md) and [Classification contracts](../../../docs/classification-conventions.md). Algorithm-specific prerequisites include sampling, weighted counts and deterministic class ordering.

## 8. Step-by-Step Working Process

1. Validate dense X and targets, estimator count T, sample count m and local seed.
2. For each estimator draw m integers uniformly from [0,n), with replacement, then draw an independent integer base seed.
3. Ask the factory for a fresh unfitted estimator and fit copied sampled rows.
4. For classification, count predicted labels in the global sorted class order. Missing classes in a bootstrap do not remove global columns.
5. For regression, take the arithmetic mean of the T prediction vectors.
6. If OOB diagnostics are requested, aggregate a row only over estimators whose sampled indices omit it; retain coverage explicitly.
7. Publish fitted state only after every base fit succeeds. No later estimator consumes an earlier estimator's prediction.

The stored state follows the prediction formula above. All training is bounded, uses local RNGs and publishes fitted attributes only on successful completion.

## 9. Pseudocode

```text
rng <- local RNG(seed)
for t in 1..T:
    indices[t] <- m uniform indices with replacement
    base_seed[t] <- next independent integer from rng
    model[t] <- factory(base_seed[t]).fit(X[indices[t]], y[indices[t]])
predict regression <- mean(model[t].predict(query))
predict classification <- sorted class with most votes
```

## 10. Dry Run

For X=[0,1,2,3], labels=[cold,cold,warm,warm], T=3, depth=1 and seed=0,
the recorded bootstraps are [3,2,2,1], [0,0,0,0], [2,3,2,2]. The second base
sees only cold labels; it remains a valid one-class model. At x=0, two trees vote
cold; at x=3, two vote warm. The executed output is ["cold","warm"]. A bootstrap
with four draws need not contain every row or every class.

## 11. Time Complexity

Let B(m,p,d) be a base fit cost and Q(p,d) its one-row prediction cost. Fit costs O(T[m+B]); inference is O(TqQ+TqK) for q classification queries or O(TqQ) for regression. For default exhaustive trees B is conservatively O(p*m²*d), since every candidate partition is evaluated explicitly. There is no parallel speedup claim. Best/average runtime depends on early stops and data-dependent partitions; no universal average-case speed or wall-clock bound is asserted.

## 12. Space Complexity

Model storage is T times the base-model storage, plus O(Tm) retained bootstrap indices. Default tree storage is O(T*min(m,2^d)*K) for class distributions, or scalar leaves for regression. Temporary sampled matrices use O(mp). OOB accumulation needs O(nK) or O(n). Predictions can hold O(Tq) regression values.

## 13. Python Implementation

The working from-scratch source is [python/solution.py](python/solution.py); [python/example.py](python/example.py) is executable. Public APIs are `BaggingClassifier / BaggingRegressor`, with fit/predict/score and the task-specific methods above. Core training uses NumPy/local code, never scikit-learn. B3 [support](../support.py) reuses canonical B1/B2 contracts and metrics; [tree.py](../tree.py) is explicit ensemble infrastructure. Factory defaults reuse canonical models rather than copying their solvers. Runtime dependencies come from [requirements-ml.txt](../../../requirements-ml.txt).

## 14. C++ Implementation

Classical ML uses the Python-first policy: optional C++ is **not implemented** for this topic. There are no dummy C++ source/test files. Existing DSA Python/C++ and C++17/C++20 requirements remain mandatory and unchanged.

## 15. Input and Output Examples

From the repository root with the ML test environment installed:

```sh
python machine-learning/ensemble-methods/bagging/python/example.py
```

The dataset, hyperparameters, seed and executed output are explained in the dry run. The same reusable API can be called as:

```python
# From this topic's python directory
from solution import BaggingClassifier
model = BaggingClassifier(**{'n_estimators': 3, 'max_depth': 1, 'random_state': 0})
model.fit([[0], [1], [2], [3]], ['cold', 'cold', 'warm', 'warm'])
predictions = model.predict([[0], [3]])
```

The JSON CLI accepts X, y, predict and optional parameters. It prints a predictions object; invalid input exits 2 with stderr and no prediction JSON. Factory callables are Python API configuration, not JSON-serializable CLI parameters.

## 16. Edge Cases

A one-row dataset creates repeated copies of that row. One estimator equals its single base prediction. Exact class ties choose sorted class order. An uncovered OOB row is NaN diagnostic, not a fabricated prediction; the score is None if all rows are uncovered. Zero/negative estimator counts and invalid sample sizes fail.

Do not mutate public parameters during inference. Caller arrays and global RNG state are preserved. Unsupported sample weights raise TypeError except where explicitly supported. Nonfinite/ambiguous shapes and predict-before-fit raise clear errors; extreme unresolved float64 operations fail rather than returning a fabricated success.

## 17. Advantages

Works with different from-scratch fit/predict base families, retains explicit bootstrap evidence, and offers honest OOB coverage. Independent bases can be evaluated separately; aggregation itself is simple to audit.

## 18. Disadvantages and Limitations

Can retain a biased base learner and cannot promise improvement. Hard-vote fractions discard leaf confidence. More estimators increase model storage and inference work. OOB scores use only covered rows and are not substitutes for an independent test split. Factories must create deeply independent models.

The [shared contracts](../../../docs/ensemble-methods-conventions.md) state numerical/resource limits and exact unsupported features. Scores and probability outputs are educational model quantities, not calibrated guarantees. A larger ensemble need not improve held-out error.

## 19. When to Use It

Use when the base learner is unstable under resampling, repeated fits are affordable and a simple averaging/voting mechanism is desirable.

## 20. When Not to Use It

Avoid when one deterministic base already fits the useful signal, bases are highly correlated, inference budgets are strict, or training size exceeds the documented educational caps.

## 21. Comparison With Related Algorithms

| Method | Diversity / combination |
| --- | --- |
| Bagging | Bootstrap samples, independent fits, votes/mean |
| Random Forest | Bootstrap plus per-node feature sampling; class leaf-probability averaging here |
| AdaBoost | Sequential weighted-example fits and weighted votes |

## 22. Interview Questions

1. Why can an n-draw bootstrap contain fewer than n distinct rows?
2. Derive the omitted-row probability and distinguish it from guaranteed OOB coverage.
3. How does error correlation limit the variance benefit?
4. Why must a factory return fresh model state?

## 23. Practice Problems

1. Compute all votes for two constant classifiers with equal weights.
2. Enumerate all length-two bootstraps of a two-row dataset and their OOB sets.
3. Compare hard-vote fractions with mean leaf distributions on a controlled example.

For validation run:

```sh
python -m pytest machine-learning/ensemble-methods/bagging -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
```

The independent oracles use hand calculations, exhaustive candidates or separately fitted references. Marker selections overlap; do not sum them as disjoint counts. Seeds, small datasets and explicit tolerances make failures reproducible. Full DSA regression also runs with `--require-cpp`.

## 24. References

[Breiman, Bagging Predictors (1996)](https://doi.org/10.1007/BF00058655); [scikit-learn ensemble guide](https://scikit-learn.org/1.8/modules/ensemble.html#bagging-meta-estimator).

These primary references identify the mathematical method; the exact implemented subset and limits are stated here. External implementations may differ in split ties, random stream consumption, optimization or supported features; reference tests align compatible settings rather than asserting universal equivalence.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE) · [Contribution guidance](../../../CONTRIBUTING.md). This lesson belongs to authorized Phase 15 B3; its new review approval remains pending.
