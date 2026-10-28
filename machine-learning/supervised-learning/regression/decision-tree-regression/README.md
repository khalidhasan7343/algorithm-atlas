# Decision Tree Regression

## 1. Algorithm Name

**Decision Tree Regression** — dense, single-output educational regression. The canonical topic is `decision-tree-regression` in B1 Supervised Learning — Regression, Phase 13.

## 2. Overview

CART Regression constructs axis-aligned binary partitions and predicts the mean training target in each leaf. This implementation explicitly enumerates candidate boundaries after stable feature sorting, chooses the best immediate squared-error reduction and recursively builds a bounded-depth tree. It is greedy; it does not optimize all possible trees globally.

## 3. Problem Statement

Let X∈Rⁿˣᵖ be real features and y∈Rⁿ continuous targets. A node with row set S predicts μS=Σᵢ∈Syᵢ/|S| and has squared error E(S)=Σᵢ∈S(yᵢ−μS)². For feature j and threshold t, split S into L={i:xᵢⱼ≤t} and R={i:xᵢⱼ>t}. Choose the eligible pair minimizing E(L)+E(R). Both children must contain at least min_samples_leaf rows. A query follows these comparisons to a scalar leaf prediction; m queries yield an m-vector.

## 4. Why Do We Need This Algorithm?

An affine fit cannot directly represent sharp changes, interactions or different target levels in separate regions. A regression tree learns such partitions without hand-writing polynomial interactions. Its flexibility can overfit noise, so depth and leaf-size controls are part of the model rather than optional reporting details.

## 5. Real-World Applications

Examples include an interpretable piecewise-constant response to operating conditions or a modest nonlinear baseline with mixed numerical feature scales. Splits use feature ordering and do not require comparable feature units. This implementation accepts numeric arrays only; it does not infer categories, impute missing values or establish causal rules.

## 6. Core Intuition

The best constant c in a leaf minimizes Σ(yᵢ−c)². Differentiating gives c=μS. Once observations are sorted by a feature, each boundary between distinct adjacent feature values defines a unique nonempty partition. Prefix sums of centered targets and their squares compute every candidate child's error without refitting a model. A locally best split need not lead to the globally best depth-limited tree.

## 7. Prerequisites

Know binary trees, recursion, stable sorting and the mean's least-squares property. [Linear Regression](../linear-regression/README.md) provides a smooth baseline; [Polynomial Regression](../polynomial-regression/README.md) changes the basis instead of partitioning the input. No gradient or smooth optimization solver is required for this combinatorial greedy procedure.

## 8. Step-by-Step Working Process

1. Validate and copy training arrays. Start at depth zero with all row indices.
2. Detect a pure node using exact equality of its original targets, retaining their common value exactly. Otherwise compute the node mean, center targets and divide by their maximum absolute deviation. Stop at max_depth or fewer than twice min_samples_leaf rows; an underflowed squared-error diagnostic is never a purity test.
3. Visit features in their original order. Stably sort node rows by the chosen feature, then compute prefix sums and squared sums of the normalized centered targets. This common positive scaling preserves candidate rankings while preventing tiny targets' squares from underflowing. For k left rows, use Eleft=Σz²−(Σz)²/k and the corresponding suffix formula for the right child; clamp small negative variance expressions to zero.
4. Enumerate only distinct adjacent feature values and eligible child sizes. Prefer smaller total child error; differences within 32·machine_epsilon·parent_error are ties and retain the first feature/boundary encountered. Place t midway between adjacent values; if rounding reaches the upper endpoint use the lower endpoint so the split remains valid.
5. Require original-unit gain=(Eparent−Eleft−Eright)/n_total ≥ min_impurity_decrease. With node target scale s and normalized errors, compare s·sqrt(max(0,Eparent_normalized−Echildren_normalized)/n_total) against sqrt(min_impurity_decrease). This preserves the threshold's original squared-target units without prematurely squaring s. The original training sample count is used at every depth. Zero-gain splits remain permitted when the threshold is zero, allowing interactions such as XOR to become visible at a later level.
6. Recursively build children, retain frozen mean-leaf nodes and commit only after the entire fit succeeds. Prediction routes each row down the completed tree.

There is no iterative loss convergence test. `converged_=True` records completed bounded construction and does not assert global tree optimality. Depth/leaf constraints guarantee termination; finite precision limits close split rankings.

## 9. Pseudocode

```text
BUILD(rows, depth):
  if original targets are equal: return their exact common-value leaf
  value = mean(y[rows]); scale targets by their maximum absolute deviation
  if depth limit, pure target or too few rows: return leaf(value)
  best = none
  for feature in original order:
    stable-sort rows; make normalized centered prefix sums
    for eligible boundary between distinct values:
      score = left_squared_error + right_squared_error
      retain first boundary with a materially better score
  if no split or original-unit root-gain too small: return leaf(value)
  return node(feature, threshold, BUILD(left,depth+1), BUILD(right,depth+1))
PREDICT(row): follow <= threshold left, otherwise right, until a leaf
```

## 10. Dry Run

Use x=[0,1,2,3] and y=[1,1,5,5]. The root mean is 3 and root squared error is 4+4+4+4=16. Splitting after x=1 gives threshold 1.5, left mean 1, right mean 5 and total child error 0. Splitting after x=0 or x=2 gives child error 32/3, so threshold 1.5 wins uniquely. Its root-normalized gain is 16/4=4. With max_depth=1 the leaves predict 1 at x=0.5 and 5 at x=2.5. A min_impurity_decrease of 4 permits the split; 4.1 rejects it.

## 11. Time Complexity

At a node with s rows, sorting p features costs O(ps log s) and prefix/candidate work costs O(ps). With actual depth d, a conservative bound is O(dpn log n), since row counts per level sum to at most n. Depth is bounded by max_depth≤32. Predicting m rows costs O(md); a root-only tree predicts in O(m). Repeated sorting is deliberately simple and is less efficient than specialized globally presorted tree builders.

## 12. Space Complexity

The owned dense training matrix costs O(np). Recursive row-index/temporary arrays have a conservative O(nd) bound plus O(n) split workspace. The completed model uses O(nodes) frozen node records; nodes≤2n−1 since every split has nonempty disjoint children. Inference keeps a checked O(mp) query copy and O(m) output, then walks nodes iteratively. The estimator does not keep the training matrix after construction.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) provides `DecisionTreeRegression(max_depth=5, min_samples_leaf=1, min_impurity_decrease=0.0)` with keyword-only parameters. Depth is a native int in 1..32, min_samples_leaf a native int in 1..1024, and min_impurity_decrease finite in [0,10¹²]. Fit requires n≤2048, p≤32 and at most 262144 cells, finite real inputs with |value|≤10¹², 2D X and 1D y. It returns self; predict accepts (m,p), m≤10000 under the same cell limit and returns (m,). Score is R², with a constant-target convention of 1 for perfect fit and 0 otherwise. Inspect `tree_`, `depth_`, `n_leaves_`, `training_mse_` and `n_features_in_`. Each frozen Node stores mean, row count, squared error, optional feature/threshold and children. There is no seed, pruning path or sample-weight argument.

## 14. C++ Implementation

C++ is optional for classical ML and **not implemented** for this topic. There is no dummy C++ source or C++ test. The catalog keeps `cpp_status: planned` as an honest optional deliverable; Python/numerical completion is independent of it. DSA retains mandatory Python/C++ and both C++17/C++20 gates. See the [track policy](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install runtime dependencies with `python -m pip install -r requirements-ml.txt`, then run:

```sh
.venv/bin/python machine-learning/supervised-learning/regression/decision-tree-regression/python/example.py
```

Expected rounded prediction:

```text
[1.0, 5.0]
```

The example fits the small training dataset from the dry run and predicts a separate query. Equivalent API code is:

```python
import numpy as np
from solution import DecisionTreeRegression  # run from this topic's python/ directory
X = [[0.0], [1.0], [2.0], [3.0]]
y = [1.0, 1.0, 5.0, 5.0]
model = DecisionTreeRegression(max_depth=1).fit(X, y)
print(np.round(model.predict([[0.5], [2.5]]), 6).tolist())
```

The standalone `solution.py` also accepts one JSON object with `X`, `y`, `predict` and an optional constructor `parameters` object, and returns `{"predictions":[...]}` at full float64 precision. Invalid data or non-convergence produces stderr and exit 2, with no successful prediction JSON. Run tests with `python -m pytest machine-learning/supervised-learning/regression/decision-tree-regression -q` after installing `requirements-ml-test.txt`.

## 16. Edge Cases

A single row, constant target or all-identical features produces a leaf. Repeated feature values are never separated by a threshold. A zero-gain root may still expose a later interaction; the depth bound controls such expansion. Adjacent floating-point values use the lower-endpoint fallback when midpoint rounding would create an empty child. Centered sums avoid cancellation from a large target offset, but cannot recover differences already rounded out of input float64 values. Empty shaped queries return an empty vector. NaN/Inf, complex/bool data, wrong dimensions, mismatched query features, invalid parameters and resource overflows raise ValueError. A failed refit preserves the old tree; later mutation of caller arrays cannot change its nodes.

## 17. Advantages

The model represents interactions and threshold effects, has no coefficient-scaling penalty and is easy to inspect on small examples. Deterministic feature order and stable sorting make ties reproducible. Independent brute-force split tests exercise the greedy decision directly, rather than relying only on a library's final predictions.

## 18. Disadvantages and Limitations

Greedy search can miss a better whole tree, and small data changes may alter splits sharply. Deep trees overfit and piecewise-constant leaves cannot extrapolate a linear trend beyond the observed partitions. Close scores depend on float64 rounding; this implementation's tie tolerance and zero-gain convention can differ from another library. It omits categorical/missing-value routing, sample weights, feature subsampling, ensembles and cost-complexity pruning. Frozen nodes prevent accidental node-field reassignment; the estimator's public fitted-state attributes remain user-accessible.

## 19. When to Use It

Use it for an inspectable nonlinear baseline on modest numerical data. Select depth and leaf size with training/validation data and measure MSE/MAE/R² on a held-out set once selection is complete. Inspect leaf sample counts and how predictions behave near thresholds. Scaling is unnecessary for order-based splits, though preprocessing must still avoid leakage.

## 20. When Not to Use It

Avoid claiming smooth derivatives, reliable extrapolation, global optimization or causal effects from a fitted tree. Do not grow a deep tree solely to eliminate training error. A smooth affine trend can be represented more compactly by Linear or Ridge Regression; deployment requiring missing-value handling needs an explicit policy outside this implementation.

## 21. Comparison With Related Algorithms

| Related method | Difference |
| --- | --- |
| Linear Regression | One global affine function; smooth extrapolation, different bias |
| Polynomial Regression | Fixed smooth basis followed by least squares |
| SVR | Convex norm/tube objective rather than greedy partition search |
| Random Forest | Combines randomized trees; later catalog category, not implemented here |

## 22. Interview Questions

Why is a leaf mean optimal for squared error? Derive the prefix-sum score and explain target centering. Why can a zero-gain split expose an interaction? Which denominator is used in min_impurity_decrease? Why do reference tests avoid requiring identical trees when tied partitions exist?

## 23. Practice Problems

1. Enumerate all thresholds in the dry run and compute each child's squared error.
2. Construct a two-feature XOR target and compare depth one with depth two.
3. Use a fixed split to compare validation error over depths and leaf sizes, then report held-out metrics, tree depth and leaf count without optimizing on held-out targets.

## 24. References

- [scikit-learn decision-tree mathematical formulation](https://scikit-learn.org/1.8/modules/tree.html#mathematical-formulation).
- [Regression-tree criteria and practical limitations](https://scikit-learn.org/1.8/modules/tree.html#regression).

The implementation uses its own split enumeration. Reference tests use data with distinct useful split scores; separate brute-force tests verify deterministic tie behavior and normalized-gain boundaries. Gradient checking is inapplicable to discrete split search.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). See [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 13 owner review is pending; implementation and test evidence do not imply owner approval.
