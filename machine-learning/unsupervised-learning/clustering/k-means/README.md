# K-Means — Lloyd fixed-point clustering

## 1. Algorithm Name

K-Means — Lloyd fixed-point clustering

## 2. Overview

Partition Euclidean numeric observations into K nonempty groups by alternating nearest-center assignments and centroid means. Seeded random or D² initialization and explicit center matrices are supported; each accepted run reaches an assignment fixed point.

## 3. Problem Statement

All fitting inputs are dense finite real numeric X=(n_samples,n_features);
1D X, booleans, strings, complex numbers, missing/infinite values and implicit
reshaping are rejected. Numeric features have magnitude <=10^12. Standard limits
are n<=512,p<=32; hierarchical and spectral/density methods state tighter limits
below. Prediction, when defined, requires the fitted feature count and at most
4096 rows; empty query matrices are supported. No supervised target y is consumed.
Caller inputs and global NumPy RNG state are unchanged. Failed fits do not replace
an earlier complete fitted state. See the exact task-specific API below.

KMeans(n_clusters=8, init="k-means++", n_init=10, max_iter=300, random_state=0) provides fit, fit_predict, predict, transform (Euclidean distances to centers) and score (negative squared-distance sum). Counts are native integers: K 1..min(n,64), n_init 1..16, max_iter 1..1000; seed 0..2^32-1. Explicit initial centers have shape (K,p) and require n_init=1. Fitting requires at least K distinct observed rows. No tolerance parameter is accepted: convergence is the strict assignment fixed-point criterion.

## 4. Why Do We Need This Algorithm?

A compact prototype per group gives a simple way to describe approximately spherical clusters. Alternating minimization makes the objective and each update easy to inspect, while exposing sensitivity to scale, initial centers and local minima.

## 5. Real-World Applications

Small numeric segmentation or vector-quantization exercises can summarize observations by representative means. Quantization distortion is measurable as squared Euclidean error, but IDs have no semantic class meaning. Raw categorical labels, non-spherical density clusters and production-scale compression require different representations or methods.

## 6. Core Intuition

Given centers, every row chooses its nearest center. Given a fixed partition, the arithmetic mean minimizes its squared error. Repeat these two updates, using deterministic first-center ties, until reassigning with the updated means gives the same labels.

The objective is J=sum_i ||x_i-mu_label(i)||². Differentiating a nonempty cluster quadratic yields mu_j=mean(x_i in j). Each ordinary assignment/mean step cannot increase J in exact arithmetic. Empty-cluster repairs make progress possible but are explicitly recorded. Finite Lloyd fixed points are local solutions, not guaranteed global minima.

## 7. Prerequisites

Euclidean distance, means, squared-loss minimization and local minima. Read [ML development](../../../../docs/ml-development.md), [current scope](../../../../docs/clustering-scope.md) and [numerical contracts](../../../../docs/clustering-conventions.md).

## 8. Step-by-Step Working Process

1. Validate data, K, initialization, seeds and iteration/resource limits; reject fewer than K distinct rows.
2. Subtract the first row and divide all coordinates by one positive global scale. This preserves Euclidean assignments while preventing tiny squared fitting distances from vanishing.
3. Initialize centers from supplied coordinates, random rows, or sequential D² probabilities using a local RNG.
4. Assign each row to its first nearest center in normalized squared distance.
5. For an empty cluster, move the farthest currently assigned row from a cluster with more than one member; retain deterministic first-row ties.
6. Recompute each nonempty cluster mean, then reassign using those updated means.
7. Accept only when the assignments agree; otherwise continue up to max_iter. Try the bounded configured initializations and keep the best converged normalized objective.
8. If none converges, raise ConvergenceError without replacing a prior fit. Store centers, labels, physical/normalized inertia and repair diagnostics.

All loops/recursion are bounded by explicit data/iteration limits. Fitted arrays and diagnostics are copied into state only after the full procedure succeeds.

## 9. Pseudocode

```text
best <- none
for bounded initialization:
    centers <- seeded/supplied normalized centers
    repeat at most max_iter:
        labels <- nearest center
        repair empty clusters using eligible farthest rows
        means <- cluster means
        if nearest_labels(means) == labels:
            keep candidate if objective is best; stop this run
        centers <- means
if no candidate: fail explicitly
publish best; inference uses stored offset/scaled center representation
```

## 10. Dry Run

For X=[0,2,10,12], K=2 and explicit centers [0,12], the first assignment is [0,0,1,1]. Updated means are [1,11], and reassignment stays unchanged. Each of four rows has squared error one, so J=4. Distances for queries 1 and 11 are [[0,10],[10,0]], and score(X)=-4. The executable labels are [0,0,1,1].

## 11. Time Complexity

Let n be rows, p features, K clusters, R initializations and I iterations. Fit uses O(R*I*n*K*p), plus initialization and O(n*p) means. Querying q rows costs O(q*K*p). Best-case fixed-point runs can stop after one iteration; worst execution is explicitly bounded. No average-case or global-optimality rate is claimed.

## 12. Space Complexity

Normalized data use O(np), centers O(Kp), pairwise fitting differences O(nKp), distances O(nK), labels O(n), and per-run objective history O(I). Only the best accepted run is retained. Transform output needs O(qK); one query uses O(Kp) temporary differences.

## 13. Python Implementation

The from-scratch implementation is [python/solution.py](python/solution.py), with reusable `KMeans` and the API described above. [python/example.py](python/example.py) is a fixed executable example. Core logic uses NumPy/local code, never a scikit-learn/SciPy estimator. Shared [support.py](../support.py) supplies strict contracts and stable Euclidean distances. Tests are in [tests/test_python.py](tests/test_python.py). Install [requirements-ml.txt](../../../../requirements-ml.txt) for runtime; use [requirements-ml-test.txt](../../../../requirements-ml-test.txt) for reference tests.

## 14. C++ Implementation

Classical ML has a Python-first policy. Optional C++ is **not implemented** here; there are no dummy C++ source/test files. DSA remains Python/C++ mandatory, with actual C++17/C++20 validation. This status is explicit in the catalog rather than represented by a fake implementation.

## 15. Input and Output Examples

From the repository root with the existing ML environment:

```sh
python machine-learning/unsupervised-learning/clustering/k-means/python/example.py
```

The independently justified labels are `[0, 0, 1, 1]`. Cluster IDs are conventional, not class meanings; the dry run explains their ordering. Equivalent Python API, from this topic's python directory:

```python
from solution import KMeans
model = KMeans(**{'n_clusters': 2, 'init': [[0], [12]], 'n_init': 1, 'random_state': 0})
labels = model.fit_predict([[0], [2], [10], [12]])
```

The JSON CLI accepts exactly X and optional parameters and prints a labels object. Invalid input exits 2 with stderr and no labels JSON. Numeric comparisons use tolerances; exact labels are used only when the example/tie rule fixes them.

## 16. Edge Cases

K=1 with constant data returns the exact constant. Fewer than K distinct rows is a ValueError rather than silently returning fewer clusters. Repeated initial centers trigger deterministic empty-cluster repair. Tiny true inertia may round to zero in original squared units while normalized_inertia_ remains positive; zero physical inertia is never a convergence shortcut. Query distances keep the offset and scaled center separate to retain small centroid displacements around large offsets.

Predict/transform before fit, where those methods exist, raises ValueError. Invalid hyperparameters are checked again at fit. Exhausted iterative fitting is not silently returned as converged. Unsupported keywords fail rather than being ignored.

## 17. Advantages

Clear objective, interpretable means, reproducible initialization and inspectable repairs/history. Canonical reuse supplies the partition step for later spectral embedding and GMM initialization.

## 18. Disadvantages and Limitations

Only dense finite Euclidean data; clusters are centroid-shaped and sensitive to scaling/outliers. Local minima and initialization dependence remain. Extremely ill-conditioned relative directions can be unresolved in float64. Iteration exhaustion raises rather than returning an unfinished model. No mini-batching, weights, arbitrary metrics or automatic K selection.

## 19. When to Use It

Use for compact approximately spherical numeric groups when prototype means and squared-error distortion are meaningful.

## 20. When Not to Use It

Avoid when nonconvex density structure, unknown noise regions, strong unequal feature units or arbitrary categorical dissimilarities dominate.

## 21. Comparison With Related Algorithms

| Method | Core criterion |
| --- | --- |
| K-Means | Within-cluster squared Euclidean error |
| DBSCAN | Radius-supported connected dense regions and noise |
| GMM | Probabilistic mixture likelihood with soft responsibilities |

## 22. Interview Questions

1. Derive the mean update from the squared-error gradient.
2. Why are cluster IDs not supervised class labels?
3. Why can multiple starts improve but not prove global optimality?
4. Why is a zero underflowed physical objective not proof of exact fit?

## 23. Practice Problems

1. Reproduce the four-row objective and means by hand.
2. Supply repeated initial centers and inspect repaired cluster counts.
3. Compare fixed explicit initial centers with sklearn using label-permutation-invariant checks.

Validation commands, from the root:

```sh
python -m pytest machine-learning/unsupervised-learning/clustering/k-means -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
```

Oracles use independent formulas, exhaustive tiny cases or separately fitted references. Different valid labelings/trees/eigenvector signs are compared through the appropriate invariants. Marker groups overlap and are not additive. Seeds, data sizes and tolerances are fixed; no network dataset download or hidden library fit is used.

## 24. References

[scikit-learn K-Means guide](https://scikit-learn.org/1.8/modules/clustering.html#k-means); [Arthur and Vassilvitskii, k-means++](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf).

References identify the mathematical method. The exact implemented subset, numeric domain, tie policy and unsupported features are stated here; external libraries can use different valid initialization, ordering, stopping or metric conventions.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE) · [Contribution guidance](../../../../CONTRIBUTING.md). Current Phase 16 review approval is pending.
