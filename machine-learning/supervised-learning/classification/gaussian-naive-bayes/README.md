# Gaussian Naive Bayes

## 1. Algorithm Name

**Gaussian Naive Bayes**, canonical `gaussian-naive-bayes` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

Gaussian NB is a generative classifier: estimate a Gaussian distribution for each feature within each class, multiply conditional densities under an independence assumption, and combine with class priors. Computation uses additive log densities and stable normalization instead of multiplying many tiny numbers. All sufficient statistics and likelihood logic are implemented here.

## 3. Problem Statement

For n×p numerical X and class k, estimate prior πk=nk/n, feature mean μkⱼ and population variance vkⱼ=(1/nk)Σᵢ:yᵢ=k(Xᵢⱼ−μkⱼ)². Add epsilon=var_smoothing·max(1,maxⱼVar(Xⱼ)) to every variance. The joint log score is ℓk(x)=logπk−½Σⱼ[log(2π(vkⱼ+epsilon))+(xⱼ−μkⱼ)²/(vkⱼ+epsilon)]. Predict the largest score, ties by sorted class. Probabilities normalize exp(ℓk) across classes; the modeled product is a density, not a discrete probability of observing an exact real vector.

## 4. Why Do We Need This Algorithm?

Direct density products can underflow in many dimensions, and empirical zero variances cause division by zero. A diagonal Gaussian model provides a compact numerical baseline while log arithmetic and an explicit variance floor handle those implementation problems. The independence approximation reduces parameter/storage cost but can be wrong for correlated features.

## 5. Real-World Applications

Examples include a modest continuous-feature classification baseline, studying generative-versus-discriminative assumptions, or examining how variance and priors change Gaussian decision scores. Measurements should have a plausible within-class density model. Good classification on one synthetic split does not establish calibrated posterior probabilities on another population.

## 6. Core Intuition

Bayes' rule gives P(k|x) proportional to πkP(x|k). Conditional independence replaces a joint feature density by a product of univariate Gaussians, so logs turn products into sums. The class-independent evidence denominator is unnecessary for argmax but is restored by normalizing shifted log scores. Smoothing adds positive variance even for single-observation classes or globally constant columns.

## 7. Prerequisites

Know Gaussian mean/variance, log densities, Bayes' rule and conditional independence. [Multinomial NB](../multinomial-naive-bayes/README.md) models count events; [Bernoulli NB](../bernoulli-naive-bayes/README.md) models binary presence and absence. [QDA](../quadratic-discriminant-analysis/README.md) models full class covariances instead of diagonal ones.

## 8. Step-by-Step Working Process

1. Validate/copy dense real X and homogeneous labels; sort classes deterministically and count their observations.
2. Use empirical priors or validate supplied positive priors summing to one in sorted class order.
3. Compute the global population variances and epsilon using the explicit max(1,variance) scale. For each class calculate feature means and population variances, then add epsilon.
4. On query, compute each class's joint log density one class at a time; this avoids allocating an m×c×p tensor.
5. Predict the first maximum in sorted class order. For probabilities subtract the row maximum from log scores before exponentiating and divide by the shifted sum.
6. Fit commits statistics only after successful validation/numerical work; a failed refit preserves prior state.

There is no iterative optimizer, gradient stopping criterion or convergence budget. Estimated moments maximize the separate Gaussian likelihoods before smoothing; smoothing deliberately modifies that statistical estimate.

## 9. Pseudocode

```text
encode sorted classes; class_count = counts(y)
epsilon = smoothing * max(1, maximum_global_population_variance)
for class k:
  mean[k] = column means of its training rows
  variance[k] = population variances + epsilon
  prior[k] = empirical or validated supplied prior
for query/class pair:
  score = log(prior) - half_sum(log(2*pi*variance) + squared_residual/variance)
predict first maximum; probabilities = normalized exp(score-row_max)
```

## 10. Dry Run

Train class a on x=[0,1] and class b on x=[5,6]. Both have prior 1/2, means 1/2 and 11/2, and unsmoothed variance 1/4. The global mean is 3 and global variance is (9+4+4+9)/4=6.5, so default epsilon is 6.5×10⁻⁹. At x=0, the squared residuals are 1/4 and 121/4; equal priors/variances make class a score larger. At x=6, symmetry selects b. With all features constant and class proportions 1/4 versus 3/4, identical likelihoods leave the posterior equal to those priors.

## 11. Time Complexity

Sufficient-statistic work is O(np) plus O(n log n) deterministic label preparation, with c≤32. Computing scores on m queries costs O(mcp). Class iteration keeps arithmetic explicit and avoids a covariance factorization. No O(p³) solve is required because covariances are diagonal.

## 12. Space Complexity

Fit uses O(np+cp+n) including the owned checked input and per-class moments. The fitted model stores O(cp+c) means, variances, priors and counts, not training rows. Query copying uses O(mp); scores/probabilities use O(mc), and one class's residual workspace O(mp). No recursive optimizer or binary checkpoint is produced.

## 13. Python Implementation

`GaussianNaiveBayes(var_smoothing=1e-9, priors=None)` supports multiclass/single-class fit, joint-log-score decision_function, predict_proba, predict and accuracy score. Smoothing is finite in [10⁻¹²,1]. Priors are optional positive values summing to one, one per sorted class. Shared dense limits are n≤2048, p≤128, m≤10000, at most 262144 X/query cells and finite |feature|≤10¹². y is 1D homogeneous int64 integers or nonempty strings, at most 32 classes; no ambiguous reshaping or mixed coercion. classes_ gives probability columns. Inspect theta_, var_ (already smoothed), epsilon_, class_count_, class_prior_ and class_log_prior_. Scores/probabilities have shape(m,c), predictions shape(m,). Fit returns self; no weights, online partial fitting or random state.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/gaussian-naive-bayes/python/example.py
```

Expected output:

```text
['a', 'b']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import GaussianNaiveBayes
X = [[0.0], [1.0], [5.0], [6.0]]
y = ["a", "a", "b", "b"]
model = GaussianNaiveBayes().fit(X, y)
print(model.predict([[0.0], [6.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/gaussian-naive-bayes -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

A one-row class is valid: its raw variances are zero and smoothing supplies positive denominators. Constant columns and globally constant data remain finite; a single-class posterior is one. Empty shaped queries work. NaN/Inf, bool/complex/string features, unsupported labels, wrong dimensions, invalid priors or smoothing bounds raise ValueError. Failed refits preserve old statistics; inputs are not mutated. Extremely distant observations can produce sharply saturated posteriors, but log scores remain meaningful within documented bounds.

## 17. Advantages

Fast, small-state, multiclass and transparent. Every class score decomposes into prior and per-feature Gaussian terms. The variance floor handles degenerate small datasets, and log normalization avoids the direct product underflow seen in high-dimensional naive likelihood multiplication.

## 18. Disadvantages and Limitations

Conditional independence and within-class Gaussian assumptions can be poor. Correlated features can count related evidence more than once and distort probabilities. The unit-scale floor means smoothing depends on feature units; match it explicitly in external comparisons. A positive variance floor ensures numerical denominators, not accurate density estimation or calibration. No full covariance, missing-value policy, sparse arrays or sample weights are implemented.

## 19. When to Use It

Use it as a simple continuous-feature baseline, checking held-out confusion matrix and class-specific precision/recall/F1 as well as accuracy/log loss. Fit any preprocessing only on training rows. Compare priors and class populations when a minority class has little data.

## 20. When Not to Use It

Do not treat integer word counts as automatically Gaussian or assume predictive independence merely because the code multiplies densities. Do not use a posterior as calibrated decision confidence without evaluation. If covariance interactions matter and data support their estimation, compare LDA/QDA within the authorized category.

## 21. Comparison With Related Algorithms

| Model | Conditional feature model |
| --- | --- |
| Gaussian NB | Independent Gaussian densities per class |
| Multinomial NB | Nonnegative event-count likelihood |
| Bernoulli NB | Binary presence and absence probabilities |
| QDA | Full class-specific covariance, a different parameter/data requirement |

## 22. Interview Questions

Derive the joint log score. Why can the evidence denominator be omitted for prediction but not for probabilities? How does smoothing handle one-row classes? Explain why matched epsilon matters in reference comparisons. Why is density at a point not the probability of that exact real observation?

## 23. Practice Problems

1. Calculate the two dry-run scores at x=3 and explain the tie.
2. Duplicate a strongly correlated feature and observe how an independence approximation changes posterior sharpness.
3. Evaluate a fixed held-out dataset with an imbalanced class distribution, retaining separate per-class metrics and recording smoothing.

## 24. References

- [scikit-learn Gaussian NB mathematical formulation](https://scikit-learn.org/1.8/modules/naive_bayes.html#gaussian-naive-bayes).

Reference tests align epsilon explicitly: this implementation uses max(1,global_variance), while the library's variance scale can differ. Analytical likelihood tests cover globally constant inputs independently rather than comparing two undefined zero-variance densities.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
