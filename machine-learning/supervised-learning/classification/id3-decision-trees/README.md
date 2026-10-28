# ID3 Decision Trees

## 1. Algorithm Name

**ID3 Decision Trees**, canonical `id3-decision-trees` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

ID3 grows a categorical decision tree by selecting the feature with largest information gain, then creating one branch per observed value. This implementation uses integer-coded categories, explicit Shannon entropy and recursive feature removal. It is a multiway categorical learner, not a renamed numeric CART tree.

## 3. Problem Statement

For node S with class proportions pk, Shannon entropy is H(S)=−Σpk log₂pk, taking 0log0=0. For categorical feature j with observed groups Sv, information gain is IG(S,j)=H(S)−Σv(|Sv|/|S|)H(Sv). Choose the first original feature with materially largest eligible gain. Each child must meet min_samples_leaf. Predict its empirical class distribution at a leaf, and the first sorted class maximizing that distribution. At an unseen category, stop at the current node and use its distribution/majority fallback.

## 4. Why Do We Need This Algorithm?

A numeric threshold imposes an ordering on feature values. For nominal categories that ordering can be arbitrary. ID3 explicitly tests equality to category codes and separates every observed category in one split. Information gain measures reduction of class uncertainty under that partition.

## 5. Real-World Applications

Examples include a small categorical rule-learning exercise or an encoded weather/choice dataset. The integer codes identify categories only; code 2 is not assumed twice code 1. No dictionary fitting, raw-string feature parsing or automatic numerical discretization is performed.

## 6. Core Intuition

A feature is useful when knowing its value makes the class distribution less uncertain. Pure child groups have entropy zero, while mixed groups retain uncertainty. ID3 greedily maximizes immediate entropy reduction, removes the selected feature on each descendant path and repeats. High-cardinality identifiers can achieve large gain by fragmenting data, a genuine limitation rather than evidence of predictive usefulness.

## 7. Prerequisites

Know categorical variables, class frequencies, Shannon entropy and recursion. [CART](../cart-decision-trees/README.md) uses binary numeric Gini splits. [C4.5](../c4-5-decision-trees/README.md) adjusts selection using split information/gain ratio and supports continuous thresholds. The scalar entropy helper is also reused there as explicit canonical mathematical reuse.

## 8. Step-by-Step Working Process

1. Validate/copy numeric X; every feature must contain integer-valued category codes, with at most 64 observed values per training column. Encode sorted class labels.
2. Compute the current node class counts, entropy and empirical distribution.
3. Stop at purity, depth/sample limits or feature exhaustion. Otherwise, for each remaining feature, group rows by sorted observed values. Reject a split if any child is too small.
4. Calculate weighted child entropy and nonnegative gain. Keep the first best feature, treating gain differences within 10⁻¹⁴ as ties.
5. Require gain≥min_gain. With default zero threshold, a zero-gain split is allowed; feature removal still guarantees progress and can expose XOR at the next level.
6. Remove the chosen feature for every child, recursively build branches and store immutable branch tuples. Commit only after the whole fit succeeds.
7. At query time follow exact category equality. An unseen value falls back immediately to the distribution at that node; it is not assigned to an arbitrary branch.

This is bounded greedy ID3 with explicit depth/sample controls. Completed construction does not establish a globally optimal tree or generalization.

## 9. Pseudocode

```text
BUILD(rows, available_features, depth):
  make class frequencies and entropy
  if pure, limits or no available feature: return leaf
  for feature in original available order:
    groups = equality groups for sorted observed codes
    if eligible: gain = parent_entropy - weighted_child_entropy
  choose first maximum; if gain below min_gain: return leaf
  remove chosen feature; recursively build one child per group
PREDICT(row): follow matching categories; unseen code returns current distribution
```

## 10. Dry Run

Train on [feature0,feature1]=[0,0],[0,1],[1,0],[1,1], labels [no,no,yes,yes]. Root entropy is one bit. Feature0 produces two pure two-row groups and gain 1−0=1. Feature1 produces two equally mixed groups, gain 1−1=0. Choose feature0. Queries [0,1] and [1,0] predict no and yes. Query feature0=2 is unseen, so root frequencies [1/2,1/2] apply and sorted-class tie selects no. The separate encoded Play Tennis test verifies the known root information gain ≈0.24674982.

## 11. Time Complexity

Let b≤64 be observed categorical branching and c≤32 classes. At each node, grouping/entropy evaluation includes feature sorting/unique work, repeated equality masks and class counts. A conservative depth-d bound is O(dpn(log n+bc)), with d≤min(max_depth,p). Query branch lookup scans immutable tuples, costing O(mdb), plus O(mc) probability output. No binary-threshold search is claimed.

## 12. Space Complexity

Fit uses O(np) checked data, conservative O(nd) recursive index workspace and O(nodes·c) stored distributions. Every internal node has at least two nonempty children, so nodes≤2n−1. The fitted tree does not retain observations. Query copying/output costs O(mp+mc); immutable branches keep model state separate from caller arrays.

## 13. Python Implementation

`ID3Classifier(max_depth=5, min_samples_leaf=1, min_gain=0.0)` exposes fit, predict_proba, predict and accuracy score. Depth is a native int in 1..16, leaf size 1..256, gain threshold in [0,5] bits. Training n≤512,p≤32, at most 64 categories/column; shared cell/query/finite-magnitude caps apply. Features must be integer-valued numeric codes, including at query time. Labels are homogeneous int64-compatible integers or nonempty strings, at most 32 classes. Inspect tree_, depth_, n_leaves_; nodes contain distribution, sample count, entropy, chosen feature, immutable (value,child) branches and gain. Probability rows are empirical node/leaf frequencies, not calibrated guarantees. No continuous thresholds, pruning, weights or raw-string feature encoder.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/id3-decision-trees/python/example.py
```

Expected output:

```text
['no', 'yes']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import ID3Classifier
X = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
y = ["no", "no", "yes", "yes"]
model = ID3Classifier().fit(X, y)
print(model.predict([[0.0, 1.0], [1.0, 0.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/id3-decision-trees -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

Pure or constant-feature nodes become leaves. Duplicate rows with conflicting labels can remain mixed after feature exhaustion. Zero-gain default splitting can resolve XOR; positive min_gain deliberately stops it. Unseen integer codes use current-node fallback. NaN/Inf, fractional category codes, bool/string/complex matrices, excessive categories, invalid labels/parameters and shape violations raise ValueError. Empty shaped queries work. Failed refits preserve prior trees and input mutation does not alter stored statistics.

## 17. Advantages

Authentic multiway category handling with visible entropy/gain calculations, deterministic ties and a specified unseen-category policy. Feature removal and depth/sample controls bound construction. Independent exhaustive grouping tests can verify split decisions without borrowing another tree implementation.

## 18. Disadvantages and Limitations

Raw information gain favors high-cardinality attributes; a unique identifier can overfit perfectly. Greedy splitting misses some globally better trees. This version has no pruning, missing-value routing, sample weights, raw categorical encoding or continuous thresholding. Depth limits and min_gain controls intentionally modify unrestricted tree growth. Node frequency probabilities need calibration evaluation.

## 19. When to Use It

Use it for a small clearly categorical educational problem with a fixed training-fitted code map. Select limits using validation data, inspect branch populations and evaluate unseen-category fallback on a held-out split with class-specific metrics. Keep identifiers out of the representation unless their predictive use is justified.

## 20. When Not to Use It

Do not treat arbitrary real-valued measurements as categories by silently rounding them. Do not assign held-out unseen values to an arbitrary child or infer that perfect training fit establishes generalization. If continuous thresholds or gain-ratio selection are intended, use the separately documented C4.5-style topic.

## 21. Comparison With Related Algorithms

| Tree | Split semantics |
| --- | --- |
| ID3 | Multiway categorical equality; maximum information gain |
| CART | Binary numeric thresholds; Gini |
| C4.5 style | Mixed equality/thresholds; gain ratio and explicit correction/filter |
| Regression CART | Mean targets and squared-error reduction |

## 22. Interview Questions

Derive information gain from weighted conditional entropy. Why does a high-cardinality identifier attract ID3? How does feature removal guarantee termination? What distribution should an unseen category use? Why can zero-gain splitting matter for an interaction?

## 23. Practice Problems

1. Trace the dry run and an unseen root category by hand.
2. Build a unique identifier plus a meaningful binary predictor and compare ID3's gain choice with C4.5's gain ratio.
3. Verify every root candidate on a fixed-seed categorical dataset using an independent Counter/log₂ calculation, then evaluate bounded depth on held-out rows.

## 24. References

- [Quinlan, Induction of Decision Trees (1986)](https://doi.org/10.1007/BF00116251).
- [Quinlan, Improved Use of Continuous Attributes in C4.5 (1996)](https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume4/quinlan96a.pdf), for the successor's distinct split criteria.

There is no direct scikit-learn ID3 equivalent used as an oracle. Tests independently calculate entropy/information gain across 60 seeded tiny datasets and verify categorical examples and unseen-value behavior.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
