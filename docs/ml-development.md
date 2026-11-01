# Machine Learning development standard

Maintainer: **MD.Khalid Hasan**. [MIT License](../LICENSE).
The owner **MD.Khalid Hasan** explicitly approved the verified Phase25 B13 handoff on **2026-11-01 Asia/Dhaka** and authorized **Phase26 — Machine Learning B1–B13 Final Comprehensive Audit**. This is audit/stabilization only:seven workstreams;no new category or canonical. See [scope](../docs/ml-final-audit-scope.md) and [checkpoints](../docs/ml-final-audit-checkpoints.md). Preserve inventory35 categories/256 memberships/235 canonicals,all prior approvals,historical reports/evidence/packages,DSA source and existing staged work. Preserve DPO identity,path,four blocked statuses,research and owner-approved remain-blocked decision.

Independently inspect every implemented ML canonical,math,oracles/tests,exact25-section lessons,numerics,resources,security,dependencies,CI and shared ownership. Make only minimal confirmed in-scope fixes;record reproductions and rerun affected checks. Request owner input before altering canonical identity,approved mathematical scope,public API contracts or blocker decisions. ML Python/NumPy mandatory,C++ optional;DSA Python/C++17/C++20 mandatory. No downloads or pretrained frameworks. Deliver tracked36-part report and verified ZIP/checksum/JSON,then STOP. **Phase26 audit and final B Track owner approval pending.** No C1,nextphase,commit,push,tag,release or publication. Never set Git identity from public email.


## Track and language policy

| Track | Required implementation/tests | C++ policy |
| --- | --- | --- |
| DSA | Python, C++, Python tests, C++ tests | Both C++17 and C++20 remain mandatory |
| Classical ML | Python, numerical tests, mathematical explanation, reproducible examples | Optional; source and executable C++ test must be provided together |
| B7 Neural Networks and Deep Learning | Python/NumPy, explicit gradients, numerical tests | Optional C++ |
| B8 Reinforcement Learning | Python/NumPy, Bellman/gradient oracles, real A3C concurrency | Optional C++ |
| Future AI | Not authorized here | Retains previous structural rules |

[The central policy](../scripts/track_policy.py) identifies tracks from canonical
paths checked against their catalog owners. Phase19 extends the same Python-first NumPy policy to all B7 canonical paths; existing catalog ownership/path and DSA/AI checks remain mandatory.
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
and convergence diagnostics. Exhausting a convergence-required solver raises an explicit convergence error.
Finite-budget embedding/neural experiments expose converged_, optimization_status_
and objective history without claiming convergence; see the B5 contracts.

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

## Clustering extension — Phase 16

The [B4 contracts](clustering-conventions.md) define fit(X), label/metric semantics,
transductive versus meaningful new-row methods, bounded convergence and numerical
limits. Phase 16 [scope](clustering-scope.md) is now owner-approved; historical handoff evidence remains unchanged.
K-Means is reused canonically by GMM initialization and spectral partitioning.
Hierarchies/DBSCAN/HDBSCAN/spectral do not expose an invented centroid predictor.
Clustering metrics use explicit noise coverage and label-permutation agreement;
likelihood and held-out assignment are reported only where meaningful.

## Dimensionality reduction extension — Phase 17

See [B5 contracts](dimensionality-reduction-conventions.md) for decomposition, supervised projection, independence, graph/probability embedding and canonical NumPy reconstruction semantics. B4 historical handoff approval fields remain generation-time evidence; current Phase 16 approval is recorded in the catalog.

## Association Rule Learning extension — Phase18

[Transactions and exact thresholds](association-rule-learning-conventions.md) replace
numeric feature matrices for B6. Standard-library combinatorial core logic is
appropriate; NumPy is used only where useful in independent references. Frequent
itemsets and rule support/confidence/lift have distinct contracts. Each miner has
its own mechanism; shared rules do not add a catalog canonical. Earlier B5 contracts
and all language policies are preserved.

## Reinforcement Learning extension — Phase20

[RL contracts](reinforcement-learning-conventions.md) specify environment termination/
truncation, sampled versus fixed targets, exploration, replay, actor/critic gradients,
worker synchronization and bounded deterministic planning. Nine defined canonicals
are completed; exact DPO identity remains intentionally blocked under the
owner-approved Outcome3 decision. Phase20 implementation review is now owner-approved;
its historical handoff artifacts retain their original generation-time status.
The narrow Phase20 blocker-review checkpoint does not make DPO complete or weaken
other implementation/language requirements. B1–B7 and DSA bytes remain preserved.

## Time Series extension — Phase23

[Time-series contracts](time-series-conventions.md) define regular chronological input,conditional innovation estimation,training-only differencing/scaling,recursive forecast indexing,additive Prophet subset priors and categorical HMM log-space inference/ML EM. Forecasting and latent sequence inference retain appropriate separate APIs. B10 is owner-approved and reused without source changes.

## Anomaly Detection extension — Phase24

[Anomaly contracts](anomaly-detection-conventions.md) define score orientation,training quantile/tie rules,random isolation,constrained one-class KKT certificates and exact tie-inclusive training LOF. Existing B4/B2 validation/distance and B1 kernel helpers are reused unchanged. No duplicate AI work or novelty LOF is claimed.

## Natural Language Processing extension — Phase25

[NLP contracts](natural-language-processing-conventions.md) define Unicode/tokenization/vocabulary boundaries, exact statistical and embedding objectives, frozen-backbone/head-only educational BERT/GPT, supervised POS, canonical CRF-backed BIO NER and CNF CYK. No pretrained equivalence or final track-audit approval is claimed.
