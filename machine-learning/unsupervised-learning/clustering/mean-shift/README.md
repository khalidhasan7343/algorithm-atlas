# Mean Shift — flat-kernel mode seeking

## 1. Algorithm Name

Mean Shift — flat-kernel mode seeking

## 2. Overview

Starting at every observation, repeatedly move to the mean of observations within a fixed Euclidean bandwidth. Merge nearby supported candidate modes deterministically, then assign observations to their nearest retained mode. This is a bounded flat-neighborhood implementation, not a Gaussian-kernel estimator.

## 3. Problem Statement

All fitting inputs are dense finite real numeric X=(n_samples,n_features);
1D X, booleans, strings, complex numbers, missing/infinite values and implicit
reshaping are rejected. Numeric features have magnitude <=10^12. Standard limits
are n<=512,p<=32; hierarchical and spectral/density methods state tighter limits
below. Prediction, when defined, requires the fitted feature count and at most
4096 rows; empty query matrices are supported. No supervised target y is consumed.
Caller inputs and global NumPy RNG state are unchanged. Failed fits do not replace
an earlier complete fitted state. See the exact task-specific API below.

MeanShift(bandwidth=1,max_iter=300,tol=1e-3,cluster_all=True) provides fit, fit_predict and nearest-mode predict. Bandwidth is finite real (0,10^12], max_iter native integer 1..1000, tol relative to bandwidth in (0,1], and cluster_all a native bool. Data limits n<=512,p<=32. Outputs cluster_centers_, labels_, candidate_centers_/support_, seed_iterations_, n_iter_ and converged_. There is no stochastic seed parameter because all starts and tie rules are deterministic.

## 4. Why Do We Need This Algorithm?

A centroid count K need not be specified when the goal is locating supported modes at a chosen bandwidth. Iterative mean shifts reveal how the local neighborhood changes as a seed moves; merging avoids returning many copies of the same mode.

## 5. Real-World Applications

Small coordinate or descriptor tables can demonstrate density-mode grouping and bandwidth sensitivity. Image-region feature clustering is a conceptual application after valid numeric feature construction; raw-image processing and automatic bandwidth selection are outside this implementation. A nearest-mode prediction is a defined extension, not a claim that new rows refit the density modes.

## 6. Core Intuition

A shift vector points from the current location to the average of nearby rows. For an Epanechnikov density profile, away from radius boundaries its gradient is proportional to the sum of these displacements. Candidate fixed points are neighborhood means; modes closer than the bandwidth are merged by support priority.

For N_h(x)={i:||xi-x||<=h}, update x_next=mean_{i in N_h(x)}xi. Stop when ||x_next-x||<=tol*h. For f(x)=sum_i max(0,1-||xi-x||²/h²), grad f=2/h²*sum_inside(xi-x), so mean_shift=h²*grad f/(2*|N_h|) away from boundary discontinuities. This explains the gradient direction but does not prove universal global-mode convergence.

## 7. Prerequisites

Euclidean balls, arithmetic means, kernel-density intuition and bounded fixed-point iteration. Read [ML development](../../../../docs/ml-development.md), [current scope](../../../../docs/clustering-scope.md) and [numerical contracts](../../../../docs/clustering-conventions.md).

## 8. Step-by-Step Working Process

1. Validate bandwidth, relative tolerance, iteration count, cluster_all and numeric X.
2. Use each input row as a seed; find all rows within the inclusive bandwidth of the current center.
3. Move to the anchor-centered mean of those rows, preserving exactly constant coordinates.
4. Stop that seed after movement<=tol*bandwidth. Any seed exhausting the limit fails the fit rather than being silently omitted.
5. Count support around each final candidate. Sort by descending support, then descending center coordinates, then seed index.
6. Greedily keep a candidate only when farther than one bandwidth from every retained mode.
7. Assign each row to its first nearest retained mode. If cluster_all=False, distances beyond the bandwidth receive -1.
8. Store centers and candidate/convergence diagnostics. Query prediction uses the fitted bandwidth and assignment rule, not additional shifting.

All loops/recursion are bounded by explicit data/iteration limits. Fitted arrays and diagnostics are copied into state only after the full procedure succeeds.

## 9. Pseudocode

```text
for each row seed:
    center <- seed
    repeat at most max_iter:
        neighborhood <- rows within bandwidth
        updated <- neighborhood mean
        if movement<=tol*bandwidth: save candidate/support; stop
        center <- updated
    if unfinished: raise ConvergenceError
sort candidates by support and deterministic coordinate ties
retain candidates farther than bandwidth from previous retained modes
labels <- nearest mode, optionally -1 beyond bandwidth
```

## 10. Dry Run

For X=[0,0.1,5,5.1] with bandwidth 0.3, the first two seeds move to 0.05 and the last two to 5.05. Each candidate has support two. Descending coordinate tie order retains 5.05 first, then 0.05; duplicate candidates merge. Thus retained centers are [5.05,0.05] and training labels [1,1,0,0]. With cluster_all=False, a query at 20 is noise.

## 11. Time Complexity

With n rows, p features and at most I shifts per seed, brute-force neighborhood updates cost O(I*n²*p). Greedy mode suppression adds O(n²p), and assigning q query rows to C retained modes costs O(qCp). There is no spatial index, bin seeding, parallel speedup or automatic bandwidth estimator.

## 12. Space Complexity

Candidate modes use O(np), support/iteration arrays O(n), and retained modes O(Cp). A shift needs O(np) row-difference work. Assignment distances need O(qC), with an explicit distance-cell budget; no n*n*p distance tensor is allocated.

## 13. Python Implementation

The from-scratch implementation is [python/solution.py](python/solution.py), with reusable `MeanShift` and the API described above. [python/example.py](python/example.py) is a fixed executable example. Core logic uses NumPy/local code, never a scikit-learn/SciPy estimator. Shared [support.py](../support.py) supplies strict contracts and stable Euclidean distances. Tests are in [tests/test_python.py](tests/test_python.py). Install [requirements-ml.txt](../../../../requirements-ml.txt) for runtime; use [requirements-ml-test.txt](../../../../requirements-ml-test.txt) for reference tests.

## 14. C++ Implementation

Classical ML has a Python-first policy. Optional C++ is **not implemented** here; there are no dummy C++ source/test files. DSA remains Python/C++ mandatory, with actual C++17/C++20 validation. This status is explicit in the catalog rather than represented by a fake implementation.

## 15. Input and Output Examples

From the repository root with the existing ML environment:

```sh
python machine-learning/unsupervised-learning/clustering/mean-shift/python/example.py
```

The independently justified labels are `[1, 1, 0, 0]`. Cluster IDs are conventional, not class meanings; the dry run explains their ordering. Equivalent Python API, from this topic's python directory:

```python
from solution import MeanShift
model = MeanShift(**{'bandwidth': 0.3, 'tol': 1e-08})
labels = model.fit_predict([[0], [0.1], [5], [5.1]])
```

The JSON CLI accepts exactly X and optional parameters and prints a labels object. Invalid input exits 2 with stderr and no labels JSON. Numeric comparisons use tolerances; exact labels are used only when the example/tie rule fixes them.

## 16. Edge Cases

Constant duplicates yield one exact mode. Small bandwidth can retain isolated singleton modes. Tiny uniform scales use stable norms, and a large common offset uses anchor-centered means. At hard radius boundaries finite precision can change membership. Relative stopping thresholds can underflow to zero at extremely tiny units, requiring an exact floating fixed point. No supported neighborhood or an exhausted seed raises an explicit convergence error.

Predict/transform before fit, where those methods exist, raises ValueError. Invalid hyperparameters are checked again at fit. Exhausted iterative fitting is not silently returned as converged. Unsupported keywords fail rather than being ignored.

## 17. Advantages

Does not require a chosen K, exposes every candidate/support and has a direct mean-shift/KDE-gradient interpretation.

## 18. Disadvantages and Limitations

Bandwidth still sets the grouping scale. Flat neighborhoods can be nonsmooth; convergence is bounded rather than universally guaranteed. Dense all-seed scanning is expensive. The greedy suppression rule and coordinate ties can differ from other valid mode-merging implementations. No Gaussian kernel, variable bandwidth, weights, bin seeding or production indexing is implemented.

## 19. When to Use It

Use for small data where mode locations and bandwidth effects are central and a fixed Euclidean radius is meaningful.

## 20. When Not to Use It

Avoid very large/high-dimensional data, a requirement for automatic bandwidth selection, a fixed-K objective or assumptions that every local mode is the globally densest mode.

## 21. Comparison With Related Algorithms

| Method | Update / grouping |
| --- | --- |
| Mean Shift | Neighborhood means and mode suppression at bandwidth |
| K-Means | Fixed-K assignments and centroid SSE |
| DBSCAN | Fixed-radius core connectivity, not mode ascent |

## 22. Interview Questions

1. Derive the relationship between the Epanechnikov gradient and a mean shift.
2. Why can different seeds converge to the same candidate?
3. What determines the retained mode order in the example?
4. Why does nearest-mode prediction differ from refitting modes?

## 23. Practice Problems

1. Reproduce the two neighborhood means and labels.
2. Finite-difference a kernel-density gradient away from radius boundaries.
3. Compare flat-kernel modes with sklearn using the same bandwidth and all-row seeds.

Validation commands, from the root:

```sh
python -m pytest machine-learning/unsupervised-learning/clustering/mean-shift -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
```

Oracles use independent formulas, exhaustive tiny cases or separately fitted references. Different valid labelings/trees/eigenvector signs are compared through the appropriate invariants. Marker groups overlap and are not additive. Seeds, data sizes and tolerances are fixed; no network dataset download or hidden library fit is used.

## 24. References

[scikit-learn Mean Shift guide](https://scikit-learn.org/1.8/modules/clustering.html#mean-shift).

References identify the mathematical method. The exact implemented subset, numeric domain, tie policy and unsupported features are stated here; external libraries can use different valid initialization, ordering, stopping or metric conventions.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE) · [Contribution guidance](../../../../CONTRIBUTING.md). Current Phase 16 review approval is pending.
