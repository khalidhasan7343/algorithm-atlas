# Phase 14 — Classification review report

Owner/maintainer: **MD.Khalid Hasan** · [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas) · [MIT](../../../LICENSE).
Prepared 2026-10-28 (Asia/Dhaka). **Phase 14 owner approval: pending.**

## 1. Phase identity and prerequisite approval

Phase 14 — Supervised Learning — Classification follows completed B1 Regression.
The owner explicitly supplied **“OWNER-APPROVAL CHECKPOINT IS SATISFIED.”** with
the Phase 14 request, satisfying Phase 13 approval. This is recorded in catalog
phase_records.13 and appended to the prior checkpoint/scope without rewriting
their historical execution evidence. Phase 11/12 and DSA final-audit approval
records remain independent and unchanged. No Phase 15/B3 or other category,
Deep Learning, AI, commit, push or release is authorized.

## 2. Category identity

**B2 — Supervised Learning — Classification**, canonical directory
`machine-learning/supervised-learning/classification/`, slug `classification`.
The current catalog confirmed all eleven requested names/IDs/paths before changes.
Every B2 record was planned; none had existing source/test implementations.

## 3. Scope and baseline

[Scope lock](../../classification-scope.md), [contracts](../../classification-conventions.md)
and [checkpoints](../../classification-checkpoints.md) define four sequential batches.
Started from clean `main` at `f2cc7c295e0f3fcf83dcb67ab3e6cf8d9c2e1f7e`.
The [baseline](../../classification-evidence/baseline.json) captures tracked-file
hashes, original catalog/development metadata, Python/dependency/compiler versions
and empty pre-existing changes. Baseline catalog/link/generated checks passed;
530 infrastructure+B1 tests passed in 4.45s. Inventory remains **35 categories,
256 memberships, 235 canonicals**, including 97 DSA and seven B1 implementations.
The new eleven bring track-required completed canonicals to 115, leaving 120,
including the unchanged blocked Dynamic Policy Optimization topic.

## 4. All eleven canonical algorithms

| Canonical ID | Implemented scope | Individual tests |
| --- | --- | ---: |
| logistic-regression | Binary mean cross-entropy/L2; stable Newton/backtracking | 22 |
| k-nearest-neighbors | Multiclass Euclidean full search, stable neighbors/votes | 14 |
| gaussian-naive-bayes | Class means/population variances, explicit smoothing/log densities | 17 |
| multinomial-naive-bayes | Nonnegative event counts/weights, additive smoothing | 17 |
| bernoulli-naive-bayes | Explicit bit/threshold contract, presence and absence | 14 |
| support-vector-machines | Binary linear hinge-loss C-SVM dual, bounded ADMM/gap | 20 |
| cart-decision-trees | Multiclass binary Gini splits and class distributions | 11 |
| id3-decision-trees | Multiway integer-coded categories, entropy/information gain | 11 |
| c4-5-decision-trees | Mixed gain ratio, optional MDL correction, explicit omissions | 10 |
| linear-discriminant-analysis | Prior-weighted full shared covariance, linear scores | 14 |
| quadratic-discriminant-analysis | Class sample covariances, shrinkage/quadratic scores | 16 |

There are 166 individual tests plus **232 shared contract/metric/cross-model checks**.
No B3/other-category algorithm implementation is introduced.

## 5. Python implementations and common API

All eleven implement their essential mathematics using NumPy primitives, never
calling a scikit-learn/SciPy estimator. Shared support handles checked arrays,
strict label encoding, finite arithmetic, probability normalization, imports/CLI
and generic factor-resolution checks. Core optimization, likelihoods and split
selection remain in the canonical solutions. C4.5 explicitly reuses ID3's scalar
entropy helper, not its tree builder.

Fit/predict/accuracy score are consistent. Probabilistic models expose
predict_proba; Logistic and SVM expose signed decision margins, while NB/LDA/QDA
expose class log/discriminant score matrices. Original labels are returned, class
ordering is deterministic, training arrays/global RNG are unchanged, and failed
refits preserve successful state. Label families are homogeneous int64-compatible
integers or nonempty strings; bool/float/mixed coercion is rejected.

## 6. Optional C++ and preserved DSA policy

C++ is optional and **absent for all eleven B2 topics**; cpp_status remains planned
as an honest optional deliverable. No dummy source/test is created. The Phase 13
track policy, central validator, root conftest, dependency files, pytest markers
and CI configuration are unchanged. DSA still requires Python/C++, both test
files and C++17/C++20. `pytest --require-cpp` continues discovering all tracks.

## 7. Mathematical correctness evidence

Logistic tests derive a constant-feature intercept from class odds and finite-
difference the regularized loss. KNN compares every neighbor against a scalar
distance/row-order oracle. NB tests independently multiply Gaussian/count/bit
likelihoods and verify priors and posterior normalization, including absent-bit
evidence that reverses a presence-only decision. SVM verifies the analytic
w=1,b=0,P=D=0.5 solution, support conditions, feasibility and gap.

CART enumerates weighted Gini splits; ID3 independently calculates Shannon gain
and the encoded Play Tennis root; C4.5 independently enumerates mixed-feature
gain/ratio/correction/filter candidates. LDA verifies linear Gaussian discriminants
and pooled covariance; QDA checks an equal-mean/unequal-variance quadratic boundary
and independent full Gaussian scores with slogdet/linear solves.

## 8. Numerical validation

The final B2 selection passed **398 tests in 1.06s**, with **54 numerical tests
passed, 344 deselected, in 0.61s**. Deselection is the intentional marker filter,
not a skip. Tests cover stable sigmoid/log-loss, extreme logits, large common
feature offsets, zero variances/counts, tiny classes, label domains, shapes,
neighbor/vote ties, repeated/constant features, covariance singularity and
near-collinearity, resource caps, finite posteriors and failed-refit state.
See [final results](../../classification-evidence/final-results.json) and
[numerical transcript](../../classification-evidence/numerical-attempt1.txt).

## 9. Independent reference comparisons

**45 reference tests passed, 353 deselected, in 0.60s**, using installed
scikit-learn 1.8.0. Logistic maps C=1/(n·alpha), including an explicitly asserted
unregularized-library warning. KNN comparisons avoid tied boundary distances;
CART reference data control split ambiguity. NB aligns event/smoothing/prior
contracts, including Gaussian epsilon scaling. SVM aligns linear C, kernel and
tolerance. LDA aligns prior-weighted population covariance; QDA aligns per-class
sample covariance and reg_param with enough rows for full feature rank.

No scikit-learn ID3/C4.5 equivalent is claimed: independent exhaustive mathematical
oracles cover them. Comparisons do not demand identical optimization iterations,
nonunique coefficients, arbitrary ties or raw scores differing by class-independent
terms. [Reference-source evidence](../../classification-evidence/reference-sources.json)
distinguishes primary retrievals from unverified retrieval endpoints.

## 10. Seeded randomized checks

All randomness uses local generators with explicit source seeds and bounded sizes.
Examples: 14011/14012 Logistic; 14021/14022 KNN; 14211–14231 NB; 14311/14312 SVM;
14321–14341 trees; 14411–14423 discriminants; 14911 metrics. KNN's scalar oracle
checks 24 seeded datasets across k=1,5,n. Tree oracles enumerate **70 CART,
60 ID3 and 100 C4.5 mixed-feature datasets**. Reference predictions use held-out
query rows and explicit numeric tolerances. Shared checks repeat every model
with both integer and string labels and verify unchanged global RNG state.

## 11. Convergence and failure behavior

Logistic records objective history, centered gradient infinity norm and iterations;
bounded Armijo search enforces accepted-step descent. SVM records box/signed-
equality feasibility, residuals, primal/dual objectives, gap and iterations.
Budget exhaustion raises ConvergenceError without replacing a previous fit.
Neither optimizer promises finite-budget convergence on every allowed scale.
NB/discriminants use closed moment/factor calculations, not iterative convergence.
Trees terminate through depth/sample/features; converged_ means construction
completed, not global tree optimality. Covariance resolution is checked explicitly
before Cholesky instead of silently accepting a rounded singular factor.

## 12. Executed examples and CLIs

All **11 authored examples**, **11 equivalent JSON prediction calls** and
**11 invalid-shape CLI calls** passed. Expected labels are independently determined
from worked examples. Invalid CLIs exit 2 with stderr and no prediction JSON.
[Example evidence](../../classification-evidence/examples-attempt4.json) records
observed and expected labels. Exact standalone/API commands appear in every
lesson; no README output is inferred from a placeholder.

## 13. Metrics and evaluation experiments

The [metrics module](../../../machine-learning/supervised-learning/classification/metrics.py)
defines accuracy, true-row/predicted-column confusion matrices, per-class
precision/recall/F1, macro and true-support-weighted averages. Zero division is
zero; explicit zero-support classes remain in macro averages. Binary positive
defaults to the second sorted class and can be overridden. Multiclass data are
not forced into a binary summary. Log loss checks probability/class order and
clips selected probabilities below at 10⁻¹⁵. No sample weights are supported.
Independent sklearn metric comparisons and hand calculations passed.

The [experiment](../../classification-evidence/benchmark.json), seed 14028, uses
three model-appropriate small cohorts. Continuous scaling is fitted only to
72 training rows, evaluated on 36 held-out rows. Count models use 60/30 raw-count
rows; mixed trees use 72/36 rows with explicit fixed ID3 bins/categorical indices.
All hyperparameters/bins are fixed before test evaluation. Training/test metrics,
confusion matrices, timing and optimization/tree diagnostics are separate.

| Model | Cohort | Held-out accuracy | Held-out log loss |
| --- | --- | ---: | ---: |
| Logistic | continuous | 0.888889 | 0.373791 |
| KNN | continuous | 0.888889 | 0.252204 |
| Gaussian NB | continuous | 0.861111 | 0.333273 |
| Linear SVM | continuous | 0.861111 | unavailable: no probability API |
| CART | continuous | 0.722222 | 7.807147 |
| LDA | continuous | 0.888889 | 0.266547 |
| QDA | continuous | 0.861111 | 0.323496 |
| Multinomial NB | counts | 1.000000 | 0.028229 |
| Bernoulli NB | thresholded counts | 0.900000 | 0.192732 |
| ID3 | categorical/fixed bins | 1.000000 | 0.015885 |
| C4.5 style | mixed | 1.000000 | 0.000000 |

CART's large log loss reflects confident zero leaf frequencies on some wrong
held-out labels and the documented clipping rule, not a hidden failed computation.
These different cohorts/representations and one split establish no universal
model superiority or timing guarantee.

## 14. Documentation validation

All eleven lessons have exactly the established 25 headings, in order, with
genuine derivations, contracts, pseudocode, worked examples, complexity, limitations,
evaluation and references. C++ sections honestly state optional/absent. Generated
documentation manages **162** planning/category/index pages, preserving authored
lessons. Catalog validation checks relative Markdown links repository-wide.
Current guides now record Phase 13 approval and Phase 14-only authorization;
historical reports/archive metadata retain their handoff-time statements.

## 15. Catalog and preservation

Catalog validation passed; schema, category/member order, IDs and paths are
unchanged. Only B2 algorithm statuses/notes and authorized development/approval
metadata changed. Every out-of-scope algorithm record is identical, including
all B1 records and blocked DPO. The [preservation check](../../classification-evidence/preservation-results.json)
verified **1,383 protected files**, including all DSA source/lessons/tests,
B1 canonical/support/tests and historical reports/evidence/packages. Original
B1 scope/checkpoint bytes remain an exact prefix followed by explicit new approval.
Only current category navigation is regenerated; no prior algorithm is rewritten.

## 16. B1 Regression checks

All **214 B1 tests passed in 0.66s** in the final targeted run, following 530
baseline infrastructure+B1 checks. All seven B1 canonical records, source,
tests, support and authored lessons remain byte-identical. Phase 13 approval
updates the live checkpoint/catalog, not frozen numerical reports or ZIP metadata.

## 17. DSA regression checks

The new full repository run passed **2,615 tests in 438.84s** with zero failures,
errors or skips: **1,687 DSA checks** (1,149 Python, 269 C++17, 269 C++20),
214 B1, 398 B2 and 316 infrastructure checks. All required tests actually executed;
no historical pass is substituted. [JUnit-derived matrix](../../classification-evidence/test-matrix.json)
and [full transcript](../../classification-evidence/full-suite-attempt1.txt)
retain the observed results.

## 18. C++17 and C++20

Both standards remain the default through unchanged root parametrization and
`--require-cpp`. Baseline/batch infrastructure compiler checks passed on both.
The full-suite JUnit matrix records **269 DSA C++17 and 269 DSA C++20 passes**,
plus two infrastructure toolchain checks under each standard. No B2 dummy C++ files exist and no DSA C++ check is disabled.

## 19. CI-equivalent checks

Local Python 3.14.2/macOS arm64 uses Apple Clang 21 through g++. Catalog,
generated docs, all targeted B2/reference/numerical/B1 and infrastructure checks
passed. The required full suite passed 2,615 tests; actual ZIP extraction results are
recorded post-creation in the external package sidecar. The unchanged CI matrix is Python 3.11–3.14 with
CXX=g++; **hosted GitHub Actions was not triggered or verified**, and local
results do not establish hosted Linux or other-Python outcomes.

## 20. Dependencies

No installation or dependency upgrade was needed. Existing runtime NumPy 2.5.4
and test references scikit-learn 1.8.0/SciPy 1.18.1 were reused, with pytest 9.1.1
and PyYAML 6.0.3. Requirements files and CI remain unchanged. Core code imports
NumPy and standard-library/local helpers only; no deep-learning framework,
dataset download, pickle loader, secret, checkpoint or network training call.
[Environment evidence](../../classification-evidence/environment.json) records
versions. DSA-only development remains possible with requirements-dev.txt.

## 21. Files created

Eleven canonical `python/solution.py`, `python/example.py`, `tests/test_python.py`
sets; category support, conftest, metrics, shared tests and held-out experiment;
scope/contracts/checkpoints and evidence; this report; classification validation,
scope/example verification and package scripts; category package README/ZIP/
checksum/metadata. [Changed-file inventory](../../classification-evidence/changed-files.json)
lists exact source/evidence paths, separate from generated review deliverables.

## 22. Files modified

Catalog B2 and development/approval records; current AGENTS/README/CONTRIBUTING,
development/getting-started/glossary/roadmap/ML-standard guidance; generated
index/progress/B1/B2 navigation; eleven B2 planning READMEs replaced by lessons;
generator's active ML label/category notes; review/package indexes. B1 scope and
checkpoint receive only appended explicit approval. No DSA/B1 canonical source,
test or lesson, historical report/archive/evidence, language policy, validator,
root test fixture, dependency file or CI configuration changed.

## 23. Known limitations and unsupported domains

Dense finite numeric input with declared magnitude/cell/sample/feature limits;
no sparse arrays, missing values or sample weights. Labels are homogeneous
int64-compatible integers or nonempty strings, not arbitrary Python objects.
Logistic/SVM are binary; SVM is linear, small-n and nonprobabilistic. KNN uses
full sorting and explicit original-row boundary ties. NB assumptions/smoothing
depend on representation/units. ID3 uses integer-coded categories only. C4.5 is
the documented educational gain-ratio/MDL/filter variant, without pruning,
fractional missing routing, categorical subset grouping or full historical
compatibility. Trees are greedy; leaf/vote probabilities lack calibration guarantees.
LDA has no transform; QDA requires two rows/class; unresolved covariance fails
even with insufficient positive regularization. Bounded solvers may not converge
on poorly scaled inputs. There is no new B2 scope blocker; DPO's existing blocker
remains outside this category. Hosted CI/other platforms remain unexecuted.

## 24. Defects, failed attempts and fixes

Batch 1 initially had **1 failed / 35 passed**: its large-offset KNN test used
10¹²+2, outside the documented bound. The test moved within the bound; no domain
guard was weakened. Two expected unregularized sklearn warnings are asserted
explicitly; the runner bounds reference worker discovery with LOKY_MAX_CPU_COUNT.
The full first failure is retained in batch1-initial.txt.

Batch 4 initially had **1 failed / 29 passed**: a mathematically singular QDA
matrix produced a tiny positive rounded Cholesky diagonal and was incorrectly
accepted. Both discriminants now explicitly check eigenvalue resolution before
factorization; exact/near-singular errors and regularized alternatives pass.
The failed transcript is preserved. Predict-before-fit and unsigned binary target
gradient handling were corrected during Batch 1 development; shared tests cover
the public prediction contract. Nine new compressed solutions were reformatted
with identical parsed ASTs; no approved implementation was changed.

## 25. Reproduction and package verification

With the existing .venv activated, from the repository root:

```sh
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
python -m pytest machine-learning/supervised-learning/regression -q
python -m pytest machine-learning/supervised-learning/classification -q
python -m pytest machine-learning/supervised-learning/classification -m numerical -q
python -m pytest machine-learning/supervised-learning/classification -m reference -q
python scripts/verify_classification_scope.py --check-only
python scripts/verify_classification_examples.py --check-only
python machine-learning/supervised-learning/classification/experiments/benchmark.py
```

Install requirements-ml-test.txt in a fresh environment first; a C++17/C++20
compiler is required. Source exports omit historical archives: use --source-only
with the scope verifier. The stage runner preserves numbered attempts. The
packager refuses existing outputs, checks safe unique paths/CRC/required content/
source bytes, creates SHA-256 and extracts the actual ZIP for catalog/generated/
scope/example/full-suite checks using externally installed dependencies.

Deliverables under `artifacts/review-packages/classification/`:
`algorithm-atlas-classification-review.zip`,
`algorithm-atlas-classification-review.zip.sha256`, and
`algorithm-atlas-classification-review.json`.
Run shasum from that folder. The external JSON records post-ZIP extraction results
and file hashes without self-referential archive hashing. Historical ZIPs/sidecars,
.git, environments, caches, secrets, binaries, data/checkpoints and nested ZIPs
are excluded. Original historical artifacts remain unchanged locally. Report
tracking/unignored status is checked in the final working-tree handoff.

## 26. Owner approval checkpoint

**Phase 14 owner approval: pending.** Stop after all eleven implementations and
the verified report/ZIP/checksum/JSON are delivered. No B3 Ensemble Methods,
other ML category, Deep Learning, AI, commit, push, release or publication.
This agent has not created a commit or changed Git identity.
