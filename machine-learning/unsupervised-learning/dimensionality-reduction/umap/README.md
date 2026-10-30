# Uniform Manifold Approximation and Projection (exact educational UMAP)

## 1. Algorithm Name

Uniform Manifold Approximation and Projection (exact educational UMAP)

## 2. Overview

Construct a locally scaled fuzzy nearest-neighbor graph and embed it with explicit attractive and repulsive cross-entropy gradients.

## 3. Problem Statement

For 3<=n<=128 numeric rows and 2<=k<n, compute a symmetric fuzzy graph and one d-dimensional embedding,1<=d<=3; there is no out-of-sample transform.

## 4. Why Do We Need This Algorithm?

A single global radius can miss neighborhoods with differing sampling density. Local connectivity and adaptive bandwidths let each observation contribute a graded neighborhood.

## 5. Real-World Applications

Small manifold-neighborhood visualization experiments and fuzzy graph inspection, with no claim of production UMAP throughput or identical coordinates.

## 6. Core Intuition

Give nearby points strong fuzzy edges, combine both directions by probabilistic union, then attract important edges while repelling pairs absent from the graph.

Exact Euclidean kNN excludes self, breaks equal-distance ties by row index, and uses rho_i=first positive neighbor distance (or0). Solve sum_j exp(-max(0,dij-rho_i)/sigma_i)=log2(k) on selected neighbors, with an explicit floor when ties make that target unattainable. Directed wij are zero off kNN; Gij=wij+wji-wij*wji. Output qij=1/(1+a*(||yi-yj||²+epsilon)), fixed b=1, epsilon1e-6. Minimize sum_(i<j)[G log(G/q)+(1-G)log((1-G)/(1-q))], with endpoint0log0=0. Pair gradient for yi is2*(G-q)/(r²+epsilon)*(yi-yj); the opposite sign updates yj.

## 7. Prerequisites

Vectors, inner products, matrix multiplication, derivatives where optimization is used, and floating-point tolerances. Read the [B5 contracts](../../../../docs/dimensionality-reduction-conventions.md) and linked comparisons below.

## 8. Step-by-Step Working Process

Center/uniformly scale X, build all distances and stable exact kNN, determine rho and adaptive sigma, expose saturated_rows_ for floor-limited targets, then fuzzy-union directed edges. Initialize a seeded Gaussian embedding, and optimize the complete smoothed pair objective by bounded full-gradient Armijo descent. Both attraction and repulsion are included; no PCA/t-SNE substitute or generic graph layout. Disconnected graphs remain supported because full pair repulsion and random initialization do not need a connected spectral basis.

## 9. Pseudocode

```text
exact Euclidean kNN excluding self
for each row: rho=first positive distance; calibrate sigma or mark floor saturation
directed membership=exp(-max(0,d-rho)/sigma) on kNN
G=directed+directed.T-directed*directed.T
seed random Y; compute smoothed rational q
minimize full Bernoulli graph divergence by bounded gradient/backtracking
return graph, Y, calibration/optimization diagnostics
```

## 10. Dry Run

X=(0,1,3,7), k=2. Neighbor IDs are (1,2),(0,2),(1,0),(2,1), rho=(1,1,2,4) in original distance units; the implementation stores uniformly normalized distance units. log2(2)=1 is approached at the sigma floor: each nearest edge has membership1 and further edges underflow to0. Fuzzy union gives the path0–1–2–3. The seeded 30-step example embeds this exact graph and records actual status/coordinates in evidence.

## 11. Time Complexity

Exact graph construction O(n²*p+n² log n), local searches O(100*n*k); optimization O(T*B*n²*d), T<=5000 and B<=60. Defaults k5,T300,a1,learning_rate1. No approximate-neighbor or negative-sampling acceleration.

## 12. Space Complexity

O(n²+n*k+n*d) graph/distance/embedding state plus O(n*p) input; full pair matrices deliberately bound this educational implementation to small n.

## 13. Python Implementation

[UMAP source](python/solution.py) implements the stated mechanism using NumPy primitives and shared bounded contracts; no reference estimator is imported. [Executable example](python/example.py); [tests](tests/test_python.py). Fit copies caller data and installs state only after successful validation/computation. Queries validate fitted feature dimensions.

Validation hand-checks the k2 path graph and fuzzy-union formula, compares exact kNN with sklearn and local scales with independent SciPy brentq roots, and central-differences the full smoothed objective. Duplicate/saturated/disconnected graphs, deterministic embeddings and budget status are covered.

## 14. C++ Implementation

C++ is optional for this authorized Python/NumPy scope and is absent; no placeholder source or test is provided. DSA still requires actual Python/C++17/C++20 checks.

## 15. Input and Output Examples

From repository root, with requirements-ml-test.txt installed:

```sh
python machine-learning/unsupervised-learning/dimensionality-reduction/umap/python/example.py
```

The example uses the dry-run input and prints a JSON embedding. The solution also accepts a JSON object with X, optional parameters and y for supervised LDA on stdin. Actual example/CLI outputs are retained in the Phase 17 evidence. Numeric coordinates are sign/rotation dependent where explained; objectives and subspaces are the comparison contract.

## 16. Edge Cases

Duplicate ties can force directed mass above log2(k); saturated_rows_ records this instead of inventing a solved sigma. Sigma floor=1e-12*max(mean selected distance,1e-12) in normalized units. Disconnected and fully duplicate inputs are accepted. Epsilon avoids infinite repulsion at coincident embedded points; derivatives match this explicitly smoothed objective.

Reject nonfinite/nonreal arrays, invalid dimensions and unsupported resource limits before fitting. Invalid refits preserve previous fitted arrays. Random methods use a local generator and never modify global RNG state.

## 17. Advantages

Inspectable local graph, verified fuzzy-union algebra, exact deterministic gradients, and transparent density/tie diagnostics.

## 18. Disadvantages and Limitations

Fixed Euclidean metric, local_connectivity1, exact search and full pair cross-entropy. Uses b=1 and user a>0 rather than fitting reference min_dist/spread curves; epsilon slightly changes the ideal singular output objective. No approximate NN, negative sampling, transform, spectral initialization or reference-coordinate guarantee. Full cross-entropy differs from the effective objective of production sampled updates.

## 19. When to Use It

Use to learn essential UMAP graph construction and attraction/repulsion mechanics on a bounded dataset.

## 20. When Not to Use It

Use production software for large datasets, sparse/arbitrary metrics or a validated out-of-sample transform; do not infer global cluster distances from the plot.

## 21. Comparison With Related Algorithms

UMAP fuzzifies a sparse local graph, while t-SNE builds entropy-calibrated joint probabilities and minimizes KL. Both are nonlinear/nonconvex and transductive here. PCA provides a reusable linear transform and a rank-k squared-error guarantee.

## 22. Interview Questions

Why fuzzy union? Either direction can establish a strong undirected edge. Why is sigma calibration sometimes saturated? Tied rho-or-closer neighbors already exceed target mass. Why no raw-coordinate reference assertion? Initialization, objective sampling and rigid motions change coordinates without defining graph correctness.

## 23. Practice Problems

Verify all six off-diagonal path entries for the dry run. Derive the smoothed pair gradient. Construct two groups of three duplicate rows with k2 and check their graph components remain disconnected.

## 24. References

[McInnes, Healy and Melville, UMAP paper](https://arxiv.org/abs/1802.03426); [UMAP authors: how it works](https://umap-learn.readthedocs.io/en/latest/how_umap_works.html); [official graph implementation](https://github.com/lmcinnes/umap/blob/master/umap/umap_.py).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). This lesson is part of Phase 17 B5; owner review is pending.
