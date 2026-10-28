# C4.5 Decision Trees

## 1. Algorithm Name

**C4.5 Decision Trees**, canonical `c4-5-decision-trees` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

This educational C4.5-style classifier combines categorical multiway tests, continuous thresholds, information gain and gain ratio. It includes an optional MDL-inspired threshold charge and an average-positive-gain feature filter. It explicitly rejects missing values and performs no pruning or fractional missing-value routing; it does not claim full historical C4.5 compatibility.

## 3. Problem Statement

At node S, entropy H=−Σpklog₂pk. For candidate groups Sv, raw gain G=H−Σv(|Sv|/|S|)H(Sv), and split information SI=−Σv(|Sv|/|S|)log₂(|Sv|/|S|). Categorical columns create one group per observed integer code. Continuous columns use binary ≤t and >t groups, choosing the threshold with maximum raw gain. With MDL enabled and q distinct continuous values, adjusted gain A=G−log₂(q−1)/|S|; categorical A=G. Ratio R=A/SI. Constant columns are skipped. Among positive feasible feature candidates, filter A≥their mean (within 10⁻¹⁴) and A≥min_gain, then choose largest ratio, ties by original feature order.

## 4. Why Do We Need This Algorithm?

ID3's raw information gain can prefer a unique identifier that fragments rows into tiny groups. Dividing by split information reduces that attraction, while a gain filter avoids choosing an almost uninformative but artificially high-ratio split. Continuous features also offer many thresholds, motivating an explicit threshold-choice complexity charge.

## 5. Real-World Applications

Examples include a small mixed numerical/categorical rule-learning problem with a known code map or studying how gain ratio changes an ID3 split. This lesson is a controlled educational variant; production missing-value routing, confidence-based pruning and rule extraction require additional separately tested logic.

## 6. Core Intuition

Raw gain measures class uncertainty reduction; split information measures how much a partition distinguishes groups regardless of class. Their ratio changes the selection preference. The MDL-inspired subtraction penalizes choosing among many possible continuous thresholds. Selection is still greedy: these corrections change a local score, not a proof of best whole-tree classification.

## 7. Prerequisites

Understand [ID3 entropy/information gain](../id3-decision-trees/README.md), binary threshold search, conditional distributions and model complexity. The scalar entropy helper is explicitly reused from canonical ID3; C4.5's mixed split enumeration, ratio, filter, correction and routing are implemented here. [CART](../cart-decision-trees/README.md) provides a different Gini-based numeric tree.

## 8. Step-by-Step Working Process

1. Validate/copy X and labels. Capture the explicit categorical column indices; those columns require integer codes and at most 64 observed categories. Other columns remain continuous. Reject all NaN/Inf; there is no missing-value imputation.
2. At each node compute class frequencies and entropy. Stop at purity, depth/sample limits or no eligible positive-gain candidate.
3. For an unused categorical feature, form all observed-value groups, require every child to meet min_samples_leaf, and calculate gain/split information.
4. For each continuous feature, stable-sort observations and scan distinct adjacent boundaries with class-count updates. Choose the first maximum raw information gain threshold; use a lower-endpoint fallback if midpoint rounding would empty a child. Continuous features may be reused at deeper levels.
5. Optionally subtract log₂(q−1)/node_size from continuous gain, where q is the number of distinct node values, including candidate boundaries disallowed by the leaf-size constraint. Exclude adjusted gain≤10⁻¹⁴. Average the remaining per-feature adjusted gains, retain those above that mean and min_gain, and choose the first materially largest adjusted-gain/split-information ratio.
6. Build children; categorical features cannot be reused on their descendant path. Store immutable nodes and commit only after success. Queries follow thresholds/equalities; unseen categorical values return the current node distribution.

This precise average-positive-feature filter and finite resource controls define the variant. Pruning, fractional unknown-value routing, categorical subset grouping and full release-specific historical behavior are omitted.

## 9. Pseudocode

```text
BUILD(rows, used_categorical_columns, depth):
  calculate entropy/distribution; stop at purity or bounds
  for feature in original order:
    categorical: multiway equal-code groups and raw gain
    continuous: best raw-gain threshold and optional MDL charge
    calculate adjusted gain and split information
  keep positive candidates above mean adjusted gain and min_gain
  select first maximum adjusted_gain/split_information
  recursively build children; mark categorical feature used
QUERY: follow thresholds or categories; unseen category uses current distribution
```

## 10. Dry Run

With continuous x=[0,1,2,3] and labels [0,0,1,1], root entropy is one bit. Threshold 1.5 gives pure equal children, raw gain 1 and split information 1. There are q−1=3 possible distinct-value thresholds, so default adjusted gain and ratio are 1−log₂(3)/4≈0.603759. With correction disabled the ratio is one. In the runnable mixed example, categorical feature0 perfectly divides no/yes groups and wins; query code 2 is unseen and uses root [1/2,1/2], selecting no by sorted-class tie. A unique eight-valued identifier has raw gain one but ratio 1/log₂8=1/3, while a perfectly informative binary category has ratio one.

## 11. Time Complexity

For n rows,p features,c≤32 classes and b≤64 categorical branches, a conservative depth-d bound is O(dpn(log n+bc)). Numeric scans update class counts and evaluate O(c) entropy; categorical grouping uses repeated equality masks. d≤16 bounds recursion. Query cost is O(mdb) for tuple-based categorical lookup, plus O(mc) probability output; continuous routing is constant work per visited node.

## 12. Space Complexity

Training uses O(np) checked data and conservative O(nd) recursive indices/workspace, plus O(nodes·c) fitted node distributions. Nonempty child groups imply nodes≤2n−1. Fitted nodes retain split statistics, thresholds or categorical values and immutable children, not original observations. Query copies and probability output use O(mp+mc). No external model binary or dataset is stored.

## 13. Python Implementation

`C45Classifier(categorical_features=None, max_depth=5, min_samples_leaf=1, min_gain=1e-12, mdl_correction=True)` exposes fit/predict/predict_proba/accuracy score. None means all columns continuous; categorical_features is a unique list/tuple of native integer column indices. Depth is 1..16, leaf size 1..256, min_gain in [0,5] bits and correction strictly bool. Fit n≤512,p≤32; shared cell/magnitude/query limits apply. Categorical columns require integer-valued numeric codes and ≤64 observed values; class labels use the common homogeneous int64/string contract with ≤32 classes. Inspect categorical_features_, tree_, depth_, n_leaves_, mdl_correction_, missing_values_="reject" and pruning_="none". Nodes expose gain, adjusted_gain, split_information and gain_ratio. Output probabilities are empirical fallback/leaf frequencies, not calibrated guarantees.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/c4-5-decision-trees/python/example.py
```

Expected output:

```text
['no', 'yes', 'no']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import C45Classifier
X = [[0.0, 0.0], [0.0, 1.0], [1.0, 2.0], [1.0, 3.0]]
y = ["no", "no", "yes", "yes"]
model = C45Classifier(categorical_features=[0]).fit(X, y)
print(model.predict([[0.0, 99.0], [1.0, -1.0], [2.0, 2.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/c4-5-decision-trees -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

Pure/constant features or zero split information produce leaves without division by zero. Repeated continuous values are never separated arbitrarily. Zero adjusted gain stops construction, so a pure XOR interaction may remain invisible at its root. Unseen categories use node-majority fallback; missing/fractional categorical values are errors. Invalid dimensions, indices, bool/complex/string matrices, unsupported labels and numerical/resource violations fail explicitly. Empty shaped queries work; a failed refit preserves old state and caller mutations cannot alter stored nodes.

## 17. Advantages

Genuine mixed-feature equality/threshold handling and a transparent distinction between entropy gain, split information and gain ratio. The correction/filter and fitted diagnostics are visible and independently testable. Deterministic ties and bounded depth keep the experiment reproducible.

## 18. Disadvantages and Limitations

This is a C4.5-style subset, not a full historical implementation. No post-pruning, fractional missing routing, categorical subset grouping, sample weights or rule extraction. Greedy choices and the stated gain filter can underfit interactions or overfit noise. MDL correction may suppress small-data continuous splits. Leaf frequency probabilities and successful construction are not calibration or generalization certificates.

## 19. When to Use It

Use it to compare information-gain versus gain-ratio behavior on a small explicit mixed-feature dataset. Fit category mapping/preprocessing solely on training rows and validate depth, leaf size and correction choices without test leakage. Inspect the root's raw/adjusted statistics and evaluate held-out class metrics.

## 20. When Not to Use It

Do not claim complete C4.5 compatibility or silently route NaN values through an arbitrary branch. Do not treat arbitrary category codes as continuous merely because they are numbers; supply categorical_features. If the task depends on historical pruning or unknown-value behavior, this educational scope is insufficient.

## 21. Comparison With Related Algorithms

| Tree | Selection/representation |
| --- | --- |
| ID3 | Categorical raw information gain, no ratio/threshold correction |
| CART | Binary numeric Gini reduction |
| This C4.5 style | Mixed groups, adjusted gain ratio and explicit gain filter |
| Full historical C4.5 | Additional pruning/unknown-value/release-specific behavior omitted here |

## 22. Interview Questions

Why can gain ratio reduce identifier preference? Why filter low-gain candidates first? Derive the four-row MDL adjustment. Explain categorical feature removal versus continuous reuse. What is the documented behavior on an unseen category, a missing value and zero adjusted gain?

## 23. Practice Problems

1. Compute gain, split information and ratio for an identifier and a meaningful binary feature.
2. Enumerate all tiny continuous thresholds, apply the explicit correction/filter and verify the chosen root.
3. Compare correction on/off using fixed train/validation/test splits, recording tree size and held-out macro F1 without claiming universal superiority.

## 24. References

- [Quinlan, Improved Use of Continuous Attributes in C4.5 (1996)](https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume4/quinlan96a.pdf).
- [Quinlan, Induction of Decision Trees (1986)](https://doi.org/10.1007/BF00116251).

Primary references motivate the criteria; all source and prose here are independently written. There is no scikit-learn C4.5 oracle claimed. Tests independently enumerate mixed-feature candidate statistics on 100 seeded datasets, plus exact correction, cardinality, fallback and zero-information cases.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
