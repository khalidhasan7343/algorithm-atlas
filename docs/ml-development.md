# Machine Learning development standard

Maintainer: **MD.Khalid Hasan**. [MIT License](../LICENSE).
The owner explicitly approved the latest B1 Regression completion audit and all
prior work, and authorized **Phase 15 — B3 Ensemble Methods only**. Implement the
eight catalog canonicals under [the scope lock](ensemble-methods-scope.md),
with actual stage gates in [the checkpoints](ensemble-methods-checkpoints.md).
Preserve approved B1/B2/DSA algorithms, tests, lessons and historical evidence/packages.
Inventory remains 35 categories / 256 memberships / 235 canonicals.

Python/NumPy, numerical/oracle/reference tests and exact 25-section lessons are
mandatory for ML; C++ is optional. DSA retains Python/C++ and both C++17/C++20.
The **Phase 15 review approval remains pending**. Stop after its completion report
and verified ZIP/checksum/JSON. No Phase 16, other category, commit, push, tag,
release or publication. Never set Git identity from public email.

## Track and language policy

| Track | Required implementation/tests | C++ policy |
| --- | --- | --- |
| DSA | Python, C++, Python tests, C++ tests | Both C++17 and C++20 remain mandatory |
| Classical ML | Python, numerical tests, mathematical explanation, reproducible examples | Optional; source and executable C++ test must be provided together |
| Future Deep Learning / AI | Not authorized here | Retains previous structural rules until a separate language/framework policy is authorized |

[The central policy](../scripts/track_policy.py) identifies tracks from canonical
paths checked against their catalog owners. No algorithm IDs are special-cased.
The catalog schema and status vocabulary are unchanged. A Python-only ML record
leaves `cpp_status: planned`, explicitly meaning optional and not implemented;
this does not prevent Python-based completion. Optional C++ source/test files
must form a nonempty pair, have truthful statuses, use the shared compiler
fixtures, and execute under C++17/C++20 when supplied. Partial optional C++ is
invalid. All completed algorithms require Python source and Python tests.

`python -m pytest --require-cpp` still discovers all four roots and enforces
compiler availability for DSA tests. Python-only ML tests never request C++
fixtures. Neither DSA requirements nor its existing tests are removed.

## Runtime and reference dependencies

DSA-only setup remains `python -m pip install -r requirements-dev.txt` and
`python -m pytest tests dsa --require-cpp`. Install `requirements-ml.txt` for ML
runtime, or `requirements-ml-test.txt` for the full suite with reference tests.
NumPy supplies array/linear-algebra primitives. scikit-learn is a development
reference only; core solutions never import it. No deep-learning framework,
dataset download, pickle loader or model checkpoint is introduced.

Full local/CI setup:

```sh
python -m pip install -r requirements-ml-test.txt
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
python -m pytest machine-learning/supervised-learning/regression -q
```

Tests require their dependencies and fail clearly when absent. They do not
silently skip required numerical/reference verification. CI installs the ML
test requirements alongside unchanged DSA dependencies.

## Algorithms and numerical contracts

Every topic exposes its genuine mathematical logic. Reusing a canonical topic
(Polynomial Regression uses Linear Regression) is explicit; NumPy SVD/least
squares is a numerical primitive, not a hidden estimator. Define the exact loss
normalization, intercept treatment, regularization, optimization, stopping
conditions and failure behavior. Deterministic bounded solvers expose iteration
and convergence diagnostics. Exhausting an iterative solver raises an explicit
convergence error; a partial fit is not presented as success.

Dense single-output float64 regression is the initial scope. Inputs have shape
`X=(n_samples,n_features)`, `y=(n_samples,)`; one-dimensional X or column-vector
y is rejected rather than guessed. Validate real numeric dtype, finite values,
resource/numeric limits and matching dimensions. Models copy training state and
do not mutate user arrays or global random state. Predict-before-fit is an error.
Document what a failed refit does to a prior fitted model. Fit preprocessing only
on training data; retain it for inference and keep held-out data separate.

Use stable least squares instead of normal-equation inversion, unpenalized
intercepts, explicit zero-column handling, checked nonfinite computations,
appropriate condition/rank diagnostics, and bounded matrix/feature expansion.
No solver can promise convergence on every ill-conditioned dataset. Hyperparameter
choices, scaling requirements and numerical tolerances must be stated.

## Documentation, tests and experiments

Keep the exact [25-section template](development.md#required-algorithm-readme-sections).
Use section 14, **C++ Implementation**, to state that C++ is optional and absent,
with no dummy files. Cover objectives, derivations, assumptions, training and
inference, shapes/state, hyperparameters, numerical stability, stopping criteria,
complexity, a worked numerical dry run, evaluation, limitations and references.

Tests include analytical solutions or independent optimization, smooth-gradient
finite differences (away from L1/epsilon kinks), KKT/duality checks where relevant,
known splits for trees, deterministic synthetic data, invalid shapes, constant and
singular features, held-out predictions, bounded non-convergence and failed-refit
state. scikit-learn comparisons align objective scaling and intercepts, compare
predictions/objectives when nonunique coefficients differ, and do not assume the
same optimizer or tie rules. Seeds, sample counts and tolerances are recorded.

Examples and modest benchmarks are local and reproducible. Report training and
test metrics separately; no uncontrolled performance-superiority claims or CI
wall-clock thresholds. Test results, audit results and owner approval are distinct.
Final review uses the existing report/package folders and stops for explicit owner
approval before any next ML category.

## Classification extension — Phase 14

The [classification contracts](classification-conventions.md) define strict label
families, binary versus multiclass APIs, class/probability ordering, numeric and
categorical domains, convergence/errors, metrics and held-out evaluation. They
extend this Python-first foundation without changing B1 or DSA implementations.

## Ensemble extension — Phase 15

The [B3 contracts](ensemble-methods-conventions.md) specify factory independence,
bootstrap and split RNGs, hard versus soft probability semantics, ordered prefix
boosting, target-statistic leakage avoidance and out-of-fold meta-training.
The exact variants and their deliberately bounded resource limits are part of the
lessons. XGBoost/CatBoost production-library parity is not claimed.
