# HDBSCAN — condensed density hierarchy and EOM

## 1. Algorithm Name

HDBSCAN — condensed density hierarchy and EOM

## 2. Overview

Construct a density-adjusted single-linkage hierarchy, condense groups smaller than a minimum size, then select a nonoverlapping set of stable clusters using excess-of-mass (EOM). This implementation includes the actual mutual-reachability/MST/condensation/selection pipeline, not a fixed-radius DBSCAN substitute.

## 3. Problem Statement

All fitting inputs are dense finite real numeric X=(n_samples,n_features);
1D X, booleans, strings, complex numbers, missing/infinite values and implicit
reshaping are rejected. Numeric features have magnitude <=10^12. Standard limits
are n<=512,p<=32; hierarchical and spectral/density methods state tighter limits
below. Prediction, when defined, requires the fitted feature count and at most
4096 rows; empty query matrices are supported. No supervised target y is consumed.
Caller inputs and global NumPy RNG state are unchanged. Failed fits do not replace
an earlier complete fitted state. See the exact task-specific API below.

HDBSCAN(min_cluster_size=5,min_samples=None) provides fit and fit_predict. Fitting needs 2..256 rows and 1..32 columns; min_cluster_size is a native integer 2..n and min_samples is 1..n, defaulting to min_cluster_size. It includes the observation itself, matching sklearn’s convention. Euclidean metric, alpha=1, EOM and root exclusion are fixed. Outputs labels_, probabilities_ membership strengths, core distances, mutual reachability, MST, linkage/condensed trees, cluster births/exits/stabilities and selected cluster IDs. No out-of-sample prediction is claimed.

## 4. Why Do We Need This Algorithm?

A single density radius can miss groups with different density scales. A hierarchy followed by persistence selection asks which groups survive over substantial density intervals, while small transient branches become noise.

## 5. Real-World Applications

Small numeric descriptor or spatial-coordinate datasets can illustrate varying-density groups, border strength and points rejected as noise. The condensed tree makes persistence decisions inspectable. Scale assumptions and the minimum-size/support choices still require validation; membership strengths are not calibrated class probabilities or a universal anomaly score.

## 6. Core Intuition

Increase density by decreasing distance. Sparse points have larger core distances, so mutual reachability delays joining them to dense groups. An MST preserves single-linkage connectivity at every threshold. Condensation follows sufficiently large branches and records when points fall out; EOM compares a parent’s persistence mass with the best disjoint choices below it.

Core(i) is the self-inclusive min_samples-th ordered distance. MutualReach(i,j)=max(core(i),core(j),||xi-xj||). Condensed density is lambda=distance_scale_/merge_distance, a positive global rescaling of ordinary 1/d. Stability(C)=sum_{i born in C}(lambda_exit(i)-lambda_birth(C)). Uniform rescaling multiplies all finite physical-density stabilities equally, preserving EOM choices; membership uses exit/max-exit ratios. The root is ineligible. Infinite zero-distance persistence is explicit, and equal infinite endpoints have zero duration.

## 7. Prerequisites

Density connectivity, MST/single linkage, rooted trees, extended-real intervals and dynamic programming on disjoint descendants. Read [ML development](../../../../docs/ml-development.md), [current scope](../../../../docs/clustering-scope.md) and [numerical contracts](../../../../docs/clustering-conventions.md).

## 8. Step-by-Step Working Process

1. Validate finite data, minimum size and self-inclusive support; compute stable Euclidean distances and core distances.
2. Form the complete mutual-reachability matrix at alpha=1.
3. Build an exact dense Prim MST with deterministic row/parent ties. Existing integer-weight DSA Prim has a different numeric contract, so this local float machinery does not replace it.
4. Sort MST edges and union components into a complete binary single-linkage hierarchy.
5. Traverse downward. Two sufficiently large children create new cluster identities; one large child retains its parent identity while small branches lose points; two small children end the current cluster.
6. Store every departure density and condensed edge. Use global distance scaling to protect tiny uniform feature scales; reject unresolved finite relative densities above 10^300.
7. Compute stability from point lifetimes. Bottom-up EOM chooses an eligible parent if its mass is at least the best descendant sum; otherwise choose descendants. Equal infinite scores favor the eligible parent.
8. Label selected birth memberships in smallest-row order; unselected points remain -1. Normalize each selected point’s departure by its selected-cluster maximum departure for membership strength.

All loops/recursion are bounded by explicit data/iteration limits. Fitted arrays and diagnostics are copied into state only after the full procedure succeeds.

## 9. Pseudocode

```text
D <- Euclidean distances
core <- self-inclusive support neighbor distance
M[i,j] <- max(D[i,j],core[i],core[j])
MST <- exact dense minimum spanning tree of M
hierarchy <- sorted-edge union tree
condense(node, cluster):
    two large children -> end parent, create/recurse child clusters
    one large child -> lose small-branch points; continue same identity
    no large children -> lose all remaining points
stability <- sum point departure-minus-birth intervals
EOM <- best parent OR disjoint descendants, excluding root
labels <- selected memberships, remaining noise; strength <- relative departure
```

## 10. Dry Run

For X=[0,0.1,0.2,5,5.1,5.2,12], min_cluster_size=3 and self-inclusive min_samples=2, core distances are [0.1,0.1,0.1,0.1,0.1,0.1,6.8]. The isolated last point leaves before two size-three groups separate at distance 4.8. With distance_scale_=12, their birth density is 12/4.8=2.5 and each ends near 12/0.1=120, giving stability 3*(120-2.5)=352.5. EOM selects both groups; labels [0,0,0,1,1,1,-1] and strengths [1,1,1,1,1,1,0] are verified.

## 11. Time Complexity

For n<=256,p<=32, distance construction is O(n²p), dense MST O(n²), edge sorting O(n log n), and the explicit retained membership/exit traversal at most O(n²). EOM is linear in the condensed cluster graph once lifetimes are available. A conservative total is O(n²p+n²); no indexed or approximate-MST acceleration is claimed.

## 12. Space Complexity

Dense distances/reachability use O(n²); retained hierarchy memberships and cluster exit dictionaries can also require O(n²). MST and condensed-edge arrays use O(n), with O(np) copied input temporaries. Binary hierarchy recursion is bounded by n-1<=255, not unbounded. This is an educational dense implementation.

## 13. Python Implementation

The from-scratch implementation is [python/solution.py](python/solution.py), with reusable `HDBSCAN` and the API described above. [python/example.py](python/example.py) is a fixed executable example. Core logic uses NumPy/local code, never a scikit-learn/SciPy estimator. Shared [support.py](../support.py) supplies strict contracts and stable Euclidean distances. Tests are in [tests/test_python.py](tests/test_python.py). Install [requirements-ml.txt](../../../../requirements-ml.txt) for runtime; use [requirements-ml-test.txt](../../../../requirements-ml-test.txt) for reference tests.

## 14. C++ Implementation

Classical ML has a Python-first policy. Optional C++ is **not implemented** here; there are no dummy C++ source/test files. DSA remains Python/C++ mandatory, with actual C++17/C++20 validation. This status is explicit in the catalog rather than represented by a fake implementation.

## 15. Input and Output Examples

From the repository root with the existing ML environment:

```sh
python machine-learning/unsupervised-learning/clustering/hdbscan/python/example.py
```

The independently justified labels are `[0, 0, 0, 1, 1, 1, -1]`. Cluster IDs are conventional, not class meanings; the dry run explains their ordering. Equivalent Python API, from this topic's python directory:

```python
from solution import HDBSCAN
model = HDBSCAN(**{'min_cluster_size': 3, 'min_samples': 2})
labels = model.fit_predict([[0], [0.1], [0.2], [5], [5.1], [5.2], [12]])
```

The JSON CLI accepts exactly X and optional parameters and prints a labels object. Invalid input exits 2 with stderr and no labels JSON. Numeric comparisons use tolerances; exact labels are used only when the example/tie rule fixes them.

## 16. Edge Cases

Exact duplicates can create zero-distance events and infinite lifetime/stability. Equal infinity endpoints contribute zero duration; finite birth to infinite exit contributes infinite stability. Strength is one for infinite departure in an infinite-maximum selected group, zero for finite departure there. The root is always excluded, so one undivided constant group can yield all noise. Small relative scales beyond the representable density bound raise ValueError rather than silently becoming duplicate events. Public condensed lambdas/stabilities are normalized units, unlike raw 1/d library diagnostics.

Predict/transform before fit, where those methods exist, raises ValueError. Invalid hyperparameters are checked again at fit. Exhausted iterative fitting is not silently returned as converged. Unsupported keywords fail rather than being ignored.

## 17. Advantages

Exposes all essential density-hierarchy stages, meaningful noise and persistence evidence, exact MST rather than epsilon scanning, and independently checkable selection.

## 18. Disadvantages and Limitations

Euclidean dense alpha=1/EOM/root-excluded subset only; no arbitrary metrics, precomputed distances, leaf/epsilon selection, allow_single_cluster, approximate prediction, GLOSH outlier scoring or production indexing. Infinite/tied events have the documented deterministic policy and need not reproduce every library internal ordering. Parameters and density scaling still matter; no globally correct semantic clustering is promised.

## 19. When to Use It

Use for small data where density persistence, varying density and explicit noise are important to inspect.

## 20. When Not to Use It

Avoid production-scale data, an online predictor requirement, arbitrary distance metrics or interpretations of membership strength as supervised class probability.

## 21. Comparison With Related Algorithms

| Method | Extraction mechanism |
| --- | --- |
| DBSCAN | One fixed radius and self-inclusive support |
| HDBSCAN here | Mutual-reachability hierarchy, condensation and EOM |
| Single linkage alone | Distance connectivity without density adjustment/condensation |

## 22. Interview Questions

1. Derive mutual reachability and explain core-distance inflation.
2. Why does an MST preserve all single-linkage threshold components?
3. Compute the two 352.5 stabilities in the example.
4. Why must root exclusion and duplicate infinity handling be explicit?

## 23. Practice Problems

1. Reconstruct every finite condensed stability from edge mass and birth density.
2. Enumerate all disjoint cluster selections on a tiny condensed tree and check EOM’s maximum score.
3. Compare sklearn labels and strengths with the same self-inclusive support, root exclusion and exact dense settings.

Validation commands, from the root:

```sh
python -m pytest machine-learning/unsupervised-learning/clustering/hdbscan -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
```

Oracles use independent formulas, exhaustive tiny cases or separately fitted references. Different valid labelings/trees/eigenvector signs are compared through the appropriate invariants. Marker groups overlap and are not additive. Seeds, data sizes and tolerances are fixed; no network dataset download or hidden library fit is used.

## 24. References

[Developer algorithm explanation and stability formula](https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html); [sklearn 1.8 HDBSCAN API and self-neighbor convention](https://scikit-learn.org/1.8/modules/generated/sklearn.cluster.HDBSCAN.html).

References identify the mathematical method. The exact implemented subset, numeric domain, tie policy and unsupported features are stated here; external libraries can use different valid initialization, ordering, stopping or metric conventions.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE) · [Contribution guidance](../../../../CONTRIBUTING.md). Current Phase 16 review approval is pending.
