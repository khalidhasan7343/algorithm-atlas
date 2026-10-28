# K-Nearest Neighbors

## 1. Algorithm Name

**K-Nearest Neighbors**, canonical `k-nearest-neighbors` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

KNN classification stores labeled observations and predicts by voting among the k closest training rows. This implementation explicitly computes dense Euclidean distances, stably orders neighbors and counts uniform class votes. It has no tree index or learned distance metric; training is storage and validation, while most computation occurs at query time.

## 3. Problem Statement

Given X∈Rⁿˣᵖ, original class labels y and integer 1≤k≤n, compute d(x,xᵢ)=sqrt(Σⱼ(xⱼ−Xᵢⱼ)²) for each query. Select the k smallest distances; equal distances retain original training-row order. Count selected labels and choose the largest count; class-count ties choose the first sorted class. predict_proba returns neighbor vote fractions in classes_ order. These fractions are empirical local estimates, not a guarantee of calibrated probabilities.

## 4. Why Do We Need This Algorithm?

A single affine boundary can miss local structure. Nearest-neighbor voting provides a direct baseline based on a transparent geometric similarity rule, without fitting a global coefficient vector. Its behavior depends strongly on feature units, k and which observations are retained, making it useful for studying the distinction between representation, distance and classification.

## 5. Real-World Applications

Examples include recognizing a nearby pattern in a small measured-feature collection or comparing a learned classifier with a local-memory baseline. Distances require meaningful numerical coordinates; integer codes for unrelated categories do not automatically have meaningful Euclidean spacing. Stored training rows can reveal sensitive data, so this educational implementation uses synthetic local datasets only.

## 6. Core Intuition

For each query the prediction minimizes no global training loss. It is the majority class of an explicitly selected neighborhood. Small k can follow noisy individual labels; larger k smooths neighborhoods but can ignore local boundaries. Scaling one feature changes distances and may change the neighborhood even when all labels stay fixed. Deterministic ties are necessary because multiple equally valid neighbors may straddle the k boundary.

## 7. Prerequisites

Understand Euclidean distance, sorting, class counts and training/test separation. [Logistic Regression](../logistic-regression/README.md) learns parameters instead of retaining every row. The algorithm needs no gradient, convergence criterion or random seed. Know why preprocessing must be fitted only using training observations.

## 8. Step-by-Step Working Process

1. Require a native-integer k and validate/copy X and labels. Reject k greater than the training count. Store sorted classes and encoded labels, preserving original row order.
2. On query, check fitted state, dimensions and both matrix and m·k output budgets. Process query blocks sized so the temporary query×training×feature difference tensor stays within the shared cell limit.
3. Subtract coordinates directly and sum squared differences. This avoids the cancellation of ||x||²+||z||²−2xᵀz when vectors have large common offsets.
4. Stable-sort squared distances for each query, take the first k indices, and return square-rooted distances from kneighbors.
5. Count encoded labels among those rows and divide by k. Choose argmax in sorted class order for a deterministic class-vote tie. No exact-zero-distance special weighting is used; all selected neighbors vote once.

The search is exhaustive: each stored row is considered. The tie convention is part of the public contract, rather than an incidental ordering assumed to match every external library.

## 9. Pseudocode

```text
FIT(X,y): validate k <= n; copy X; encode sorted classes; store k
KNEIGHBORS(query):
  validate fitted dimensions and output budget
  for each bounded query block:
    squared = sum((query_block[:,None,:]-training_X[None,:,:])**2, features)
    order = stable_argsort(squared)[:, :k]
    store order and sqrt(selected squared distances)
PREDICT_PROBA(query): count each class in selected labels; divide by k
PREDICT(query): return first sorted class with maximum vote fraction
```

## 10. Dry Run

Train on x=[−1,1,1,3] and labels [z,a,b,a], with k=2. At query x=1, squared distances are [4,0,0,4]. The two zero-distance rows have original indices 1 and 2, so votes are one a and one b. Sorted classes are [a,b,z]; probabilities are [1/2,1/2,0], and the prediction is a. With k=1 at query zero, rows 0 and 1 are equally near; original row 0 wins, predicting z. With k=n, probabilities are [1/2,1/4,1/4] for every query.

## 11. Time Complexity

Fit validation/encoding and copying costs O(np+n log n), with sorted distinct labels bounded at 32. For m queries, direct distance work costs O(mnp), stable full sorting O(mn log n), and votes O(m(k+c)) for c classes. kneighbors returns only k neighbors but deliberately sorts all n; no O(log n) indexed-query claim is made. Increasing n shifts both storage and inference costs.

## 12. Space Complexity

Fitted storage costs O(np+n+c), including owned rows, encoded labels and classes. kneighbors needs O(mk) outputs and bounded block workspace O(bnp+bn), with b chosen from the cell budget. Query copying costs O(mp). Class probabilities add O(mc). The m·k budget prevents a valid small-feature query from creating an unexpectedly huge neighbor-output matrix.

## 13. Python Implementation

`KNearestNeighbors(n_neighbors=5)` exposes fit, kneighbors, predict, predict_proba and accuracy score. k is a native integer in 1..2048 and must not exceed n at fit. X has n≤2048, p≤128 and at most 262144 cells; queries have m≤10000, the same cell cap and m·k≤262144. Numeric values must be finite, real and |value|≤10¹². Labels are one homogeneous family of int64-compatible integers or nonempty strings, at most 32 sorted classes; single-class data are allowed. kneighbors returns (distances,indices), both shape(m,k); predict_proba returns(m,c), predict returns(m,) original labels. n_neighbors_ captures the fitted k independently of later constructor-attribute changes. Fit returns self and owns all retained arrays. There are no distance weights, alternative metrics, approximate searches or randomness.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/k-nearest-neighbors/python/example.py
```

Expected output:

```text
['a']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import KNearestNeighbors
X = [[-1.0], [1.0], [1.0], [3.0]]
y = ["z", "a", "b", "a"]
model = KNearestNeighbors(n_neighbors=2).fit(X, y)
print(model.predict([[1.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/k-nearest-neighbors -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

k=1, k=n, identical observations, repeated labels and contradictory duplicate rows are valid. Exact distance ties use original row order; class ties use sorted label order. Empty shaped queries return empty outputs. Invalid k, dimensions, nonfinite/complex/bool/string features, mixed/float/bool labels and exceeded budgets raise ValueError. A failed refit leaves the previous model unchanged. Predict-before-fit is an error. Direct differences remain useful for large common offsets, but cannot recover differences already rounded out of float64 input values.

## 17. Advantages

Simple, multiclass, deterministic and easy to audit with a scalar distance oracle. It can model nonlinear local regions without a parameter optimizer. Neighbor indices and vote fractions expose the evidence used for each prediction. Training cost is modest for the explicitly bounded dataset.

## 18. Disadvantages and Limitations

Inference and stored data grow with n; full sorting is more expensive than specialized selection/index structures. Irrelevant features, inconsistent units, high dimensionality, duplicate-label conflicts and sparse local coverage can impair predictions. Vote fractions are not guaranteed calibrated, and k cannot be chosen by inspecting final test targets. This dense implementation lacks sample weights, learned metrics, missing-value handling and sparse matrices.

## 19. When to Use It

Use it as a small-data geometric baseline when feature distances are meaningful. Fit any scaler on training data only, choose k on validation data, and report held-out accuracy plus per-class precision/recall/F1 and confusion matrix. Inspect neighborhoods near a failure rather than assuming the majority vote expresses certainty.

## 20. When Not to Use It

Avoid raw Euclidean distance on arbitrary category codes or features whose units make one dimension dominate unintentionally. Do not claim a tree-based nearest-neighbor index or cheap large-n queries. When training data cannot be retained, use a permitted model whose fitted state summarizes them instead.

## 21. Comparison With Related Algorithms

| Alternative | Difference |
| --- | --- |
| Logistic Regression | Learned affine probability model with a smooth training objective |
| CART | Learned threshold partitions and leaf distributions |
| Gaussian NB | Parametric per-class feature densities |
| Weighted KNN | Changes the vote rule; intentionally not implemented here |

## 22. Interview Questions

Why can stable row order matter at the k boundary? How do vote ties differ from distance ties? Explain why k=n yields query-independent vote fractions. What is the time complexity of this full-sort implementation? Why can changing feature units change the result?

## 23. Practice Problems

1. Trace the dry run for k=1,2,4 at three queries.
2. Write a Python scalar distance/sort/vote oracle and compare on fixed-seed tiny integer datasets with deliberate ties.
3. Fit a scaler only on training rows and compare validation-selected k values, retaining one untouched test split and avoiding universal superiority claims.

## 24. References

- [scikit-learn nearest-neighbor classification](https://scikit-learn.org/1.8/modules/neighbors.html#nearest-neighbors-classification).
- [NumPy stable argsort](https://numpy.org/doc/2.3/reference/generated/numpy.argsort.html).

Independent tests enumerate scalar distances and row-index ties. Library comparisons use data without tied boundary distances so implementation-specific neighbor ordering cannot invalidate a correct contract.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
