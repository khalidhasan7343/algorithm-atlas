# Random Forest

## 1. Algorithm Name

Random Forest

## 2. Overview

A collection of bootstrap decision trees with a fresh random feature subset at each eligible split. Classification averages aligned leaf distributions; regression averages scalar leaves. This implements the central forest mechanism with exhaustive greedy splits and explicit depth/leaf bounds.

## 3. Problem Statement

Input X has shape (n,p), y shape (n,). Numeric fitting is bounded to 512 rows and 32 features; CatBoost has its stricter 64-row/8-feature limits. Regression is finite scalar float64. Classifiers preserve sorted homogeneous int64/string labels. Empty prediction matrices are supported; empty fitting data is rejected. See the complete [shared contracts](../../../docs/ensemble-methods-conventions.md) for exact ranges, atomic fit state, seed behavior, factory protocols and metric conventions.

Public model(s): `RandomForestClassifier / RandomForestRegressor`. Fitting constructs an ensemble; inference predicts one scalar or original class label per query row. Supported classification probabilities have one column per fitted sorted class.

## 4. Why Do We Need This Algorithm?

Bootstrap trees can remain correlated when a dominant feature drives the same splits in every tree. Restricting each node to a random feature subset can diversify their partitions. The tradeoff is that a node can miss a useful feature and increase individual-tree bias.

## 5. Real-World Applications

Numeric sensor measurements or engineered image-region features can require nonlinear class boundaries and interactions. A forest lets a teaching experiment compare all-feature trees with random node subspaces and inspect the correlation/diversity tradeoff. This dense small-data implementation requires preprocessed finite features and makes no claim to handle raw imagery or missing sensor readings.

## 6. Core Intuition

Random Forest reuses the canonical Bagging bootstrap loop but changes the tree-building contract: candidate features are sampled independently at every eligible node. This is not one global feature subset per tree and not an Extra Trees random-threshold method. Thresholds are still searched greedily among deterministic midpoint candidates.

If tree t has leaf distribution p_tk(x), forest p_k(x)=sum_t p_tk(x)/T. Prediction chooses the first largest global class column. Regression uses the same mean identity for leaf means. Each stored node records its sampled candidate feature tuple, allowing tests to verify feature selection independently of final accuracy.

## 7. Prerequisites

Required: NumPy arrays, training versus test separation, probability/means, decision-tree partitions and finite-precision arithmetic. Read [ML development](../../../docs/ml-development.md), [Regression metrics](../../../docs/regression-evaluation.md) and [Classification contracts](../../../docs/classification-conventions.md). Algorithm-specific prerequisites include sampling, weighted counts and deterministic class ordering.

## 8. Step-by-Step Working Process

1. Validate n_estimators, max_features, max_samples, depth, leaf size and seed.
2. For each tree retain a bootstrap sample and independent tree seed using canonical Bagging.
3. At a nonterminal node draw max_features distinct feature indices using that tree's local RNG.
4. Evaluate every valid midpoint of the chosen features using weighted Gini or locally normalized squared error.
5. Expand only an impurity-reducing valid split; recurse subject to the fixed depth and positive-row leaf constraints.
6. Classification leaves retain empirical distributions in the tree's own sorted class order. Align them to the forest classes before averaging.
7. Average scalar regression outputs or class distributions, and optionally collect covered-only OOB predictions.

The stored state follows the prediction formula above. All training is bounded, uses local RNGs and publishes fitted attributes only on successful completion.

## 9. Pseudocode

```text
for each bootstrap tree t:
    grow(node):
        if pure or depth/leaf bound: return empirical leaf
        features <- local_rng.choose(p, k, without_replacement)
        split <- best positive-impurity-gain midpoint among features
        recurse on valid children, otherwise return leaf
predict <- mean of aligned tree distributions or regression values
```

## 10. Dry Run

The example has one feature, so sqrt(p)=1 and every eligible node considers it.
With seed 0 and three depth-one trees, bootstrap cohorts are [3,2,2,1],
[0,0,0,0] and [2,3,2,2]. Queries 0 and 3 predict cold and warm. With multiple
features, the seeded tests visit stored nodes and independently check that each
candidate subset has the requested size and the chosen feature belongs to it.

## 11. Time Complexity

Let n be training rows, m bootstrap draws, p features, k sampled features per node, d depth, T trees, K classes and q query rows. Exhaustive split evaluation gives a conservative O(T*k*m²*d) fit bound plus bootstrap work; prediction is O(T*q*d+T*q*K). A full scan of distinct values per node is educational, not the optimized production bound. Best/average runtime depends on early stops and data-dependent partitions; no universal average-case speed or wall-clock bound is asserted.

## 12. Space Complexity

Bootstrap indices use O(Tm); tree storage is O(T*min(m,2^d)*K) for classification and scalar per node for regression. Recursion stack depth is O(d). Sampled data and partition temporaries add O(mp+m*d); probability aggregation uses O(qK). No feature-importance array or training-data store is exposed.

## 13. Python Implementation

The working from-scratch source is [python/solution.py](python/solution.py); [python/example.py](python/example.py) is executable. Public APIs are `RandomForestClassifier / RandomForestRegressor`, with fit/predict/score and the task-specific methods above. Core training uses NumPy/local code, never scikit-learn. B3 [support](../support.py) reuses canonical B1/B2 contracts and metrics; [tree.py](../tree.py) is explicit ensemble infrastructure. Factory defaults reuse canonical models rather than copying their solvers. Runtime dependencies come from [requirements-ml.txt](../../../requirements-ml.txt).

## 14. C++ Implementation

Classical ML uses the Python-first policy: optional C++ is **not implemented** for this topic. There are no dummy C++ source/test files. Existing DSA Python/C++ and C++17/C++20 requirements remain mandatory and unchanged.

## 15. Input and Output Examples

From the repository root with the ML test environment installed:

```sh
python machine-learning/ensemble-methods/random-forest/python/example.py
```

The dataset, hyperparameters, seed and executed output are explained in the dry run. The same reusable API can be called as:

```python
# From this topic's python directory
from solution import RandomForestClassifier
model = RandomForestClassifier(**{'n_estimators': 3, 'max_depth': 1, 'random_state': 0})
model.fit([[0], [1], [2], [3]], ['cold', 'cold', 'warm', 'warm'])
predictions = model.predict([[0], [3]])
```

The JSON CLI accepts X, y, predict and optional parameters. It prints a predictions object; invalid input exits 2 with stderr and no prediction JSON. Factory callables are Python API configuration, not JSON-serializable CLI parameters.

## 16. Edge Cases

Constant features produce no valid threshold. Pure leaves are exact. Missing bootstrap classes are aligned with zero probability columns. Duplicate observations can appear repeatedly. One tree is a randomized bootstrap tree, not a guarantee of the full-data CART fit. Invalid max_features fails instead of silently clipping.

Do not mutate public parameters during inference. Caller arrays and global RNG state are preserved. Unsupported sample weights raise TypeError except where explicitly supported. Nonfinite/ambiguous shapes and predict-before-fit raise clear errors; extreme unresolved float64 operations fail rather than returning a fabricated success.

## 17. Advantages

Adds a directly visible source of diversity to bootstrap aggregation, supports both tasks and reports node candidates and OOB coverage for inspection.

## 18. Disadvantages and Limitations

Trees are greedy. Zero-gain nodes stop, so an XOR problem requiring a zero-gain first split can differ from libraries that grow through such nodes. More trees need more storage and do not guarantee higher test accuracy. Empirical leaf probabilities are not calibrated. Bootstrap is always enabled; feature importance is not exposed.

The [shared contracts](../../../docs/ensemble-methods-conventions.md) state numerical/resource limits and exact unsupported features. Scores and probability outputs are educational model quantities, not calibrated guarantees. A larger ensemble need not improve held-out error.

## 19. When to Use It

Use for bounded numeric tabular examples where nonlinear partitions and randomized ensemble diversity are useful teaching mechanisms.

## 20. When Not to Use It

Avoid for categorical strings without explicit encoding, sparse or missing data, extrapolation-heavy regression, strict model-size limits or production-scale performance requirements.

## 21. Comparison With Related Algorithms

| Method | Node thresholds | Feature randomness |
| --- | --- | --- |
| Bagged trees | Best midpoint | All features by default |
| Random Forest | Best midpoint | Fresh subset per node |
| Extra Trees | Random thresholds | Often subsets; not implemented here |

## 22. Interview Questions

1. Distinguish per-node and per-tree feature sampling.
2. Why can lower tree correlation help an average?
3. How do missing bootstrap classes affect probability columns?
4. Why need not a one-tree forest equal a full-data CART?

## 23. Practice Problems

1. Visit each stored node and verify candidate subset sizes.
2. Manually align two trees with different class sets.
3. Compare forests with all features and one feature using the same split, without claiming universal improvement.

For validation run:

```sh
python -m pytest machine-learning/ensemble-methods/random-forest -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
```

The independent oracles use hand calculations, exhaustive candidates or separately fitted references. Marker selections overlap; do not sum them as disjoint counts. Seeds, small datasets and explicit tolerances make failures reproducible. Full DSA regression also runs with `--require-cpp`.

## 24. References

[Breiman, Random Forests (2001)](https://doi.org/10.1023/A:1010933404324); [scikit-learn forests](https://scikit-learn.org/1.8/modules/ensemble.html#forest).

These primary references identify the mathematical method; the exact implemented subset and limits are stated here. External implementations may differ in split ties, random stream consumption, optimization or supported features; reference tests align compatible settings rather than asserting universal equivalence.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE) · [Contribution guidance](../../../CONTRIBUTING.md). This lesson belongs to authorized Phase 15 B3; its new review approval remains pending.
