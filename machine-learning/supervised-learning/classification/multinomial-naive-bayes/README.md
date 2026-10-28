# Multinomial Naive Bayes

## 1. Algorithm Name

**Multinomial Naive Bayes**, canonical `multinomial-naive-bayes` in Phase 14 B2 Supervised Learning — Classification.

## 2. Overview

Multinomial NB classifies nonnegative event-count vectors using class-specific feature occurrence probabilities. Additive smoothing prevents unseen events from receiving log zero. The implementation explicitly aggregates counts and computes log likelihoods; it is not a Gaussian model or a wrapper around a reference classifier.

## 3. Problem Statement

For class k and feature j, let Fkⱼ=Σᵢ:yᵢ=kXᵢⱼ. With p features and alpha>0, θkⱼ=(Fkⱼ+alpha)/(ΣₗFkₗ+p·alpha). The joint class score for query x is ℓk(x)=logπk+Σⱼxⱼlogθkⱼ. Predict the first maximum over sorted classes; normalize shifted log scores for posterior probabilities. X must be nonnegative. Integer counts have the literal multinomial event interpretation; nonnegative fractional weights are accepted as the same algebraic extension. The count-vector combinatorial factor is omitted because it is common across classes.

## 4. Why Do We Need This Algorithm?

A training class can have no observed instances of a feature. Unsmoothed probabilities then assign zero likelihood to a query containing that event, overwhelming all other evidence. Additive smoothing resolves this while preserving a simple count-based classifier, and log arithmetic prevents long event sequences from underflowing as direct products.

## 5. Real-World Applications

Examples include a small numerical bag-of-events representation or a toy document-term count exercise. This lesson does not perform tokenization, download corpora or justify a particular text representation. Features must represent comparable event coordinates; negative transformed features are outside this event model.

## 6. Core Intuition

Within each class, pool observed feature occurrences into one categorical event distribution θk. A query with repeated events contributes one logθ term per count, so its length affects evidence strength. The label prior is estimated from numbers of training rows, not numbers of events. These two counts play different roles and should not be conflated.

## 7. Prerequisites

Know Bayes' rule, count aggregation, categorical probabilities, additive smoothing and log products. [Bernoulli NB](../bernoulli-naive-bayes/README.md) includes absent-feature terms; Multinomial NB does not. [Gaussian NB](../gaussian-naive-bayes/README.md) instead estimates continuous means/variances.

## 8. Step-by-Step Working Process

1. Validate/copy X and labels; reject every negative feature at fit and query time. Encode deterministic sorted classes.
2. Count rows per class and choose empirical priors or supplied positive priors summing to one.
3. Sum each feature's counts within each class. Add alpha to every class-feature count and sum the smoothed counts across features.
4. Store logθ as log(smoothed_count)−log(smoothed_total), with finite checks before committing the fit.
5. For a query compute Xquery·logθᵀ+logprior. The all-zero vector contributes no event terms and therefore has posterior equal to the priors.
6. Normalize by subtracting each row's largest log score before exponentiation. Argmax ties select the first sorted class.

No iterative optimization or gradient stopping rule is relevant. Smoothing deliberately changes empirical frequency estimates; it is part of the statistical contract.

## 9. Pseudocode

```text
reject negative X; encode classes
for class k:
  feature_count[k] = sum(X[rows with class k], axis=rows)
  smoothed = feature_count[k] + alpha
  feature_log_prob[k] = log(smoothed) - log(sum(smoothed))
store empirical or supplied class priors
score(query) = query @ feature_log_prob.T + log(priors)
posterior = normalized_exp(score-row_max)
prediction = first sorted class maximizing score
```

## 10. Dry Run

Class left has rows [3,0],[2,1], giving feature totals [5,1]; class right has [0,3],[1,2], giving [1,5]. Each class has prior 1/2. Alpha=1 gives θleft=[6/8,2/8]=[3/4,1/4], θright=[1/4,3/4]. Query [2,0] has unnormalized scores in probability space [(1/2)(3/4)²,(1/2)(1/4)²], hence posterior [0.9,0.1] and prediction left. Query [0,2] reverses these; query [0,0] leaves [0.5,0.5] and deterministically selects left.

## 11. Time Complexity

For n rows, p features and c classes, aggregation costs O(np), plus O(n log n) deterministic label preparation. Query scores cost O(mpc) through dense matrix multiplication and normalization O(mc). There is no iterative training or covariance factorization. c is explicitly bounded at 32.

## 12. Space Complexity

Checked fit input costs O(np), and class statistics use O(cp+c). The fitted model retains feature counts/log probabilities and priors, not observations. A query needs O(mp+mc) space. Avoiding direct event-product evaluation requires no extra dataset-sized object or external service.

## 13. Python Implementation

`MultinomialNaiveBayes(alpha=1.0, priors=None)` exposes fit, joint-log-score decision_function, predict_proba, predict and accuracy score. Alpha is finite in [10⁻⁹,10⁶]; zero smoothing is intentionally unsupported. Priors, if given, are positive and sum to one in sorted classes_ order. Shared bounds: n≤2048, p≤128, m≤10000, 262144 cells and feature magnitudes≤10¹². Features are finite nonnegative numeric values; labels are homogeneous int64-compatible integers or nonempty strings, at most 32 classes. Fitted feature_count_ and feature_log_prob_ have shape(c,p); class_count_, class_prior_ and class_log_prior_ have shape(c,). Prediction probabilities/scores are(m,c), predicted original labels(m,). No sample weights, online updates or sparse inputs.

## 14. C++ Implementation

C++ is **optional and not implemented** for this classical ML topic. There is no dummy source or C++ test. The catalog's cpp_status remains planned as an honest optional deliverable, independent of Python/numerical completion. Existing DSA algorithms still require Python/C++, both test files and C++17/C++20 gates. See the [ML standard](../../../../docs/ml-development.md).

## 15. Input and Output Examples

From the repository root, install `requirements-ml.txt` for runtime, or `requirements-ml-test.txt` for tests/references. Run:

```sh
python machine-learning/supervised-learning/classification/multinomial-naive-bayes/python/example.py
```

Expected output:

```text
['left', 'right']
```

Equivalent API code, run from this topic's python directory:

```python
from solution import MultinomialNaiveBayes
X = [[3.0, 0.0], [2.0, 1.0], [0.0, 3.0], [1.0, 2.0]]
y = ["left", "left", "right", "right"]
model = MultinomialNaiveBayes().fit(X, y)
print(model.predict([[2.0, 0.0], [0.0, 2.0]]).tolist())
```

The standalone solution.py also accepts JSON with X,y,predict and optional constructor parameters, then returns predictions using original labels. Invalid input or non-convergence exits 2 with stderr and no success JSON. Execute tests with `python -m pytest machine-learning/supervised-learning/classification/multinomial-naive-bayes -q`. The dry-run output is verified by the example checker, not inferred from a planning page.

## 16. Edge Cases

All-zero rows, all-zero class event totals and single-class data remain valid because alpha is positive. Extremely long/fractional count rows use finite log scores; small class probabilities may round to zero after normalization without invalidating the log calculation. Negative features, nonfinite values, bool/complex/string matrices, wrong dimensions, invalid labels/priors and budget violations raise ValueError. Empty shaped queries work. Predict-before-fit is rejected; failed refits preserve old sufficient statistics and caller arrays are never mutated.

## 17. Advantages

Small-state, deterministic, multiclass and directly auditable through event totals. Additive smoothing and log scores handle unseen features and long count vectors. The count and prior roles are exposed rather than hidden in a generic fitting framework.

## 18. Disadvantages and Limitations

The event independence model is a strong approximation. Correlated or repeated derived features can overstate evidence, and arbitrary negative standardization is incompatible with the domain. Count length affects posterior sharpness. Nonnegative fractional weights retain the scoring rule but need not have a literal integer multinomial likelihood. This implementation omits vocabulary construction, sparse storage and calibrated confidence guarantees.

## 19. When to Use It

Use it for a small, explicitly nonnegative event representation. Preserve feature-coordinate meaning between train and test, select smoothing with training/validation data and inspect per-class metrics plus log loss on held-out data. Fit representation transforms only on training data.

## 20. When Not to Use It

Do not feed negative centered counts or treat continuous sensor values as multinomial events without a justified representation. Do not replace absent-feature likelihood terms with this formula when the intended model is Bernoulli. Avoid interpreting a high posterior as a universal confidence measure without checking the model assumptions and data distribution.

## 21. Comparison With Related Algorithms

| Model | Difference |
| --- | --- |
| Bernoulli NB | Binary event presence plus absence; repeated counts do not add repeated votes |
| Gaussian NB | Continuous independent Gaussian feature densities |
| Logistic Regression | Discriminative binary cross-entropy, not a pooled event model |
| KNN | Stores observations and compares distances |

## 22. Interview Questions

Derive the smoothed feature denominator. Why are class priors based on rows while θ is based on events? Why may the combinatorial factor be omitted for class comparison? What happens to all-zero queries? Explain the difference between fractional-weight scoring and an integer-count probability model.

## 23. Practice Problems

1. Repeat the dry run with alpha=0.5 and alpha=100.
2. Construct an unseen event and compare smoothed versus mathematically unsmoothed likelihoods without enabling unsupported alpha zero in the API.
3. Use a fixed held-out count dataset to compare smoothing values selected on validation data and report macro/weighted F1 as well as accuracy.

## 24. References

- [scikit-learn Multinomial NB formulation](https://scikit-learn.org/1.8/modules/naive_bayes.html#multinomial-naive-bayes).

Independent tests calculate tiny event products and normalize them by hand; seeded reference tests also check fractional counts, matched alpha and supplied priors. They compare posteriors, not a reused implementation helper.

## 25. Author Attribution

Author and maintainer: **MD.Khalid Hasan**, [khalidhasan7343](https://github.com/khalidhasan7343). Part of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas), distributed under the [MIT License](../../../../LICENSE). Follow [CONTRIBUTING.md](../../../../CONTRIBUTING.md). Phase 14 owner approval remains pending; passing tests do not authorize B3 or another category.
