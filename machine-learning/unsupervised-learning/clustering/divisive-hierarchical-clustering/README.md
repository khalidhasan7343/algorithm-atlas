# Divisive Hierarchical Clustering — DIANA

## 1. Algorithm Name

Divisive Hierarchical Clustering — DIANA

## 2. Overview

Build a complete top-down Euclidean hierarchy using DIANA splinter groups. Repeatedly divide the largest-diameter active group, seed a splinter with its most dissimilar observation and move observations that are closer on average to the splinter than to the remaining group. This is not bisecting K-Means.

## 3. Problem Statement

All fitting inputs are dense finite real numeric X=(n_samples,n_features);
1D X, booleans, strings, complex numbers, missing/infinite values and implicit
reshaping are rejected. Numeric features have magnitude <=10^12. Standard limits
are n<=512,p<=32; hierarchical and spectral/density methods state tighter limits
below. Prediction, when defined, requires the fitted feature count and at most
4096 rows; empty query matrices are supported. No supervised target y is consumed.
Caller inputs and global NumPy RNG state are unchanged. Failed fits do not replace
an earlier complete fitted state. See the exact task-specific API below.

DivisiveClustering(n_clusters=2) provides fit and fit_predict; K is a native integer 1..n, n<=128,p<=32. Outputs labels_, full splits_ including seed/move diagnostics, conventional reversed children_/distances_/counts_, and n_leaves_. No out-of-sample predict is defined for this transductive hierarchy.

## 4. Why Do We Need This Algorithm?

A top-down view starts with a broad population and asks which observation/group most strongly separates from it. Its dissimilarity-based division can reveal a different nested structure from bottom-up linkage merging or centroid optimization.

## 5. Real-World Applications

A small table of numeric profiles can be explored as successive broad-to-specific divisions. The stored splinter trace supports explaining which profile first separated and which joined it. Euclidean scaling must be justified; the implementation does not infer semantic categories, support mixed categorical dissimilarities or claim automatic optimal cuts.

## 6. Core Intuition

The most dissimilar row starts a splinter. Compare each remaining row’s mean distance to its own remainder, excluding itself, with its mean distance to the splinter. Positive difference favors moving it. Repeat while a resolved positive move exists, then retain both nonempty children.

For remaining group R and splinter S, delta(i)=mean_{j in R,j!=i}d(i,j)-mean_{j in S}d(i,j). Move the largest positive delta with first-row ties. Seed selection maximizes average distance to the parent’s other rows. Selecting the largest current diameter gives a nonincreasing split-height schedule; reversing it yields ordinary nondecreasing hierarchy heights.

## 7. Prerequisites

Dissimilarity matrices, means of pairwise distances, partitions and hierarchical trees. Read [ML development](../../../../docs/ml-development.md), [current scope](../../../../docs/clustering-scope.md) and [numerical contracts](../../../../docs/clustering-conventions.md).

## 8. Step-by-Step Working Process

1. Validate finite Euclidean data and K; start with the whole observation set.
2. Among nonsingleton active groups choose the largest diameter, breaking ties by smallest original row index.
3. Seed the splinter with the first row maximizing average dissimilarity to other parent members.
4. While at least two rows remain outside the splinter, compute each delta, choose the greatest and move it only if greater than 32*machine_epsilon*parent_diameter.
5. Record both children, parent diameter, initial seed and all accepted moves. Both children remain nonempty.
6. Capture the requested K-group cut but continue until every observation is a singleton.
7. Reverse the split schedule to construct leaf-ID children, heights and counts. Label the captured cut by smallest member index.

All loops/recursion are bounded by explicit data/iteration limits. Fitted arrays and diagnostics are copied into state only after the full procedure succeeds.

## 9. Pseudocode

```text
groups <- one group containing all rows
while a nonsingleton group exists:
    parent <- largest-diameter active group
    S <- most-average-dissimilar row
    R <- other rows
    while |R|>1 and max delta(i)>roundoff_threshold:
        move best row from R to S
    record parent -> (R,S), seed and moves
    replace parent; save cut at K groups
reverse split schedule to expose conventional hierarchy arrays
```

## 10. Dry Run

For X=[0,2,10,12], diameter is 12. Rows 0 and 12 tie for greatest average dissimilarity, so row 0 seeds the splinter. For row 2, distance to the remaining rows 10 and 12 averages 9, while distance to splinter row 0 is 2: delta=7, so it moves. Remaining [10,12] do not prefer [0,2]. The K=2 labels are [0,0,1,1]; full reversed split heights are [2,2,12].

## 11. Time Complexity

Let n<=128,p<=32. Stable pairwise distances require O(n²p). The intentionally direct nested splinter scans have a conservative O(n^4+n²p) worst-case bound; no optimized DIANA runtime is claimed. Every split strictly increases active group count, so there are exactly n-1 bounded splits. Best-case moves stop immediately, but a full hierarchy is still built.

## 12. Space Complexity

The distance matrix uses O(n²); active memberships use O(n). Retained parent/child membership tuples and move diagnostics can require O(n²) in an unbalanced hierarchy, while conventional children/heights/counts use O(n). No unbounded recursion is used.

## 13. Python Implementation

The from-scratch implementation is [python/solution.py](python/solution.py), with reusable `DivisiveClustering` and the API described above. [python/example.py](python/example.py) is a fixed executable example. Core logic uses NumPy/local code, never a scikit-learn/SciPy estimator. Shared [support.py](../support.py) supplies strict contracts and stable Euclidean distances. Tests are in [tests/test_python.py](tests/test_python.py). Install [requirements-ml.txt](../../../../requirements-ml.txt) for runtime; use [requirements-ml-test.txt](../../../../requirements-ml-test.txt) for reference tests.

## 14. C++ Implementation

Classical ML has a Python-first policy. Optional C++ is **not implemented** here; there are no dummy C++ source/test files. DSA remains Python/C++ mandatory, with actual C++17/C++20 validation. This status is explicit in the catalog rather than represented by a fake implementation.

## 15. Input and Output Examples

From the repository root with the existing ML environment:

```sh
python machine-learning/unsupervised-learning/clustering/divisive-hierarchical-clustering/python/example.py
```

The independently justified labels are `[0, 0, 1, 1]`. Cluster IDs are conventional, not class meanings; the dry run explains their ordering. Equivalent Python API, from this topic's python directory:

```python
from solution import DivisiveClustering
model = DivisiveClustering(**{'n_clusters': 2})
labels = model.fit_predict([[0], [2], [10], [12]])
```

The JSON CLI accepts exactly X and optional parameters and prints a labels object. Invalid input exits 2 with stderr and no labels JSON. Numeric comparisons use tolerances; exact labels are used only when the example/tie rule fixes them.

## 16. Edge Cases

K=1 captures the whole set; K=n captures all singleton rows. One row has no splits and an empty (0,2) child array. Constant duplicates still split by deterministic row ties, with zero heights and no positive splinter moves. Tiny positive diameters are compared in distance units rather than squared units. Near-zero move gains can be unresolved at float64 precision.

Predict/transform before fit, where those methods exist, raises ValueError. Invalid hyperparameters are checked again at fit. Exhausted iterative fitting is not silently returned as converged. Unsupported keywords fail rather than being ignored.

## 17. Advantages

Exposes a genuine top-down dissimilarity method and its complete decision trace, allowing independent checks of every splinter choice.

## 18. Disadvantages and Limitations

Dense Euclidean only; no arbitrary dissimilarity input, mixed metrics, standardization, automatic cut selection or production optimization. Greedy splinter divisions are not globally optimal partitions. Ties depend on row indices; do not assert identical internals against a different tie policy. There is no installed direct DIANA reference used here; mathematical trace oracles follow the documented R/cluster definition.

## 19. When to Use It

Use for small datasets where top-down divisions and explainable pairwise-dissimilarity decisions are central.

## 20. When Not to Use It

Avoid large data, required online prediction, an SSE-minimizing partition objective or applications requiring arbitrary nonnumeric dissimilarities.

## 21. Comparison With Related Algorithms

| Method | Construction |
| --- | --- |
| DIANA | Top-down diameter/splinter dissimilarity divisions |
| Agglomerative | Bottom-up chosen-linkage merges |
| Bisecting K-Means | Top-down centroid SSE subdivision; different algorithm |

## 22. Interview Questions

1. Why is self excluded from the remainder mean?
2. Compute the delta=7 move in the example.
3. Why does splitting strictly terminate after n-1 divisions?
4. Why is bisecting K-Means not a valid implementation substitute?

## 23. Practice Problems

1. Reconstruct every recorded splinter move from independent distance sums.
2. Derive a reversed hierarchy for three duplicate rows.
3. Compare DIANA and Ward cuts on the same data without requiring equality.

Validation commands, from the root:

```sh
python -m pytest machine-learning/unsupervised-learning/clustering/divisive-hierarchical-clustering -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
```

Oracles use independent formulas, exhaustive tiny cases or separately fitted references. Different valid labelings/trees/eigenvector signs are compared through the appropriate invariants. Marker groups overlap and are not additive. Seeds, data sizes and tolerances are fixed; no network dataset download or hidden library fit is used.

## 24. References

[R/cluster DIANA definition](https://stat.ethz.ch/R-manual/R-devel/library/cluster/html/diana.html).

References identify the mathematical method. The exact implemented subset, numeric domain, tie policy and unsupported features are stated here; external libraries can use different valid initialization, ordering, stopping or metric conventions.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE) · [Contribution guidance](../../../../CONTRIBUTING.md). Current Phase 16 review approval is pending.
