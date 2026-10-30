# Spectral Clustering — normalized graph embedding

## 1. Algorithm Name

Spectral Clustering — normalized graph embedding

## 2. Overview

Build a nonnegative affinity graph, solve its normalized-affinity eigenproblem, normalize embedding rows and cluster them with the canonical K-Means solver. This is the Ng-Jordan-Weiss style row-normalized relaxation, with explicit graph/numerical diagnostics and transductive labels.

## 3. Problem Statement

All fitting inputs are dense finite real numeric X=(n_samples,n_features);
1D X, booleans, strings, complex numbers, missing/infinite values and implicit
reshaping are rejected. Numeric features have magnitude <=10^12. Standard limits
are n<=512,p<=32; hierarchical and spectral/density methods state tighter limits
below. Prediction, when defined, requires the fitted feature count and at most
4096 rows; empty query matrices are supported. No supervised target y is consumed.
Caller inputs and global NumPy RNG state are unchanged. Failed fits do not replace
an earlier complete fitted state. See the exact task-specific API below.

SpectralClustering(n_clusters=8,affinity="rbf",gamma=1,n_init=10,random_state=0) provides fit and fit_predict. K is a native integer 1..min(n,64), gamma finite real (0,10^12], n_init 1..16, seed 0..2^32-1. RBF feature input has n<=256,p<=32. Precomputed input is an affinity matrix (n,n), 2<=n<=256, rather than a p<=32 feature table; it needs finite nonnegative entries<=10^12, exact zero diagonal and symmetry within 10^-12 absolute/relative tolerance. Symmetric averaging within that tolerance is explicit. No out-of-sample transform/predict is claimed.

## 4. Why Do We Need This Algorithm?

Some groups are not well represented by spherical Euclidean centroid partitions in the original coordinates. A similarity graph can encode local relationships; its relaxed partition coordinates may make those groups easier to separate.

## 5. Real-World Applications

Small graph/community or engineered-similarity studies can compare partitions in affinity space and inspect normalized cut. RBF affinity is only meaningful at an appropriate numeric feature scale. This dense implementation is not a graph neural network, arbitrary-dimensionality-reduction API or production large-graph partitioner.

## 6. Core Intuition

Normalize graph edge mass by vertex degrees, then take the eigenvectors with largest normalized-affinity eigenvalues. Row normalization emphasizes graph membership direction rather than coordinate magnitude. K-Means finds a bounded local partition in this embedding, while final label IDs are ordered by smallest observation index.

For symmetric W>=0 with zero diagonal, d=W*1 and A=D^(-1/2)*W*D^(-1/2). Largest eigenvectors of A correspond to smallest eigenvectors of L_sym=I-A. Let U contain the first K eigenvectors; set Y_i=U_i/||U_i|| and cluster rows Y. The reported normalized cut is sum_C cut(C,not C)/volume(C). This is a relaxation plus nonconvex rounding, not a guarantee of the globally minimum discrete cut.

## 7. Prerequisites

Weighted graph degrees, normalized Laplacians, symmetric eigendecomposition, eigenspace nonuniqueness and K-Means. Read [ML development](../../../../docs/ml-development.md), [current scope](../../../../docs/clustering-scope.md) and [numerical contracts](../../../../docs/clustering-conventions.md).

## 8. Step-by-Step Working Process

1. Validate feature or precomputed-affinity input and all parameters.
2. For RBF, set W_ij=exp(-gamma*||xi-xj||²) for i!=j, with zero diagonal. For precomputed input validate and explicitly average accepted symmetry roundoff.
3. Reject isolated vertices. Compute positive-edge connected components; require K at least their count to avoid an unresolved partial disconnected embedding.
4. Form A by sequential row/column square-root degree division, avoiding an overflowing outer-product denominator at tiny affinity scales.
5. Solve the dense symmetric eigenproblem and retain the largest K eigenvalues/vectors. Reject a numerically zero row norm.
6. Normalize embedding rows and fit canonical bounded K-Means with the configured seed/starts.
7. Relabel groups by their smallest original row index; compute normalized cut and store affinity, degree, eigen/embedding and K-Means diagnostics.

All loops/recursion are bounded by explicit data/iteration limits. Fitted arrays and diagnostics are copied into state only after the full procedure succeeds.

## 9. Pseudocode

```text
W <- RBF feature affinity or validated precomputed matrix
require positive degrees and components<=K
A <- W / sqrt(degree rows) / sqrt(degree columns)
U <- top K orthonormal eigenvectors of A
Y <- row-normalized U; reject zero rows
partition <- canonical K-Means(Y)
labels <- same groups, ordered by minimum input index
return transductive labels and graph/eigen/cut diagnostics
```

## 10. Dry Run

The example affinity is two disconnected three-vertex unit-weight cliques, with zero diagonal and no edges between groups. Every degree is two. The two leading eigenvalues are one, and their projector has within-clique entries 1/3 and cross-clique entries zero, irrespective of eigenvector signs or rotations. Row normalization and K=2 recover labels [0,0,0,1,1,1]. The normalized cut is zero. Tests verify eigen residuals, orthogonality, that projector and the independent cut formula.

## 11. Time Complexity

For n<=256,p<=32 and K<=64, RBF construction costs O(n²p), graph traversal O(n²), and full dense eigendecomposition O(n³). Canonical K-Means adds O(R*I*n*K²) in its K-dimensional embedding, with its explicit start/iteration bounds. No sparse eigensolver or large-graph acceleration is claimed.

## 12. Space Complexity

Affinity/normalized matrices and the full eigenbasis use O(n²), embedding O(nK), degrees/graph labels O(n), and the canonical K-Means temporary fit workspace follows its n-by-K-dimensional bound. This is intentionally a dense small-graph model.

## 13. Python Implementation

The from-scratch implementation is [python/solution.py](python/solution.py), with reusable `SpectralClustering` and the API described above. [python/example.py](python/example.py) is a fixed executable example. Core logic uses NumPy/local code, never a scikit-learn/SciPy estimator. Shared [support.py](../support.py) supplies strict contracts and stable Euclidean distances. Tests are in [tests/test_python.py](tests/test_python.py). Install [requirements-ml.txt](../../../../requirements-ml.txt) for runtime; use [requirements-ml-test.txt](../../../../requirements-ml-test.txt) for reference tests. The embedded partition is delegated only to the existing from-scratch [canonical K-Means](../k-means/README.md), not an external estimator.

## 14. C++ Implementation

Classical ML has a Python-first policy. Optional C++ is **not implemented** here; there are no dummy C++ source/test files. DSA remains Python/C++ mandatory, with actual C++17/C++20 validation. This status is explicit in the catalog rather than represented by a fake implementation.

## 15. Input and Output Examples

From the repository root with the existing ML environment:

```sh
python machine-learning/unsupervised-learning/clustering/spectral-clustering/python/example.py
```

The independently justified labels are `[0, 0, 0, 1, 1, 1]`. Cluster IDs are conventional, not class meanings; the dry run explains their ordering. Equivalent Python API, from this topic's python directory:

```python
from solution import SpectralClustering
model = SpectralClustering(**{'n_clusters': 2, 'affinity': 'precomputed', 'random_state': 0})
labels = model.fit_predict([[0, 1, 1, 0, 0, 0], [1, 0, 1, 0, 0, 0], [1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1], [0, 0, 0, 1, 0, 1], [0, 0, 0, 1, 1, 0]])
```

The JSON CLI accepts exactly X and optional parameters and prints a labels object. Invalid input exits 2 with stderr and no labels JSON. Numeric comparisons use tolerances; exact labels are used only when the example/tie rule fixes them.

## 16. Edge Cases

Disconnected components are supported when K covers all of them; too few requested groups fails rather than returning an arbitrary partial component embedding. Isolated vertices fail. Extreme RBF distances can underflow all incident similarities to zero and trigger that error. Uniform tiny positive scaling of a precomputed graph leaves normalized affinity invariant. Repeated eigenvalues/sign changes permit many equivalent bases; compare projectors/partitions, not exact vectors.

Predict/transform before fit, where those methods exist, raises ValueError. Invalid hyperparameters are checked again at fit. Exhausted iterative fitting is not silently returned as converged. Unsupported keywords fail rather than being ignored.

## 17. Advantages

Separates affinity design, graph normalization, embedding and partition rounding with inspectable matrices. Reuses the canonical K-Means implementation and handles allowed disconnected graphs explicitly.

## 18. Disadvantages and Limitations

Only dense RBF/precomputed symmetric nonnegative affinity. No nearest-neighbor graph builder, Nyström extension, sparse solver, alternative discretization, online prediction or arbitrary affinity callback. The Ng-Jordan-Weiss row-normalized convention can differ from another library’s degree-scaled rounding. Eigengap/roundoff and local K-Means choices can affect ambiguous solutions; global cut optimality is not claimed.

## 19. When to Use It

Use when a small meaningful similarity graph represents group structure better than raw centroid distance.

## 20. When Not to Use It

Avoid isolated/invalid affinities, large graphs, unavailable meaningful similarity scales, a need for inductive new-row projection or an assumption that eigenvector coordinates are uniquely oriented.

## 21. Comparison With Related Algorithms

| Method | Representation / output |
| --- | --- |
| Spectral here | Normalized graph eigenvectors, row normalization, transductive cut |
| K-Means | Original Euclidean coordinates and centroid predictions |
| Agglomerative | Linkage hierarchy from pairwise Euclidean distances |

## 22. Interview Questions

1. Derive the relationship between A and the normalized Laplacian.
2. Why are eigenvector signs and repeated-eigenspace bases nonunique?
3. Why reject isolated vertices and too-small K for disconnected graphs?
4. Why does the relaxation not prove a global discrete cut optimum?

## 23. Practice Problems

1. Derive the two-clique projector and zero normalized cut.
2. Verify A*U=U*Lambda and U^T*U=I numerically.
3. Compare compatible graph partitions with sklearn and subspace projectors with SciPy.

Validation commands, from the root:

```sh
python -m pytest machine-learning/unsupervised-learning/clustering/spectral-clustering -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
```

Oracles use independent formulas, exhaustive tiny cases or separately fitted references. Different valid labelings/trees/eigenvector signs are compared through the appropriate invariants. Marker groups overlap and are not additive. Seeds, data sizes and tolerances are fixed; no network dataset download or hidden library fit is used.

## 24. References

[scikit-learn spectral clustering guide](https://scikit-learn.org/1.8/modules/clustering.html#spectral-clustering); [Ng, Jordan and Weiss, On Spectral Clustering](https://papers.nips.cc/paper/2001/hash/801272ee79cfde7fa5960571fee36b9b-Abstract.html).

References identify the mathematical method. The exact implemented subset, numeric domain, tie policy and unsupported features are stated here; external libraries can use different valid initialization, ordering, stopping or metric conventions.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE) · [Contribution guidance](../../../../CONTRIBUTING.md). Current Phase 16 review approval is pending.
