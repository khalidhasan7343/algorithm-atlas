# Bernoulli Naive Bayes

## 1. Algorithm Name

**Bernoulli Naive Bayes**, canonical `bernoulli-naive-bayes` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

Bernoulli NB classifies binary feature patterns, with both presence and absence supplying evidence. It estimates a presence probability for each class-feature pair and scores the product of Bernoulli factors in log space. Explicit binarization distinguishes this event model from counting repeated occurrences.

## 3. Problem Statement

For binary Bᵢⱼ∈{0,1}, class population nk and presence count Fkⱼ, estimate θkⱼ=(Fkⱼ+alpha)/(nk+2alpha). The joint log score is ℓk(x)=logπk+Σⱼ[Bⱼlogθkⱼ+(1−Bⱼ)log(1−θkⱼ)]. With binarize=None, inputs must be exact numeric 0/1. Otherwise Bⱼ=1 iff Xⱼ>binarize, including a strict inequality at the threshold. Sort original classes deterministically, choose the first score maximum and normalize shifted log scores for posteriors.

## 4. Why Do We Need This Algorithm?

In a binary event representation, absence can be as informative as presence. A count-based likelihood that sums only positive events would discard that information. Additive smoothing also prevents exact zero/one empirical presence estimates from producing log-zero failures on a new pattern.

## 5. Real-World Applications

Examples include small binary indicator sets or studying a toy word-presence representation independent of word frequency. Thresholded numerical measurements need a justified threshold; this implementation does not choose one from held-out targets. A binary indicator's predictive association does not establish causation.

## 6. Core Intuition

Each class supplies p independent coin models. A present feature contributes θ; an absent feature contributes 1−θ. Smoothing adds alpha pseudo-counts to each of two outcomes, explaining the denominator nk+2alpha rather than a sum across features. Logarithms turn those products into sums without losing absence terms.

## 7. Prerequisites

Know Bernoulli probability, Bayes' rule, binary indicators and stable log arithmetic. Compare [Multinomial NB](../multinomial-naive-bayes/README.md), whose denominator pools events across features and whose likelihood has no absent-feature term. [Gaussian NB](../gaussian-naive-bayes/README.md) instead describes real-valued conditional densities.

## 8. Step-by-Step Working Process

1. Validate/copy numeric X and labels, and validate alpha, optional threshold and priors.
2. If threshold is None, reject values other than exact 0/1; otherwise binarize using X>threshold. Negative raw measurements are allowed when an explicit threshold converts them to bits.
3. Count class rows and sum binary presences per class-feature. Compute θ=(presence+alpha)/(class_count+2alpha).
4. Store logθ and log1p(−θ), checking finite values before committing. The alpha lower bound and training-row cap keep representable probabilities away from exact zero/one.
5. Apply the fitted binarization threshold to each query, not a newly mutated constructor threshold. Compute both B·logθᵀ and (1−B)·logabsenceᵀ plus log priors.
6. Normalize shifted log scores or predict the first maximum in sorted class order. No optimizer or gradient iteration is needed.

The independence assumption defines the model. The arithmetic implementation does not justify that assumption statistically.

## 9. Pseudocode

```text
B = validate_exact_bits(X) if threshold is None else (X > threshold)
for class k:
  count = number_of_rows(k)
  presence = sum(B[rows(k)], axis=rows)
  theta[k] = (presence + alpha)/(count + 2*alpha)
  store log(theta[k]) and log1p(-theta[k])
score(query) = binary_query @ log_presence.T
             + (1-binary_query) @ log_absence.T + log_priors
predict first maximum; normalize shifted logs for probabilities
```

## 10. Dry Run

Class a has two [1,0] rows; b has two [0,1] rows. Alpha=1 gives θa=[3/4,1/4] and θb=[1/4,3/4], with equal priors. Query [1,0] has unnormalized likelihoods (1/2)(3/4)(1−1/4)=9/32 and (1/2)(1/4)(1−3/4)=1/32. Its posterior is [0.9,0.1], selecting a; query [0,1] selects b. Queries [0,0] and [1,1] tie at posterior [0.5,0.5]. The absence factor is essential: it is not a multinomial repeat-count term.

## 11. Time Complexity

Fit binarization and count aggregation cost O(np), plus O(n log n) label preparation. Query scoring costs O(mpc) through two dense products, and posterior normalization O(mc). Counts are sufficient statistics, so no per-query search over n training rows occurs. c≤32 and feature counts are explicitly bounded.

## 12. Space Complexity

Training uses O(np+cp+n) for checked/binarized arrays and class counts. Fitted state stores O(cp+c) presence/absence logs and priors, no training rows. Query work uses O(mp+mc), including binary features and scores. There is no recursive optimizer or external dataset storage.

## 13. Python Implementation

`BernoulliNaiveBayes(alpha=1.0, binarize=0.0, priors=None)` exposes fit, joint-log-score decision_function, predict_proba, predict and accuracy score. Alpha is in [10⁻⁹,10⁶]; threshold is None or finite in [−10¹²,10¹²]. Shared limits are n≤2048, p≤128, m≤10000 and 262144 cells; raw numeric magnitudes≤10¹². Homogeneous int64-compatible integer or nonempty string labels are supported, at most 32 classes; one class is valid. Priors, when supplied, are positive and sum to one in sorted classes_ order. Inspect feature_count_, feature_log_prob_, feature_log_absence_, class_count_, class_prior_, class_log_prior_ and fitted binarize_. Scores/probabilities are(m,c); original-label predictions(m,). No sparse input, sample weights or partial_fit.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/bernoulli-naive-bayes/python/example.py
```

Expected output:

```text
['a', 'b']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import BernoulliNaiveBayes
X = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]]
y = ["a", "a", "b", "b"]
model = BernoulliNaiveBayes().fit(X, y)
print(model.predict([[1.0, 0.0], [0.0, 1.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/bernoulli-naive-bayes -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

All-zero/all-one patterns, constant columns and one-observation classes are permitted. At exactly the threshold the bit is zero; the next representable larger value is one. With threshold None, fractional/negative/nonbinary values fail instead of being silently converted. Bool feature arrays are rejected by the common numeric contract; use explicit numeric 0/1. Empty shaped queries work. Wrong dimensions, nonfinite input, unsupported labels/priors and invalid parameter ranges raise ValueError. Failed refits preserve previous state, and later caller mutations do not change statistics.

## 17. Advantages

Explicit treatment of absence, deterministic multiclass behavior, compact sufficient statistics and stable log normalization. The binarization rule is captured at fit and exposed for reproducibility. Tiny hand-computed likelihoods can verify every part of a prediction.

## 18. Disadvantages and Limitations

Independent binary features can be an unrealistic model, and binarization discards magnitude/frequency information. The threshold is a modeling choice; it is not learned or tuned automatically. Smoothed finite likelihoods do not establish calibration. Duplicated correlated indicators may overstate evidence. This implementation intentionally rejects zero smoothing rather than supporting infinite event log scores.

## 19. When to Use It

Use it when binary presence/absence is the intended representation. Select thresholds/smoothing on training and validation data only; report held-out per-class confusion/precision/recall/F1 and log loss. Examine whether absent indicators influence predictions as intended.

## 20. When Not to Use It

Do not use it when event frequency itself is the main signal without accepting the information loss. Do not reuse Multinomial NB's event normalization or ignore absence terms. Do not silently treat missing observations as absent bits; missing numerical values are rejected and need a separate training-fitted policy outside this estimator.

## 21. Comparison With Related Algorithms

| Related classifier | Difference |
| --- | --- |
| Multinomial NB | Nonnegative repeated counts; denominator pools events across features |
| Gaussian NB | Independent continuous densities |
| Logistic Regression | Discriminative binary probability model, not a product of per-class indicator models |
| ID3 | Learns categorical splits and interactions instead of multiplying independent features |

## 22. Interview Questions

Why is the denominator nk+2alpha? Derive the absent-feature term. How does exact-threshold behavior affect a reproducible test? What information is lost by binarization? Why should missing values not automatically be interpreted as absence?

## 23. Practice Problems

1. Compute posteriors for all four two-bit patterns in the dry run.
2. Construct a case where presence-only and correct presence/absence scoring select different classes.
3. Compare validation-selected thresholds on a fixed split, reporting both macro F1 and log loss on a final untouched held-out set.

## 24. References

- [scikit-learn Bernoulli NB formulation](https://scikit-learn.org/1.8/modules/naive_bayes.html#bernoulli-naive-bayes).
- [NumPy log1p](https://numpy.org/doc/2.3/reference/generated/numpy.log1p.html).

Tests independently multiply presence and absence factors, cover threshold equality and compare seeded reference posteriors under matched alpha, threshold and priors.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
