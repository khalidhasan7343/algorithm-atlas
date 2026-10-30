# Agglomerative Hierarchical Clustering

## 1. Algorithm Name

Agglomerative Hierarchical Clustering

## 2. Overview

Start from singleton groups and merge the least-dissimilar pair until one full hierarchy remains. The supported Euclidean linkages are single, complete, average and Ward. A requested K-group partition is captured along the way without truncating the stored full hierarchy.

## 3. Problem Statement

All fitting inputs are dense finite real numeric X=(n_samples,n_features);
1D X, booleans, strings, complex numbers, missing/infinite values and implicit
reshaping are rejected. Numeric features have magnitude <=10^12. Standard limits
are n<=512,p<=32; hierarchical and spectral/density methods state tighter limits
below. Prediction, when defined, requires the fitted feature count and at most
4096 rows; empty query matrices are supported. No supervised target y is consumed.
Caller inputs and global NumPy RNG state are unchanged. Failed fits do not replace
an earlier complete fitted state. See the exact task-specific API below.

AgglomerativeClustering(n_clusters=2, linkage="ward") provides fit and fit_predict. Training limits n<=128,p<=32; K is a native integer 1..n, and linkage is single/complete/average/ward. Outputs labels_, children_ (n-1,2), distances_, counts_ and n_leaves_. It is transductive: no invented predict/transform API for new rows.

## 4. Why Do We Need This Algorithm?

A single K partition hides how groups relate across scales. A merge hierarchy exposes nested similarity structure, and different linkage rules make different geometric assumptions explicit.

## 5. Real-World Applications

Small numeric profiles, object measurements or scientific descriptor tables can be explored as a nested merge hierarchy. A chosen cut is a descriptive partition, not a proof of natural categories. Distance scaling and linkage selection must reflect the application; this implementation supplies no missing-data or categorical-distance interpretation.

## 6. Core Intuition

Each active group has an ID. Evaluate every pair using the selected linkage, choose the smallest distance with deterministic ID ties, and replace the pair by their union. Store each merge before continuing.

Single linkage is the minimum cross-group distance; complete is the maximum; average is the mean of all cross distances. Ward minimizes the added within-group squared error DeltaSSE=nA*nB/(nA+nB)*||meanA-meanB||², and stores height sqrt(2*DeltaSSE), matching SciPy’s Euclidean Ward distance convention.

## 7. Prerequisites

Pairwise Euclidean distances, set partitions, linkage definitions and centroid SSE. Read [ML development](../../../../docs/ml-development.md), [current scope](../../../../docs/clustering-scope.md) and [numerical contracts](../../../../docs/clustering-conventions.md).

## 8. Step-by-Step Working Process

1. Validate X, linkage and requested K; compute stable Euclidean distances.
2. Initialize one active group per observation with its row ID and mean.
3. Enumerate every active pair and calculate its linkage. Ward compares square-root SSE increase directly, avoiding premature tiny squared-unit underflow.
4. Choose the lexicographically smallest (height,left_ID,right_ID) among minima.
5. Merge membership lists and allocate the next hierarchy ID n+merge_index; record child IDs, height and leaf count.
6. Capture the active partition when exactly K groups remain, but continue until the full n-1 merges are recorded.
7. Label groups by their smallest original row index; publish the full hierarchy and cut.

All loops/recursion are bounded by explicit data/iteration limits. Fitted arrays and diagnostics are copied into state only after the full procedure succeeds.

## 9. Pseudocode

```text
groups <- singleton row groups
while more than one group:
    pair <- minimum (linkage_height, left_id, right_id)
    joined <- union(pair)
    record children, height and count
    replace pair with joined
    if number of groups == K: save partition
return saved partition and full hierarchy
```

## 10. Dry Run

For X=[0,2,10,12] and Ward linkage, merge 0 with 2 at height 2, and 10 with 12 at height 2. The two resulting means are 1 and 11, both with size two; the final height is sqrt(2*2*2/4)*10=sqrt(200). The K=2 cut labels are [0,0,1,1]. Equal first merge heights are resolved by row-derived IDs.

## 11. Time Complexity

Let n<=128, p<=32. Pairwise distances cost O(n²p). The direct active-pair scans and cross-group linkage evaluation give a conservative O(n³p) full-hierarchy bound; this intentionally avoids production priority-queue/nearest-neighbor-chain optimizations. Returning a cut still computes all merges.

## 12. Space Complexity

Distance matrix O(n²), groups O(n) membership entries at a time, means O(np), and hierarchy O(n). Cross-group distance slices add O(n²) temporary storage. There is no recursive tree growth.

## 13. Python Implementation

The from-scratch implementation is [python/solution.py](python/solution.py), with reusable `AgglomerativeClustering` and the API described above. [python/example.py](python/example.py) is a fixed executable example. Core logic uses NumPy/local code, never a scikit-learn/SciPy estimator. Shared [support.py](../support.py) supplies strict contracts and stable Euclidean distances. Tests are in [tests/test_python.py](tests/test_python.py). Install [requirements-ml.txt](../../../../requirements-ml.txt) for runtime; use [requirements-ml-test.txt](../../../../requirements-ml-test.txt) for reference tests.

## 14. C++ Implementation

Classical ML has a Python-first policy. Optional C++ is **not implemented** here; there are no dummy C++ source/test files. DSA remains Python/C++ mandatory, with actual C++17/C++20 validation. This status is explicit in the catalog rather than represented by a fake implementation.

## 15. Input and Output Examples

From the repository root with the existing ML environment:

```sh
python machine-learning/unsupervised-learning/clustering/agglomerative-hierarchical-clustering/python/example.py
```

The independently justified labels are `[0, 0, 1, 1]`. Cluster IDs are conventional, not class meanings; the dry run explains their ordering. Equivalent Python API, from this topic's python directory:

```python
from solution import AgglomerativeClustering
model = AgglomerativeClustering(**{'n_clusters': 2, 'linkage': 'ward'})
labels = model.fit_predict([[0], [2], [10], [12]])
```

The JSON CLI accepts exactly X and optional parameters and prints a labels object. Invalid input exits 2 with stderr and no labels JSON. Numeric comparisons use tolerances; exact labels are used only when the example/tie rule fixes them.

## 16. Edge Cases

One observation with K=1 has empty (0,2) children and label zero. Duplicate observations merge at zero distance. Equal linkage distances can produce different valid merge orders/counts in reference libraries; compare heights/cophenetic structure or use tie-free data when asserting exact internals. K=n returns singleton labels while still storing the full hierarchy.

Predict/transform before fit, where those methods exist, raises ValueError. Invalid hyperparameters are checked again at fit. Exhausted iterative fitting is not silently returned as converged. Unsupported keywords fail rather than being ignored.

## 17. Advantages

Exposes all merge scales, deterministic ties and inspectable counts. Multiple linkage definitions share one clear hierarchy construction.

## 18. Disadvantages and Limitations

Dense pairwise storage and naive merging are intentionally expensive. The cut is transductive and greedy. Single linkage can chain through bridges, complete linkage favors compact diameters, average uses all cross pairs and Ward favors SSE-compact groups. Row-order ties can alter equally valid hierarchy details. No precomputed/custom metric, connectivity constraints, dendrogram plotting or automatic cut selection.

## 19. When to Use It

Use for small data where a nested group description and explicit linkage interpretation are useful.

## 20. When Not to Use It

Avoid large data, a required online/out-of-sample classifier, non-Euclidean Ward use or applications with unresolved feature-scale assumptions.

## 21. Comparison With Related Algorithms

| Linkage / method | Merge preference |
| --- | --- |
| Single | Closest connected pair; susceptible to chains |
| Complete | Small maximum cross-distance |
| Average | Small mean cross-distance |
| Ward | Small SSE increase |
| DIANA | Top-down division instead of bottom-up merging |

## 22. Interview Questions

1. Derive Ward’s SSE-increase identity.
2. Why are its stored heights square roots rather than raw SSE?
3. How can ties change merge counts without invalidating single-linkage heights?
4. Why does this model omit new-row prediction?

## 23. Practice Problems

1. Calculate the complete four-row Ward hierarchy.
2. Build a three-duplicate hierarchy and check every count.
3. Compare all supported linkage heights with SciPy on data without tied merge distances.

Validation commands, from the root:

```sh
python -m pytest machine-learning/unsupervised-learning/clustering/agglomerative-hierarchical-clustering -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
```

Oracles use independent formulas, exhaustive tiny cases or separately fitted references. Different valid labelings/trees/eigenvector signs are compared through the appropriate invariants. Marker groups overlap and are not additive. Seeds, data sizes and tolerances are fixed; no network dataset download or hidden library fit is used.

## 24. References

[SciPy linkage definitions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html); [scikit-learn hierarchical clustering](https://scikit-learn.org/1.8/modules/clustering.html#hierarchical-clustering).

References identify the mathematical method. The exact implemented subset, numeric domain, tie policy and unsupported features are stated here; external libraries can use different valid initialization, ordering, stopping or metric conventions.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE) · [Contribution guidance](../../../../CONTRIBUTING.md). Current Phase 16 review approval is pending.
