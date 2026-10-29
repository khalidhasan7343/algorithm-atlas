# Voting Classifiers — hard and soft aggregation

## 1. Algorithm Name

Voting Classifiers — hard and soft aggregation

## 2. Overview

Combine independent classifier outputs using weighted hard votes or aligned soft probability distributions. All base estimators are created fresh from factories and trained on the complete training cohort. Defaults reuse a bounded tree and canonical Gaussian Naive Bayes.

## 3. Problem Statement

Input X has shape (n,p), y shape (n,). Numeric fitting is bounded to 512 rows and 32 features; CatBoost has its stricter 64-row/8-feature limits. Regression is finite scalar float64. Classifiers preserve sorted homogeneous int64/string labels. Empty prediction matrices are supported; empty fitting data is rejected. See the complete [shared contracts](../../../docs/ensemble-methods-conventions.md) for exact ranges, atomic fit state, seed behavior, factory protocols and metric conventions.

Public model(s): `VotingClassifier`. Fitting constructs an ensemble; inference predicts one scalar or original class label per query row. Supported classification probabilities have one column per fitted sorted class.

## 4. Why Do We Need This Algorithm?

Different classifier assumptions can produce different errors. Voting gives a transparent combination without learning a second model. It is useful when weights are chosen independently of the held-out test set; it does not promise that heterogeneous models are accurate or well calibrated.

## 5. Real-World Applications

A compact numeric classification exercise may combine a geometric tree partition with a Gaussian likelihood classifier. Hard voting studies complementary class decisions; soft voting studies probability-column alignment and confidence averaging. Upstream text/image feature extraction, probability calibration and any weight tuning must be handled separately within training data.

## 6. Core Intuition

Hard voting turns each predicted label into a one-hot vector in the ensemble's sorted class order. Soft voting maps each base probability column using its classes_ labels before adding it. Normalized nonnegative ensemble weights determine the weighted sum. Matching column positions without matching labels would be incorrect.

With normalized a_t>=0 and sum a_t=1, hard v_k=sum a_t*1[h_t=c_k] and soft p_k=sum a_t*p_tk. For valid normalized base probabilities, the convex combination remains nonnegative and sums to one. Hard predict_proba returns vote fractions; its availability does not turn hard votes into calibrated estimates.

## 7. Prerequisites

Required: NumPy arrays, training versus test separation, probability/means, decision-tree partitions and finite-precision arithmetic. Read [ML development](../../../docs/ml-development.md), [Regression metrics](../../../docs/regression-evaluation.md) and [Classification contracts](../../../docs/classification-conventions.md). Algorithm-specific prerequisites include sampling, weighted counts and deterministic class ordering.

## 8. Step-by-Step Working Process

1. Validate at most eight seed-taking factories, voting mode and finite nonnegative weights with positive total.
2. Validate global training labels and fix deterministic sorted class order.
3. Create and fit each independent base on copied full data. Validate its prediction/probability protocol even if its ensemble weight is zero.
4. Hard mode accumulates weighted one-hot predicted labels. Soft mode aligns each probability column by class identity and accumulates weighted probabilities.
5. Normalize input ensemble weights once at fit time; their normalized weighted output sums to one.
6. Return the first sorted class attaining the maximal computed score. No learned meta-classifier is involved.

The stored state follows the prediction formula above. All training is bounded, uses local RNGs and publishes fitted attributes only on successful completion.

## 9. Pseudocode

```text
models <- fresh independently seeded factory instances fitted on full data
weights <- normalized finite nonnegative weights
for model, weight:
    if hard: contribution <- one_hot(model.predict(X), global classes)
    if soft: contribution <- align(model.predict_proba(X), model.classes_, global classes)
    result += weight*contribution
predict <- sorted_classes[argmax(result)]
```

## 10. Dry Run

The default soft-voting example trains a depth-one tree and Gaussian NB on
[0,1,2,3] with labels [cold,cold,warm,warm]; endpoint queries yield
["cold","warm"]. The explicit alignment oracle uses a base with columns [z,a]
and probabilities [3/4,1/4], and another with [a,z] and [3/4,1/4]. Weights [1,3]
produce global [a,z] scores [5/8,3/8]. Equal weights produce the exact tie
[1/2,1/2], selecting a. Binary fractions make that float64 tie exact.

## 11. Time Complexity

For B<=8 bases, base fit costs B_t and query costs Q_t, training costs sum B_t. Aggregation on q queries with K classes costs O(qBK) plus sum Q_t. Hard labels can be mapped in O(qB) expected dictionary time; the implementation constructs explicit class-sized one-hot arrays for auditability. Best/average runtime depends on early stops and data-dependent partitions; no universal average-case speed or wall-clock bound is asserted.

## 12. Space Complexity

Stores all fitted base models and B normalized weights. Aggregation uses O(qK) running output and one O(qK) contribution at a time. Fresh copied training arrays add temporary O(np). Soft class alignment uses O(K) mappings.

## 13. Python Implementation

The working from-scratch source is [python/solution.py](python/solution.py); [python/example.py](python/example.py) is executable. Public APIs are `VotingClassifier`, with fit/predict/score and the task-specific methods above. Core training uses NumPy/local code, never scikit-learn. B3 [support](../support.py) reuses canonical B1/B2 contracts and metrics; [tree.py](../tree.py) is explicit ensemble infrastructure. Factory defaults reuse canonical models rather than copying their solvers. Runtime dependencies come from [requirements-ml.txt](../../../requirements-ml.txt).

## 14. C++ Implementation

Classical ML uses the Python-first policy: optional C++ is **not implemented** for this topic. There are no dummy C++ source/test files. Existing DSA Python/C++ and C++17/C++20 requirements remain mandatory and unchanged.

## 15. Input and Output Examples

From the repository root with the ML test environment installed:

```sh
python machine-learning/ensemble-methods/voting-classifiers/python/example.py
```

The dataset, hyperparameters, seed and executed output are explained in the dry run. The same reusable API can be called as:

```python
# From this topic's python directory
from solution import VotingClassifier
model = VotingClassifier(**{'voting': 'soft', 'random_state': 0})
model.fit([[0], [1], [2], [3]], ['cold', 'cold', 'warm', 'warm'])
predictions = model.predict([[0], [3]])
```

The JSON CLI accepts X, y, predict and optional parameters. It prints a predictions object; invalid input exits 2 with stderr and no prediction JSON. Factory callables are Python API configuration, not JSON-serializable CLI parameters.

## 16. Edge Cases

Equal computed scores choose sorted classes. A reordered base class array is explicitly aligned; an unknown predicted label or probability class fails. Missing supported global classes receive zero columns. Soft outputs with negative, nonfinite, unnormalized probabilities or wrong shapes fail. All-zero weights and empty/oversized factory lists fail.

Do not mutate public parameters during inference. Caller arrays and global RNG state are preserved. Unsupported sample weights raise TypeError except where explicitly supported. Nonfinite/ambiguous shapes and predict-before-fit raise clear errors; extreme unresolved float64 operations fail rather than returning a fabricated success.

## 17. Advantages

Small, transparent combination rule; supports heterogeneous existing canonical classifiers and exposes weights and fitted bases. Class alignment is explicit and independently tested.

## 18. Disadvantages and Limitations

Weights are supplied, not learned. Correlated mistakes can reinforce each other. Soft voting assumes meaningful comparable base probabilities; normalization alone does not establish calibration. No automatic tuning, prefit-model ingestion, multioutput classification or factory cloning is implemented.

The [shared contracts](../../../docs/ensemble-methods-conventions.md) state numerical/resource limits and exact unsupported features. Scores and probability outputs are educational model quantities, not calibrated guarantees. A larger ensemble need not improve held-out error.

## 19. When to Use It

Use when a few independently useful classifiers have complementary errors and a fixed transparent voting rule is desirable.

## 20. When Not to Use It

Avoid soft voting when probabilities are invalid or incomparable, and avoid evaluating weight choices on the final test set. Use stacking only when enough training data exists for separate out-of-fold meta-learning.

## 21. Comparison With Related Algorithms

| Method | Combination learned? | Base training cohorts |
| --- | --- | --- |
| Voting | No; fixed supplied weights | Full data for each base |
| Stacking | Yes; separate meta-model | OOF folds, then full-data refits |
| Bagging | No; equal votes/mean here | Bootstrap samples |

## 22. Interview Questions

1. Give an example where probability-column position is misleading.
2. Prove a convex combination of valid distributions is normalized.
3. Why can a near decimal tie differ from an exact computed tie?
4. What does hard-mode predict_proba mean here?

## 23. Practice Problems

1. Reproduce the 5/8,3/8 aligned soft result by hand.
2. Construct two exact tied hard voters and inspect deterministic order.
3. Compare held-out hard and soft metrics on one fixed split without retuning weights on test data.

For validation run:

```sh
python -m pytest machine-learning/ensemble-methods/voting-classifiers -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
```

The independent oracles use hand calculations, exhaustive candidates or separately fitted references. Marker selections overlap; do not sum them as disjoint counts. Seeds, small datasets and explicit tolerances make failures reproducible. Full DSA regression also runs with `--require-cpp`.

## 24. References

[scikit-learn VotingClassifier guide](https://scikit-learn.org/1.8/modules/ensemble.html#voting-classifier); [official VotingClassifier API](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.VotingClassifier.html).

These primary references identify the mathematical method; the exact implemented subset and limits are stated here. External implementations may differ in split ties, random stream consumption, optimization or supported features; reference tests align compatible settings rather than asserting universal equivalence.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE) · [Contribution guidance](../../../CONTRIBUTING.md). This lesson belongs to authorized Phase 15 B3; its new review approval remains pending.
