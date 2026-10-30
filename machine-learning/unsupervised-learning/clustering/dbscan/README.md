# DBSCAN — Euclidean density connectivity

## 1. Algorithm Name

DBSCAN — Euclidean density connectivity

## 2. Overview

Find connected dense regions using a fixed Euclidean neighborhood radius and a minimum number of neighboring observations. Distinguish core points, attached border points and noise. Neighborhood support includes the observation itself.

## 3. Problem Statement

All fitting inputs are dense finite real numeric X=(n_samples,n_features);
1D X, booleans, strings, complex numbers, missing/infinite values and implicit
reshaping are rejected. Numeric features have magnitude <=10^12. Standard limits
are n<=512,p<=32; hierarchical and spectral/density methods state tighter limits
below. Prediction, when defined, requires the fitted feature count and at most
4096 rows; empty query matrices are supported. No supervised target y is consumed.
Caller inputs and global NumPy RNG state are unchanged. Failed fits do not replace
an earlier complete fitted state. See the exact task-specific API below.

DBSCAN(eps=0.5,min_samples=5) provides fit and fit_predict. eps is finite real (0,10^12], and min_samples is a native integer 1..512; it may exceed n, yielding all noise. Data limits n<=512,p<=32. Outputs labels_ (-1 noise), core_sample_indices_, copied components_, neighbor_counts_ and n_clusters_. No new-row predict or centroid score is invented.

## 4. Why Do We Need This Algorithm?

Centroid partitions can cut across curved dense regions and force isolated observations into a group. Density connectivity instead permits nonconvex shapes and explicit noise, with radius/support choices that can be inspected directly.

## 5. Real-World Applications

Small coordinate or numeric-descriptor sets with compact dense regions and isolated measurements can illustrate noise-aware grouping. Feature units and eps must be chosen within training analysis; varying densities and high-dimensional neighborhoods require caution. This implementation is not an automatic anomaly detector or a production spatial index.

## 6. Core Intuition

A core point has at least min_samples observations within eps, including itself. Expand a cluster through neighboring core points, and attach their noncore neighbors as border observations. A noncore point inspected early as noise can later be reached as border; it must not expand a cluster by itself.

Define N_eps(i)={j:||x_i-x_j||<=eps}. Core(i) iff |N_eps(i)|>=min_samples. Connected components of the core-point radius graph determine dense cluster cores. Noncore neighbors attach to the first core component reaching them; nonneighbors remain -1. A border adjacent to two distinct core components has no unique density-component assignment.

## 7. Prerequisites

Euclidean neighborhoods, graph reachability, queues, connected components and the core/border/noise distinction. Read [ML development](../../../../docs/ml-development.md), [current scope](../../../../docs/clustering-scope.md) and [numerical contracts](../../../../docs/clustering-conventions.md).

## 8. Step-by-Step Working Process

1. Validate data, eps and support; compute stable Euclidean neighborhoods with an inclusive radius.
2. Mark cores from self-inclusive counts. Initialize all labels to noise and all rows unvisited.
3. Scan rows in input order. A noncore row can be marked visited noise, but does not start a component.
4. A core row starts a bounded queue with at most one queued occurrence per observation for that expansion.
5. Inspect each queued row; only newly visited cores add their neighbors to the queue.
6. Give an unlabeled/noise row the current cluster label, including previously visited noncore noise. Never overwrite a border already labeled by another component.
7. Continue scanning and publish all labels/core diagnostics.

All loops/recursion are bounded by explicit data/iteration limits. Fitted arrays and diagnostics are copied into state only after the full procedure succeeds.

## 9. Pseudocode

```text
neighbors <- distances<=eps, including self
core <- neighbor_count>=minimum
labels <- -1; visited <- false
for row in input order:
    if visited: continue
    if noncore: mark visited; continue
    queue <- row
    while queue not exhausted:
        if first visit to a core: enqueue not-yet-queued neighbors
        if label is -1: attach current component
    advance component ID
```

## 10. Dry Run

For X=[0,0.1,5,5.1,10], eps=0.2 and min_samples=2, the first four rows each have two self-inclusive neighbors and are core. Rows [0,0.1] form component 0, [5,5.1] form component 1, and 10 has only itself and remains noise. Counts are [2,2,2,2,1]; labels are [0,0,1,1,-1]. A separate three-row test checks that an early noncore endpoint later becomes border.

## 11. Time Complexity

Computing all pairwise neighborhoods costs O(n²p). Bounded core expansion scans O(n²) neighbor entries; it does not use a spatial index. Total O(n²p), with no data-independent subquadratic guarantee. Each row is visited at most once, though an already visited border may appear in different bounded component queues.

## 12. Space Complexity

Dense distances/neighborhoods use O(n²), counts/labels/visit flags and a component queue O(n), copied core observations O(np). Pairwise distance computation uses row-sized O(np) temporaries rather than an n*n*p tensor.

## 13. Python Implementation

The from-scratch implementation is [python/solution.py](python/solution.py), with reusable `DBSCAN` and the API described above. [python/example.py](python/example.py) is a fixed executable example. Core logic uses NumPy/local code, never a scikit-learn/SciPy estimator. Shared [support.py](../support.py) supplies strict contracts and stable Euclidean distances. Tests are in [tests/test_python.py](tests/test_python.py). Install [requirements-ml.txt](../../../../requirements-ml.txt) for runtime; use [requirements-ml-test.txt](../../../../requirements-ml-test.txt) for reference tests.

## 14. C++ Implementation

Classical ML has a Python-first policy. Optional C++ is **not implemented** here; there are no dummy C++ source/test files. DSA remains Python/C++ mandatory, with actual C++17/C++20 validation. This status is explicit in the catalog rather than represented by a fake implementation.

## 15. Input and Output Examples

From the repository root with the existing ML environment:

```sh
python machine-learning/unsupervised-learning/clustering/dbscan/python/example.py
```

The independently justified labels are `[0, 0, 1, 1, -1]`. Cluster IDs are conventional, not class meanings; the dry run explains their ordering. Equivalent Python API, from this topic's python directory:

```python
from solution import DBSCAN
model = DBSCAN(**{'eps': 0.2, 'min_samples': 2})
labels = model.fit_predict([[0], [0.1], [5], [5.1], [10]])
```

The JSON CLI accepts exactly X and optional parameters and prints a labels object. Invalid input exits 2 with stderr and no labels JSON. Numeric comparisons use tolerances; exact labels are used only when the example/tie rule fixes them.

## 16. Edge Cases

min_samples=1 makes every row core, possibly singleton clusters. A support greater than n gives all noise and an empty (0,p) components array. Exact duplicates have zero distance and count separately. Inclusive radius boundaries are deterministic in float64. Ambiguous borders attach to the first reached component; core connectivity is the invariant for row-permutation tests, not an unjustified border-label invariance.

Predict/transform before fit, where those methods exist, raises ValueError. Invalid hyperparameters are checked again at fit. Exhausted iterative fitting is not silently returned as converged. Unsupported keywords fail rather than being ignored.

## 17. Advantages

Handles nonconvex core connectivity and explicit noise without choosing K; exposes support and core points for independent inspection.

## 18. Disadvantages and Limitations

A single eps can struggle with varying density. Scale and high-dimensional distance concentration matter. This bounded version has quadratic memory, Euclidean distance only, no sample weights, sparse/precomputed matrices, approximate neighbor index or out-of-sample prediction. Border ambiguity and floating-point radius boundaries remain explicit.

## 19. When to Use It

Use when a fixed radius/support model is meaningful for small numeric data and noise should remain unassigned.

## 20. When Not to Use It

Avoid strongly varying local density, very large/high-dimensional inputs, an online prediction requirement or a setting where eps lacks a meaningful scale.

## 21. Comparison With Related Algorithms

| Method | Scale / noise policy |
| --- | --- |
| DBSCAN | Fixed radius and support; explicit noise |
| HDBSCAN | Density hierarchy and stability-selected groups |
| K-Means | Fixed K, centroid SSE and no noise class |

## 22. Interview Questions

1. Why is self counted in min_samples here?
2. Why can a noncore observation become border but never expand neighbors?
3. Describe an ambiguous border and the deterministic policy.
4. Why is ordinary nearest-centroid prediction a different algorithm?

## 23. Practice Problems

1. Reproduce the five-row counts and labels.
2. Build two core components sharing a noncore border.
3. Compare noise/core sets with sklearn under aligned radius/support rules.

Validation commands, from the root:

```sh
python -m pytest machine-learning/unsupervised-learning/clustering/dbscan -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
```

Oracles use independent formulas, exhaustive tiny cases or separately fitted references. Different valid labelings/trees/eigenvector signs are compared through the appropriate invariants. Marker groups overlap and are not additive. Seeds, data sizes and tolerances are fixed; no network dataset download or hidden library fit is used.

## 24. References

[scikit-learn DBSCAN guide](https://scikit-learn.org/1.8/modules/clustering.html#dbscan); [Ester et al., original DBSCAN paper](https://cdn.aaai.org/KDD/1996/KDD96-037.pdf).

References identify the mathematical method. The exact implemented subset, numeric domain, tie policy and unsupported features are stated here; external libraries can use different valid initialization, ordering, stopping or metric conventions.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE) · [Contribution guidance](../../../../CONTRIBUTING.md). Current Phase 16 review approval is pending.
