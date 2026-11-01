# Isolation Forest

## 1. Algorithm Name

Isolation Forest scores observations by how quickly random axis-aligned partitions isolate them. The core builds genuine randomized isolation trees;it does not train supervised CART or replace isolation with a distance heuristic.

## 2. Overview

Fit a forest of randomly subsampled isolation trees to an unlabeled finite feature matrix. Estimate corrected expected path length and convert it to the original paper anomaly score. Short paths indicate easier isolation,not a calibrated probability of being anomalous.

## 3. Problem Statement

fit(X) accepts1..256 rows and1..32 features,finite real numeric magnitudes<=1e12. n_estimators1..128;max_samples is auto or integer1..n;max_depth isNone or integer0..32;random_state is0..2**32-1. contamination is auto or a finite fraction in(0,.5]. Queries preserve feature count and allow0..1024 rows. No bootstrap or feature-subset option is claimed.

trees_ contains frozen nodes with sample counts,depths,feature,split and two children;sample_indices_ records owned no-replacement subsamples. anomaly_scores(X) is positive high=anomalous;score_samples(X) is its negative. decision_function=threshold_-anomaly_score;predict returns+1 for decision>=0,-1 otherwise. anomaly_scores_,training_path_lengths_,threshold_,labels_ describe training. Constructed trees have no numerical optimizer convergence claim.

## 4. Why Do We Need This Algorithm?

Unlabeled observations may be unusual because simple random partitions isolate them quickly. A forest averages that isolation mechanism without requiring a supervised anomaly label or substituting a global distance-to-center rule.

## 5. Real-World Applications

Small unlabeled tabular screening and interpretable anomaly-ranking exercises are suitable applications when easier isolation is a plausible anomaly assumption. Validate thresholds and unseen-query behavior using a declared evaluation protocol.

## 6. Core Intuition

For leaf size m,c(0)=c(1)=0,c(2)=1,and c(m)=2*sum(1/j,j=1..m-1)-2*(m-1)/m. A path contributes traversed edges+c(leaf_size). For subsample size psi,raw anomaly score is2**(-mean_tree_path/c(psi)). Harmonics use actual finite sums rather than logarithmic approximations. psi1 has no meaningful normalization,so the declared neutral score is.5 for every supported query.

An isolated extreme observation can often be separated with a few random cuts. Dense observations usually survive more cuts or terminate in a multi-observation leaf. The leaf correction estimates unresolved additional path length when construction stops early.

## 7. Prerequisites

Binary trees,random sampling without replacement,axis-aligned partitions,harmonic sums and finite-precision bounds are prerequisites. Understand score orientation,training-only threshold calibration and the difference between anomaly ranking and probability calibration.

## 8. Step-by-Step Working Process

For each tree,sample psi row indices without replacement using a private generator. At each node choose uniformly among varying features,then draw a uniform split between its observed extremes. Repair only a floating endpoint to the next representable value above the minimum so both branches remain nonempty. Recurse until the height limit,singleton or all-constant state. Score each query by actual traversal and harmonic leaf correction;average paths before exponentiation.

## 9. Pseudocode

```text
for each tree:
    subset <- random sample without replacement
    build(subset,depth):
        if stopping condition:return leaf(count,depth)
        feature <- uniform among nonconstant columns
        split <- uniform feature-range cut with float endpoint repair
        return node(build(left),build(right))
for query:
    path <- mean(edges+c(leaf count) over trees)
    raw <- 2**(-path/c(subsample size))
return threshold-raw and signed labels
```

## 10. Dry Run

A manually specified root splits at0. Its left leaf has count2 at depth1;the right branch splits at2,ending with counts1 and2 at depth2. Query positions-1,1,3 have corrected paths2,2,3. The test supplies these expected values directly,with c(2)=1;the independent ensemble oracle separately traverses trees and evaluates rational harmonic sums.

## 11. Time Complexity

Let t be tree count,psi subsample size,d feature count,L maximum depth,n training rows and m query rows. Building costs O(t*psi*d*L) worst case for bounded partition scans;balanced trees with L around log2(psi) have O(t*psi*d*log psi) work. Training-score calibration adds O(t*n*(d+L+psi)+n log n),including repeated validated feature copies and leaf corrections. Query scoring costs O(t*m*(d+L+psi)). This implementation recomputes small harmonic sums per leaf,adding at most O(psi) per traversal;with fixed psi<=256 this is a bounded constant,but the conservative scoring bound includes both this harmonic term and repeated O(m*d) feature validation/copies.

## 12. Space Complexity

A proper binary tree has at most2*psi-1 nodes;forest storage is O(t*psi),plus O(t*psi) sample-index diagnostics. Recursive partition buffers cost O(psi*d*L) conservatively;depth is capped32. Training scoring materializes t-by-n path diagnostics transiently;query scoring similarly uses O(t*m),with bounded t,n,m.

## 13. Python Implementation

The canonical [IsolationForest](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B12 contracts](../../../docs/anomaly-detection-conventions.md) define validation and ownership. No ready-made anomaly detection estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/anomaly-detection/isolation-forest/python/example.py
```

Actual captured output:

```json
{"training": [[-0.2, 0.0], [0.1, 0.1], [0.0, -0.1], [0.2, 0.0], [-0.1, 0.2], [0.1, -0.2], [4.0, 4.0], [5.0, 4.0]], "roots": [{"feature": 0, "split": 3.660871, "count": 8, "left": 6, "right": 2}, {"feature": 0, "split": 3.141524, "count": 8, "left": 6, "right": 2}, {"feature": 1, "split": 1.15935, "count": 8, "left": 6, "right": 2}], "scores": [0.51150878, 0.42158579, 0.42873353, 0.45952177, 0.47125756, 0.45855709, 0.65961136, 0.65961136], "threshold": 0.54853442, "decisions": [0.03702565, 0.12694864, 0.1198009, 0.08901265, 0.07727687, 0.08997734, -0.11107694, -0.11107694], "labels": [1, 1, 1, 1, 1, 1, -1, -1], "status": "constructed"}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/anomaly-detection/isolation-forest -q`.

## 16. Edge Cases

One sample and max_samples1 return neutral.5. Two-sample,all-identical,duplicate and constant-feature data are supported. Constant features are excluded from split selection;all-constant nodes stop. max_depth0 gives one corrected root leaf and neutral.5 scores. Adjacent floats and tiny/subnormal spans still yield nonempty children. Invalid counts,depths,dimensions,nonfinite data or contamination fail;an invalid refit preserves the old forest.

## 17. Advantages

The random partition mechanism and sample/depth diagnostics are easy to inspect. Expected path calculations are independently auditable. The model reuses existing validation while keeping isolation-tree construction mathematically distinct from supervised trees.

## 18. Disadvantages and Limitations

Axis-aligned isolation is sensitive to coordinate representation and irrelevant features;random finite forests do not guarantee every anomaly ranks highest. Exact harmonic corrections and variable-feature selection differ from some library details,so randomized forests are not bitwise-equivalent. Constant/degenerate data carry no meaningful separation. Contamination is a training cutoff assumption,not the true anomaly rate. No novelty calibration or probabilistic calibration guarantee is claimed.

## 19. When to Use It

Use as an unlabeled baseline when unusual points are plausibly easier to isolate than common points. Fit preprocessing only on training data if the application needs it;this canonical performs no implicit normalization. Inspect ranking and out-of-sample labels using a declared threshold.

## 20. When Not to Use It

Avoid treating raw scores as probabilities or expecting exact requested outlier counts under tied scores. Density-relative anomalies may be better explained with tie-inclusive LOF;smooth kernel support estimation is the separate One-Class SVM canonical.

## 21. Comparison With Related Algorithms

Isolation Forest builds randomized partitions;One-Class SVM optimizes a constrained kernel dual;LOF compares local reachability densities. Only the first two support unseen query inference here. No supervised labels enter forest construction.

## 22. Interview Questions

Why correct a multi-sample leaf? A depth-limited tree has unresolved isolation work. Why average paths before the exponential? That is the paper score definition. Why may contamination.5 produce zero outliers on identical data? Every score is tied at the boundary and ties are inliers.

## 23. Practice Problems

Hand-compute rational c(3) and c(4). Traverse a manual tree with multiple leaf sizes. Inspect all sampled indices and both child counts. Compare fixed-seed rankings over three declared synthetic datasets. Verify that a constant column is never selected and explain why bitwise sklearn parity is not expected.

## 24. References

[https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)

[https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)

The [phase conventions](../../../docs/anomaly-detection-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

