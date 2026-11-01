# Local Outlier Factor — Tie-Inclusive Training Detection

## 1. Algorithm Name

Local Outlier Factor compares local reachability densities,not merely nearest-neighbor distance. This canonical uses exact tie-inclusive neighborhoods,excludes only the same row index,and exposes training-only outlier detection rather than unsupported novelty inference.

## 2. Overview

Given an unlabeled finite reference matrix,compute each training observation local density relative to its k-distance neighborhood. A score near1 means comparable local density;larger ratios indicate local sparsity. LOF is not a probability,and a value just above1 is not automatically an anomaly.

## 3. Problem Statement

fit(X) requires2..256 finite rows and1..32 features,magnitudes<=1e12. n_neighbors k is1..n-1 (constructor bound1..255). Euclidean metric only. contamination is auto or a finite fraction in(0,.5]. Scoring/prediction methods take no query matrix;passing X to those methods raises ValueError because novelty mode is not implemented.

distance_matrix_,k_distances_,neighborhoods_,reachability_distances_ expose the genuine geometry. mean_reachability_,log_mean_reachability_,zero_reachability_,lrd_,log_lrd_,density_representation_overflow_ distinguish mathematical zeros from float representation limits. anomaly_scores()/anomaly_scores_ contain raw LOF;log_lof_ retains its logarithm. score_samples()=-LOF,decision_function() applies the declared extended threshold,predict() returns+1/-1,fit_predict(X) returns training labels.

## 4. Why Do We Need This Algorithm?

Different legitimate clusters can have different global densities. Comparing each observation to its own neighbors can reveal relative local sparsity that a single global density or distance cutoff would obscure.

## 5. Real-World Applications

Small reference-set anomaly studies with heterogeneous local densities are suitable applications. This implementation scores its training observations only; a future-point novelty service requires a separately specified model rather than silently expanding the reference set.

## 6. Core Intuition

N_k(p) contains every other row with distance<=the kth other-row distance,including all ties. Reach(p,o)=max(kdist(o),distance(p,o));r_p=mean(reach(p,o));lrd_p=1/r_p;LOF_p=mean(lrd_o/lrd_p)=mean(r_p/r_o). For ordinary positive means,compute log means and log-mean-exp density ratios. This preserves the actual ratio even if a displayed lrd overflows. No stabilizing epsilon or fixed-size neighbor truncation changes the canonical neighborhood.

A neighbor distance is judged against that neighbor own k-distance. This stabilizes dense-cluster reachability and lets a point compare itself to the densities of its local references. Different global cluster densities can be normal within their own neighborhoods.

## 7. Prerequisites

Euclidean distances,order statistics,k-distance ties,reachability density,ratios and stable logarithmic arithmetic are prerequisites. Understand exact-zero versus representation-overflow diagnostics,duplicate-limit conventions and threshold ties.

## 8. Step-by-Step Working Process

Compute stable Euclidean distances with the approved B4 helper. Select each kth other-row distance,then include all equal-distance ties. Form reachability values using neighbor k-distances. Compute scaled mean/log-mean reachability and exact-zero flags. Average density ratios in log space. Apply the explicitly declared duplicate limit when necessary,then threshold training raw scores with tie-aware extended quantiles.

## 9. Pseudocode

```text
D <- pairwise Euclidean distances
for each p:
    kdist[p] <- kth distance excluding self index
    N[p] <- all other rows with D[p,o]<=kdist[p]
    reach[p,o] <- max(kdist[o],D[p,o])
    r[p],log_r[p],zero[p] <- stable mean reach
for each p:
    if exact-zero duplicate pile:LOF[p] <- 1
    elif positive r[p] with zero-r neighbor:LOF[p] <- +infinity
    else:LOF[p] <- log-stable mean(r[p]/r[o])
return training cutoff,decisions and labels
```

## 10. Dry Run

For X=[-11,-10,0,10] and k1,k-distances are[1,1,10,10]. The center0 has two tied neighbors,-10 and10,not one arbitrarily selected neighbor. Its mean reach is10;neighbor means are1 and10. Its LOF is(10/1+10/10)/2=5.5,while the other scores are1. Independent tests state these numbers and separately calculate complete neighborhoods/reachability/densities.

## 11. Time Complexity

Dense distances cost O(n²*d). Sorting each full row costs O(n² log n). Tie-inclusive neighborhood/reachability/ratio work costs O(n²) worst case because a neighborhood can include all n-1 other rows. Training-score quantile sorting adds O(n log n). This is a bounded brute-force implementation,not an indexed-neighbor scalability claim.

## 12. Space Complexity

Distance matrix and tie-inclusive neighbor/reachability storage cost O(n²),plus O(n*d) owned features and O(n) scalar/log diagnostics. No tree index or external nearest-neighbor estimator is used. The explicit n<=256 cap bounds dense allocations.

## 13. Python Implementation

The canonical [LocalOutlierFactor](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B12 contracts](../../../docs/anomaly-detection-conventions.md) define validation and ownership. No ready-made anomaly detection estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/anomaly-detection/local-outlier-factor/python/example.py
```

Actual captured output:

```json
{"training": [[-11.0], [-10.0], [0.0], [10.0]], "neighbors": [[1], [0], [1, 3], [2]], "k_distance": [1.0, 1.0, 10.0, 10.0], "mean_reach": [1.0, 1.0, 10.0, 10.0], "density": [1.0, 1.0, 0.09999999999999998, 0.09999999999999998], "lof": [1.0, 1.0, 5.5, 1.0], "threshold": 1.5, "decisions": [0.5, 0.5, -4.0, 0.5], "labels": [1, 1, -1, 1], "status": "training-lof-computed"}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/anomaly-detection/local-outlier-factor -q`.

## 16. Edge Cases

Ties may produce neighborhoods larger than k. Identical points/duplicate piles can have exactly zero mean reach and infinite lrd. The original paper assumes no duplicates;our explicit extension uses the common r+epsilon limit:an all-zero duplicate neighborhood has LOF1;positive reach with a zero-reach neighbor has genuine LOF+infinity. A positive but tiny mean can instead have representation-overflow lrd with a finite log density and ordinary finite LOF. Finite but unrepresentable LOF raises NumericalError. No uncontrolled NaNs or arbitrary huge finite stand-ins.

## 17. Advantages

Exact neighborhood semantics and full geometric diagnostics support hand verification. Local comparison can accommodate different cluster densities. Stable log ratios preserve tiny-scale behavior without silently adding an epsilon to the mathematical model.

## 18. Disadvantages and Limitations

Training-set detection only;no unseen query novelty API. Dense n² work and storage limit scale. k and metric choices materially affect scores;no universal anomaly ranking. Duplicate/infinite-density handling is a declared extension,not a claim that the original paper specifies it. Extended raw scores are not probabilities and may complicate quantile ties;no exact requested anomaly count is forced.

## 19. When to Use It

Use when local rather than global sparsity is the intended anomaly concept and the reference training set itself is the object of detection. Inspect neighbor sets and density ratios,choose k using permitted training/application knowledge,and evaluate with labels only after unsupervised fitting.

## 20. When Not to Use It

Do not call a fixed-k tie-truncated neighbor average the exact definition implemented here. Do not pass new query rows to training-only scoring or concatenate queries into the reference set and pretend the learned model is unchanged. Use Isolation Forest or One-Class SVM for the supported unseen-query API.

## 21. Comparison With Related Algorithms

Isolation Forest uses isolation depth;One-Class SVM estimates kernel support;LOF compares reachability densities. sklearn uses fixed-k neighbors and an additive1e-10 stabilizer,so reference comparisons here require unique kth distances and ordinary nondegenerate scales. Their duplicate/tie outputs need not match this declared extension.

## 22. Interview Questions

Whose k-distance enters reachability? The neighbor own k-distance. Can a neighborhood contain more than k points? Yes,all kth-distance ties are included. Why avoid direct infinity/infinity lrd ratios? Log mean-reach ratios distinguish true zeros from representational overflow. Why can numeric contamination label no outliers? An infinite-score tie may be the quantile boundary.

## 23. Practice Problems

Hand-compute the four-point tie witness. Compare tie-inclusive neighborhoods to two possible fixed-k choices. Derive the common-epsilon limit for duplicate piles. Verify scale/translation/permutation behavior where floating assumptions hold. Compare to sklearn only after checking that every neighborhood has exactly k members and density stabilizers are negligible.

## 24. References

[https://sigmodrecord.org/2000/06/07/lof-identifying-density-based-local-outliers/](https://sigmodrecord.org/2000/06/07/lof-identifying-density-based-local-outliers/)

[https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html)

The [phase conventions](../../../docs/anomaly-detection-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

