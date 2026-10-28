# CART Decision Trees

## 1. Algorithm Name

**CART Decision Trees**, canonical `cart-decision-trees` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

Classification CART recursively divides numeric feature space with binary threshold tests and predicts a class-frequency distribution at each leaf. This implementation uses Gini impurity, distinct from the squared-error regression tree. Stable split enumeration and explicit depth/sample controls make the greedy construction reproducible and bounded.

## 3. Problem Statement

For node S with c class counts nk and size s, let pk=nk/s and G(S)=1−Σpk². For feature j and threshold t, L={i:Xᵢⱼ≤t}, R={i:Xᵢⱼ>t}. Minimize weighted child impurity W=(|L|G(L)+|R|G(R))/s over eligible distinct adjacent values. Both children need min_samples_leaf rows. Split only if (s/n_total)(G(S)−W)≥min_impurity_decrease. Predict the first sorted class with maximum leaf frequency; probability columns follow classes_.

## 4. Why Do We Need This Algorithm?

A single linear boundary misses some interactions and sharp threshold changes. CART learns piecewise class regions without prescribing a polynomial basis. Gini impurity measures class mixing, so its criterion applies directly to multiclass labels without treating their integer encodings as ordered numerical targets.

## 5. Real-World Applications

Examples include a small interpretable threshold classifier or exploring interactions in numeric measurements. Leaf frequencies help explain a prediction, but are empirical estimates and not automatically calibrated probabilities. Deep trees can memorize noise; useful rules need held-out evaluation and sensible sample constraints.

## 6. Core Intuition

A pure node has Gini zero; splitting cannot improve its class purity. For a mixed node, every threshold between distinct sorted values defines a possible binary partition. Maintaining class counts on each side permits direct evaluation of the weighted Gini score. Greedy immediate purity improvement does not guarantee the globally best tree.

## 7. Prerequisites

Know binary trees, recursion, stable sorting, categorical label counts and weighted averages. [Regression CART](../../regression/decision-tree-regression/README.md) predicts means and uses squared error; this topic instead predicts classes and uses Gini. [ID3](../id3-decision-trees/README.md) uses categorical multiway information gain.

## 8. Step-by-Step Working Process

1. Copy/validate numeric observations and encode sorted classes. Start at depth zero with all indices.
2. Store node class frequencies and Gini. Stop at purity, max_depth or fewer than twice min_samples_leaf rows.
3. For each feature in original order, stable-sort rows and move class counts from right to left across every eligible boundary between distinct values. Compute weighted child Gini.
4. Keep the first materially best score; differences within 10⁻¹⁴ are ties. Choose the midpoint threshold; if rounding reaches the upper value, use the lower endpoint to keep children nonempty.
5. Check the root-normalized impurity reduction. Zero-gain splits are allowed when min_impurity_decrease=0, so a later XOR interaction can become visible.
6. Recursively construct children and commit frozen nodes only after success. Predict by following ≤ left and > right, then return leaf frequencies or their first maximum.

Depth/sample bounds guarantee termination. converged_ records completed construction, not global optimization. No differentiable gradient or iterative convergence criterion applies.

## 9. Pseudocode

```text
BUILD(rows, depth):
  counts = class_counts(rows); distribution = counts/len(rows)
  if pure, depth limit or insufficient rows: return leaf(distribution)
  for feature in original order:
    stable-sort; increment left class counts across distinct-value boundaries
    score = size_weighted_child_gini
    retain first materially smallest eligible score
  if no split or root_normalized_gain < threshold: return leaf(distribution)
  return threshold_node(BUILD(left), BUILD(right))
PREDICT(row): traverse binary comparisons; select leaf distribution maximum
```

## 10. Dry Run

For x=[0,1,2,3], labels [a,a,b,b], root frequencies [1/2,1/2] give Gini 1−1/4−1/4=1/2. Threshold 1.5 gives pure children and weighted impurity zero. Thresholds 0.5 or 2.5 instead give (3/4)(1−(2/3)²−(1/3)²)=1/3. Thus 1.5 wins. Its root-normalized reduction is 1/2; a threshold of 0.5 permits the split and 0.50001 rejects it. Queries 0.5 and 2.5 have leaf probabilities [1,0] and [0,1], predicting a and b.

## 11. Time Complexity

At a node with s rows, sorting costs O(ps log s) and scanning count-based scores O(psc). For actual depth d, a conservative bound is O(dpn(log n+c)); d≤16 and c≤32. Query routing costs O(md), plus O(mc) to return probability rows. This implementation sorts at each node and does not claim a globally presorted optimization.

## 12. Space Complexity

Fit retains O(np) checked input, O(nd) conservative recursive-index workspace and O(nodes·c) node distributions. Nonempty disjoint children imply at most 2n−1 nodes. After fit the model keeps only its nodes/classes, not training rows. Query copying and probabilities cost O(mp+mc); traversal is iterative.

## 13. Python Implementation

`CARTClassifier(max_depth=5, min_samples_leaf=1, min_impurity_decrease=0.0)` supports multiclass fit/predict/predict_proba/accuracy score. Depth is a native integer 1..16, leaf size 1..1024 and minimum root-normalized reduction in [0,1]. Fit n≤2048,p≤32; shared cell/magnitude/query caps apply. Labels are homogeneous int64-compatible integers or nonempty strings, at most 32 classes; one class is permitted. Inspect tree_, depth_, n_leaves_ and n_features_in_. Frozen nodes store distribution tuples, sample count, impurity, feature/threshold and children. Probability outputs(m,c) are empirical leaf frequencies; predictions(m,) retain original labels. No pruning, sample weights or categorical/missing-value inference.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/cart-decision-trees/python/example.py
```

Expected output:

```text
['a', 'b']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import CARTClassifier
X = [[0.0], [1.0], [2.0], [3.0]]
y = ["a", "a", "b", "b"]
model = CARTClassifier(max_depth=1).fit(X, y)
print(model.predict([[0.5], [2.5]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/cart-decision-trees -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

Pure data, contradictory duplicates and constant features yield valid leaves. Equal class frequencies choose the first sorted label. XOR can need a zero-gain first split; a positive minimum-gain threshold deliberately prevents it. Adjacent float values use the lower-endpoint fallback. Empty shaped queries work. Invalid dimensions/parameters/domains, NaN/Inf or oversized data raise ValueError. Failed refits preserve prior trees; caller mutation cannot alter frozen leaf statistics.

## 17. Advantages

Handles multiclass nonlinear threshold interactions with directly inspectable nodes, empirical probabilities and deterministic ties. No feature-unit regularization or optimizer tuning is needed. Independent exhaustive Gini enumeration can verify the greedy decision on tiny datasets.

## 18. Disadvantages and Limitations

Greedy selection is not global tree optimization. Deep trees overfit, boundaries are discontinuous, and small data changes can alter the structure. Leaf frequencies can be poorly calibrated or based on few rows. Numerical tie conventions may differ from libraries; tied partitions need objective-based comparison. No cost-complexity pruning, missing-value routing, categorical handling, weights or ensembles are implemented.

## 19. When to Use It

Use it as a bounded interpretable numeric classifier. Select depth/leaf size on validation data, inspect leaf populations and compare held-out confusion/precision/recall/F1 and log loss. Preprocessing must still avoid test leakage even though monotone feature scaling does not change ordering-based candidate partitions in exact arithmetic.

## 20. When Not to Use It

Do not interpret threshold rules as causal laws or demand smooth decision derivatives. Avoid arbitrarily deep memorization or coding unordered categories as meaningful numeric thresholds without a modeling decision. Use ID3/C4.5 for the explicit categorical contracts in this category.

## 21. Comparison With Related Algorithms

| Tree/model | Difference |
| --- | --- |
| Regression CART | Squared-error means, not class Gini/distributions |
| ID3 | Multiway categorical information gain |
| C4.5 style | Entropy/gain ratio with continuous and categorical tests |
| Logistic Regression | One affine binary probability boundary |

## 22. Interview Questions

Derive the dry-run weighted Gini scores. Why must label codes not be treated as ordered regression targets? Explain root-normalized minimum reduction. Why can a zero-gain split help XOR? What should a reference comparison do when multiple equally good splits exist?

## 23. Practice Problems

1. Enumerate all thresholds on a small three-class dataset.
2. Compare a depth-one and depth-two tree on XOR.
3. Select depth/leaf size with a fixed validation split and report held-out metrics and tree size without test-set tuning.

## 24. References

- [scikit-learn tree mathematical formulation and Gini criterion](https://scikit-learn.org/1.8/modules/tree.html#mathematical-formulation).

Tests use an independent Counter-based brute-force Gini oracle on 70 seeded multiclass datasets. Library comparisons use one-feature partitions with controlled split behavior instead of assuming identical random tie choices.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
