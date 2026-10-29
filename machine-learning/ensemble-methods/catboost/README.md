# CatBoost — naive ordered boosting with categorical statistics

## 1. Algorithm Name

CatBoost — naive ordered boosting with categorical statistics

## 2. Overview

A from-scratch educational implementation of ordered target statistics and the original CatBoost paper's naive prefix-model ordered boosting (Algorithm 1), using symmetric regression trees. This is a genuine ordered procedure with independent prefix models, not ordinary GBM renamed as CatBoost. The optimized shared-tree production Algorithm 2 is outside this bounded variant.

## 3. Problem Statement

Input X has shape (n,p), y shape (n,). Numeric fitting is bounded to 512 rows and 32 features; CatBoost has its stricter 64-row/8-feature limits. Regression is finite scalar float64. Classifiers preserve sorted homogeneous int64/string labels. Empty prediction matrices are supported; empty fitting data is rejected. See the complete [shared contracts](../../../docs/ensemble-methods-conventions.md) for exact ranges, atomic fit state, seed behavior, factory protocols and metric conventions.

Public model(s): `CatBoostRegressor`. Fitting constructs an ensemble; inference predicts one scalar or original class label per query row. Supported classification probabilities have one column per fitted sorted class.

## 4. Why Do We Need This Algorithm?

Using a row's own target in categorical encoding can make training features reveal their labels. Ordinary residual fitting also evaluates a row with a model trained on that row. An ordering lets both target statistics and residual estimation use only preceding observations. Maintaining every prefix directly is expensive but makes the exclusion rule auditable.

## 5. Real-World Applications

A small regression dataset with product, merchant or region identifiers can demonstrate why naive target-mean encoding leaks labels and how ordered statistics avoid each row’s own target. Prefix models make the corresponding residual exclusion inspectable. Production high-cardinality systems need the optimized framework and separate validation; this direct educational method is strictly small-data.

## 6. Core Intuition

Draw a fixed permutation. A category statistic for rank i uses only matching-category targets at ranks less than i, with a fixed target-independent prior. Maintain model M_j trained from the first j observations. At each round compute r_i=y_i-M_i(x_i) with zero-based ranks, then independently fit each prefix model's new symmetric tree to the residuals available in that prefix.

For training row i, TS_i=(sum_{j preceding i, same category}y_j+a*p)/(count+a). This excludes its own and future targets. Prefix residuals use a model trained without that row. The prefix exclusion invariant holds inductively because each new prefix tree depends only on earlier available residuals/features. Symmetric-tree leaf values are residual means; empty cells use zero update.

## 7. Prerequisites

Required: NumPy arrays, training versus test separation, probability/means, decision-tree partitions and finite-precision arithmetic. Read [ML development](../../../docs/ml-development.md), [Regression metrics](../../../docs/regression-evaluation.md) and [Classification contracts](../../../docs/classification-conventions.md). Algorithm-specific prerequisites include gradients and loss minimization.

## 8. Step-by-Step Working Process

1. Validate n<=64, p<=8, <=16 rounds, depth<=3, fixed numeric prior and positive prior weight. Categorical columns are explicitly selected.
2. Generate a local seeded permutation, shared by categorical encoding and ordered residual evaluation.
3. Scan that order to compute (previous target sum+a*prior)/(previous count+a) for every categorical entry; save full-data statistics separately.
4. Initialize all prefix models, including empty prefix M0, to the fixed prior. The prior is never inferred from y.
5. Before each round, evaluate each row with its preceding-prefix model and record the resulting residual.
6. For every nonempty prefix j, fit a new oblivious tree to that prefix's residuals only. At each level an oblivious tree shares one split across all current cells.
7. Update that prefix model by eta times its own tree. Prefix models do not share learned structures or target-dependent leaf values.
8. Return the full-prefix ensemble. For new rows, encode using full-training category statistics; unseen categories receive the fixed prior.

The stored state follows the prediction formula above. All training is bounded, uses local RNGs and publishes fitted attributes only on successful completion.

## 9. Pseudocode

```text
order <- seeded permutation
Z <- numeric columns plus ordered categorical target statistics
M[0..n] <- fixed prior
for round in 1..T:
    for rank i in 0..n-1:
        residual[i] <- y[order[i]]-M[i](Z[order[i]])
    for length j in 1..n:
        h <- symmetric_tree.fit(Z[order[:j]], residual[:j])
        M[j] <- M[j]+eta*h
return M[n]
inference encoding <- full-training statistics, unseen category -> prior
```

## 10. Dry Run

The example uses rows [(a,0),(a,1),(b,2),(b,3)], targets [0,0,4,4],
prior 0, prior weight 1 and seed 0. The order is [2,0,1,3]. In original row
order the categorical statistics are [0,0,0,2]: the last b uses the previous
b target 4 divided by count+prior_weight=2. In round one every prefix model
starts at zero, so residuals equal y. The full-prefix depth-one tree chooses
the numeric split 1.5 and predicts [0,4] at the endpoint queries. A separate
constant-feature oracle computes every prefix update by explicit arithmetic.

## 11. Time Complexity

Let n<=64, p<=8, T<=16 and depth d<=3. Every round fits n independent prefix trees. The straightforward symmetric-tree scorer enumerates O(p*j) thresholds per level for prefix size j and scans up to j rows for each of up to 2^d cells: a conservative fit bound is O(T*p*2^d*d*n³). Updating all prefix prediction rows adds O(T*n²*d). Inference is O(q*p+T*q*d) with dictionary category lookups. These are naive educational bounds, not production CatBoost bounds. Best/average runtime depends on early stops and data-dependent partitions; no universal average-case speed or wall-clock bound is asserted.

## 12. Space Complexity

Retained prefix trees use O(T*n*2^d), while the prefix prediction matrix uses O(n²). Ordered features and categorical dictionaries use O(np); residual diagnostics O(Tn). Only the full-prefix T trees are needed for deployment, but all prefixes remain stored here to verify exclusion.

## 13. Python Implementation

The working from-scratch source is [python/solution.py](python/solution.py); [python/example.py](python/example.py) is executable. Public APIs are `CatBoostRegressor`, with fit/predict/score and the task-specific methods above. Core training uses NumPy/local code, never scikit-learn. B3 [support](../support.py) reuses canonical B1/B2 contracts and metrics; [tree.py](../tree.py) is explicit ensemble infrastructure. Factory defaults reuse canonical models rather than copying their solvers. Runtime dependencies come from [requirements-ml.txt](../../../requirements-ml.txt).

## 14. C++ Implementation

Classical ML uses the Python-first policy: optional C++ is **not implemented** for this topic. There are no dummy C++ source/test files. Existing DSA Python/C++ and C++17/C++20 requirements remain mandatory and unchanged.

## 15. Input and Output Examples

From the repository root with the ML test environment installed:

```sh
python machine-learning/ensemble-methods/catboost/python/example.py
```

The dataset, hyperparameters, seed and executed output are explained in the dry run. The same reusable API can be called as:

```python
# From this topic's python directory
from solution import CatBoostRegressor
model = CatBoostRegressor(**{'categorical_features': [0], 'n_estimators': 1, 'learning_rate': 1, 'max_depth': 1, 'random_state': 0})
model.fit([['a', 0], ['a', 1], ['b', 2], ['b', 3]], [0, 0, 4, 4])
predictions = model.predict([['a', 0], ['b', 3]])
```

The JSON CLI accepts X, y, predict and optional parameters. It prints a predictions object; invalid input exits 2 with stderr and no prediction JSON. Factory callables are Python API configuration, not JSON-serializable CLI parameters.

## 16. Edge Cases

Unseen categories use the prior; categorical label families must match training. Duplicate category labels are valid and do not expose their own target. Empty symmetric cells receive zero updates. With no category columns, the ordered boosting procedure still applies to numeric features. M0 stays at the fixed prior, so even constant targets can have nonzero ordered residuals and final loss need not decrease every round.

Do not mutate public parameters during inference. Caller arrays and global RNG state are preserved. Unsupported sample weights raise TypeError except where explicitly supported. Nonfinite/ambiguous shapes and predict-before-fit raise clear errors; extreme unresolved float64 operations fail rather than returning a fabricated success.

## 17. Advantages

Makes both sources of ordering explicit, retains prefix ensembles and ordered features, and permits strong tests that alter current/future targets while checking preceding model invariance.

## 18. Disadvantages and Limitations

Only squared-loss regression and explicit single categorical columns; no category combinations, multiple permutations, optimized shared structures, Bayesian bootstrap, classification, ranking, GPU or production parity. Tiny sample counts give high-variance prefix estimates. Training ordered features differ from full-statistic inference features. The direct method is intentionally expensive and strictly capped.

The [shared contracts](../../../docs/ensemble-methods-conventions.md) state numerical/resource limits and exact unsupported features. Scores and probability outputs are educational model quantities, not calibrated guarantees. A larger ensemble need not improve held-out error.

## 19. When to Use It

Use for a small demonstration of target leakage, prefix exclusion, ordered residuals and symmetric-tree categorical boosting.

## 20. When Not to Use It

Avoid for production throughput, large datasets, the complete CatBoost API, multiclass/logistic objectives or claims of numerical equality with the optimized library.

## 21. Comparison With Related Algorithms

| Method | Residual model / category handling |
| --- | --- |
| GBM here | Current full-data model; numeric features |
| XGBoost here | Full-data second-order gradients; numeric features |
| CatBoost here | Preceding-prefix models; ordered TS and symmetric trees |

## 22. Interview Questions

1. Why must a training category statistic exclude its own target?
2. Why use the same permutation for encoding and boosting?
3. Prove a prefix model cannot depend on a future target.
4. Explain the extra cost of naive prefix fitting and why production Algorithm 2 differs.

## 23. Practice Problems

1. Hand-compute the four ordered category statistics in the dry run.
2. Alter only a future target and verify all preceding prefix trees remain unchanged.
3. For constant numeric X, compute two rounds of all prefix means independently.

For validation run:

```sh
python -m pytest machine-learning/ensemble-methods/catboost -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
```

The independent oracles use hand calculations, exhaustive candidates or separately fitted references. Marker selections overlap; do not sum them as disjoint counts. Seeds, small datasets and explicit tolerances make failures reproducible. Full DSA regression also runs with `--require-cpp`.

## 24. References

[Prokhorenkova et al., CatBoost (2018), Algorithm 1 and ordered statistics](https://papers.nips.cc/paper/7898-catboost-unbiased-boosting-with-categorical-features.pdf); [official unbiased-boosting overview](https://catboost.ai/docs/en/concepts/algorithm-main-stages_fighting-biases).

These primary references identify the mathematical method; the exact implemented subset and limits are stated here. External implementations may differ in split ties, random stream consumption, optimization or supported features; reference tests align compatible settings rather than asserting universal equivalence.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE) · [Contribution guidance](../../../CONTRIBUTING.md). This lesson belongs to authorized Phase 15 B3; its new review approval remains pending.
