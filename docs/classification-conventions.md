# Phase 14 — Classification contracts

Owner: **MD.Khalid Hasan** · [MIT](../LICENSE) · [Scope](classification-scope.md).
Phase 13 is owner-approved; Phase 14 is awaiting its separate final owner review.

## Shapes, labels and state

Dense single-output classifiers accept numeric 2D `X=(n,p)` and 1D `y=(n,)`.
No implicit X/y reshaping, string-to-number conversion, missing-value imputation
or mixed-label coercion. Feature arrays must be real numeric, excluding bool,
complex and object arrays, finite with magnitude≤10¹². They are copied to float64.
Training n≤2048,p≤128 and 262144 cells; queries m≤10000 under the same cell cap.
Individual stricter limits below take precedence.

Labels form one homogeneous family: signed-int64-compatible integers (including
NumPy integers, excluding bool) or nonempty strings of at most 256 characters.
Float, bool, bytes, None and mixed families are rejected before conversion. At
most 32 classes are sorted numerically/lexicographically, defining `classes_`
and all probability columns. Data already coerced by a caller cannot recover
their previous Python types. Original label values are returned by `predict`.

`fit` returns self after success; failed refits preserve the last valid fitted
state. Training does not mutate caller arrays or global random state. Predict
before successful fit raises ValueError; empty shaped queries return empty
outputs. Accuracy on empty labels is undefined and rejected. `score` is accuracy.
No sample weighting is implemented. Numerical failures raise ValueError;
bounded optimizer failure raises ConvergenceError rather than returning a partial
successful model. Every model's original labels, deterministic outputs and
failure-state contracts are exercised by category-level tests.

## Model domains and ties

| Model | Feature/label scope | Explicit ties or numerical policy |
| --- | --- | --- |
| Logistic | Binary, numeric; n≤2048,p≤128 | Margin≥0 selects second class; centered gradient stopping, bounded Newton/backtracking |
| KNN | Multiclass/single class, numeric | Equal distance: original row order; vote tie: first sorted class; m·k≤262144 |
| Gaussian NB | Multiclass/single class, numeric | First max log score; variance floor smoothing·max(1,max global variance) |
| Multinomial NB | Multiclass/single class, nonnegative counts/weights | First max log score; alpha≥10⁻⁹; zero rows use priors |
| Bernoulli NB | Exact numeric bits or explicit X>threshold | Includes absence; first max log score; alpha≥10⁻⁹ |
| SVM | Binary linear only; n≤256,p≤64 | Margin≥0 selects second class; box/signed-equality and primal/dual gap; no predict_proba |
| CART | Multiclass/single class; p≤32,depth≤16 | Gini ties≤10⁻¹⁴ keep first feature/boundary; zero-gain splits allowed at minimum zero |
| ID3 | Integer-coded categorical; n≤512,p≤32,≤64 categories/column | Multiway information gain; chosen feature removed; unseen category uses node distribution |
| C4.5 style | Explicit categorical indices plus continuous columns; same tree caps | Best raw-gain threshold, optional MDL charge, mean-positive-adjusted-gain filter, ratio ties keep first; no pruning; missing rejected |
| LDA | At least two classes; p≤64 | Prior-weighted population covariance +reg·I; centered linear scores; first max |
| QDA | At least two classes, ≥2 rows/class; p≤64 | Unbiased sample covariance, identity shrinkage, logdet/Cholesky scores; first max |

Trees return empirical node/leaf class distributions; KNN returns uniform vote
fractions. These are meaningful probability estimates, not calibration guarantees.
NB and discriminant scores have shape(m,c), including binary cases. Logistic/SVM
decision functions are signed shape(m,) margins/log odds. The SVM intentionally
offers no calibrated probability API. Tree construction completion is not global
tree optimality or iterative convergence.

Covariance factors require λmin>machine_epsilon·p·max(λmax,smallest_normal_float)
before Cholesky, so singular matrices cannot be accepted merely through rounding.
Positive but insufficient regularization can still fail at extreme scale. LDA
adds absolute diagonal variance; QDA uses `(1−reg_param)S+reg_param I`. LDA's
population denominator and QDA's sample denominator differ intentionally.

## Metrics and evaluation

[metrics.py](../machine-learning/supervised-learning/classification/metrics.py)
provides unweighted accuracy, confusion matrix (rows=true, columns=predicted),
per-class precision/recall/F1, macro averages and true-support-weighted averages.
Explicit classes must be unique and sorted. Zero denominators return zero;
macro includes explicit zero-support classes. Binary positive class defaults to
the second sorted class, with an explicit supported-label override; no binary
summary is forced on multiclass data. Probability log loss requires matching
class order, finite [0,1] entries and rows summing to one; selected probabilities
are clipped below at 10⁻¹⁵ before the mean negative log. Probability matrices
are limited to 262144 cells. There is no sample-weight API.

The fixed-seed experiment uses three small synthetic cohorts appropriate to
numeric, count and mixed-feature models. Continuous scaling is fitted only on
training rows; ID3 bins and all hyperparameters are fixed in source before test
evaluation. Training and held-out metrics remain separate; SVM log loss is absent
with an explicit reason. Timings and one split establish no universal superiority.

## Verification and scope

Analytical objectives, finite differences, independent likelihood products,
brute-force split enumeration and matched scikit-learn references verify the
appropriate algorithms. There is no claimed scikit-learn ID3/C4.5 equivalence.
The C4.5 variant's omitted pruning/fractional unknown routing/release-specific
behavior is explicit. Tests have fixed seeds and bounded sizes/iteration budgets;
there are no external downloads. C++ remains optional for these eleven topics;
DSA retains Python/C++ and C++17/C++20 unchanged. No B3 or other category is authorized.
