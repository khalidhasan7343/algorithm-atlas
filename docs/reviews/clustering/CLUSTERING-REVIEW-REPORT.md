# Phase 16 — B4 Unsupervised Learning — Clustering review

Owner/maintainer: **MD.Khalid Hasan** · [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas) · [MIT](../../../LICENSE).
Prepared for owner review on **2026-10-30 (Asia/Dhaka, client date)**.
Actual execution evidence retains its recorded timestamps. **New review approval: pending.**

## 1. Phase identity and prerequisite approval

Phase 16 follows completed Phase 15 Ensemble Methods. The owner's explicit
“I approved previous work and now follow this properly” immediately followed the
verified Phase 15 handoff. [Approval verification](../../clustering-evidence/approval-verification.json)
checks the actual latest B1/B2/B3 package hashes and successful extracted checks.
Catalog phase_records.15 now records owner approval and the exact accepted package
SHA; Phase 16 is separately pending. No prior report/package was rewritten to
change its historical generation-time approval status. No Phase 17/other category,
commit, push, tag, release or publication is authorized.

## 2. Category identity and discovery

The authoritative category immediately after B3 is **B4 — Unsupervised Learning —
Clustering**, slug clustering, at machine-learning/unsupervised-learning/clustering.
There is no phase-number discrepancy: the active next development milestone is 16;
roadmap learning levels are not development-phase numbers.

Started on clean main at HEAD `4869db2a868151f08c560603dc6ec3f7aa91c3a9`; the owner
advanced the repository after the previous handoff. [Baseline](../../clustering-evidence/baseline.json)
contains 2,077 pre-existing file hashes, Git/index state, dependency/compiler versions
and original catalog. No destructive Git operation, identity change, installation
or removal of owner work. Read AGENTS/catalog/current guides, pytest/CI/ignore
configuration, old ML code/reviews and validation/generation/package conventions.
No required discovery document was missing.

## 3. Exact canonical inventory

All canonical paths below are relative to machine-learning/unsupervised-learning/clustering.
Every entry owns its B4 implementation; there are **no cross-category memberships**.

| Canonical ID / path suffix | Algorithm | Implemented essential mechanism |
| --- | --- | --- |
| k-means | K-Means | Lloyd fixed-point iterations, D²/random/explicit initialization and empty-cluster repairs |
| agglomerative-hierarchical-clustering | Agglomerative Hierarchical Clustering | Euclidean single/complete/average/Ward merges and full hierarchy/cut |
| divisive-hierarchical-clustering | Divisive Hierarchical Clustering | DIANA largest-diameter splinter divisions, not bisecting K-Means |
| dbscan | DBSCAN | Self-inclusive core support, core connectivity, first-reached borders and noise |
| hdbscan | HDBSCAN | Mutual reachability, exact dense MST, condensation, EOM and membership strengths |
| mean-shift | Mean Shift | Every-row flat-kernel shifts, supported-mode merging and optional query noise |
| gaussian-mixture-models | Gaussian Mixture Models | Full-covariance regularized EM with log responsibilities/Cholesky density |
| spectral-clustering | Spectral Clustering | Normalized graph eigenvectors, row normalization and canonical K-Means |

[Scope lock](../../clustering-scope.md) fixes the actual IDs, paths and four batches.
No algorithm from B5 or another category was introduced.

## 4. Algorithm count and inventory preservation

**Eight canonicals; eight implementations completed.** All eight started as
planning-only records. Category ordering, syllabus labels, related-topic links,
canonical IDs/paths and optional-C++ statuses are preserved. Inventory remains
**35 categories / 256 memberships / 235 canonicals**. Track-required completed
canonicals are now 131; 104 remain, including the unchanged blocked DPO topic.

## 5. Implementation status and internal gates

Each actual folder has a working Python solution, example and meaningful tests,
plus a full exact 25-section lesson. Optional C++ is absent and cpp_status remains
planned, honestly meaning optional/not implemented. No placeholder C++ or external
clustering-estimator wrapper. Four sequential gates passed before continuing:

| Stage | Algorithms | Initial passing stage tests |
| --- | --- | ---: |
| 1 | K-Means / Agglomerative | 24 |
| 2 | DIANA / DBSCAN | 21 |
| 3 | HDBSCAN / Mean Shift | 24 |
| 4 | GMM / Spectral | 29 |

Each stage also executed its examples and full lessons before status updates;
catalog/generated and 316 infrastructure checks passed between stages. Additional
cross-model/metric/boundary tests are included in the final combined 206 total;
stage counts are not substituted for or added to that combined total.

## 6. Python API verification

[Contracts](../../clustering-conventions.md) state exact defaults, ranges, shapes,
seed/state/tie rules and numerical/resource limits. All provide fit(X)/fit_predict(X),
without targets/sample weights. K-Means, Mean Shift and GMM provide meaningful
new-row prediction. K-Means transforms to center distances and scores negative SSE;
GMM exposes component responsibilities, sample log densities, mean score, AIC/BIC.
Hierarchies/DBSCAN/HDBSCAN/spectral remain transductive; no fake centroid predictor.

Dense numeric features are finite with magnitude<=10^12; standard n<=512,p<=32,
hierarchies n<=128 and HDBSCAN/spectral n<=256. Precomputed spectral affinity has
its distinct square-matrix contract. Inputs and global RNG are unchanged, query
shapes are checked, supported empty predictions work, failed refits preserve state
and changed invalid parameters cannot bypass validation. Cluster IDs are not
supervised class meanings. Canonical K-Means is reused for GMM initialization and
spectral partitioning, while prior B1/B2 numerical contracts are reused unchanged.

## 7. Mathematical correctness

K-Means has independent centroid stationarity, distortion and fixed-point checks;
empty repairs never fabricate fewer than K clusters. Ward heights use the
sqrt(2*DeltaSSE) convention and stable Euclidean norms. DIANA tests independently
recalculate every selected parent diameter, seed and splinter move on random tiny
data. DBSCAN verifies self-inclusive support, core/border/noise and ambiguous-border
rules, including early noise later becoming border.

HDBSCAN tests core distances, mutual-reachability matrices, independent MST weight,
condensed edge lifetimes, mass stability and exhaustive disjoint-subset EOM choices.
This is the full essential hierarchy/selection pipeline, not repeated DBSCAN cuts.
Mean Shift tests neighborhood-mean fixed points and finite-difference Epanechnikov
profile gradients away from radius boundaries. GMM tests weighted ML moments,
Cholesky Gaussian density/responsibilities and information-criterion counts.
Spectral tests eigen residuals, orthogonality, subspace projectors, row norms,
disconnected-component recovery, normalized cut and canonical K-Means reuse.
No local/nonconvex method is presented as a globally optimal semantic partition.

## 8. Numerical stability

Targeted numerical selection: **21 passed / 185 deselected**. Stable scaled norms
avoid prematurely squaring tiny/huge raw distances. K-Means fits in uniformly
normalized coordinates and retains separate offset/scaled center representation;
physical tiny SSE can round to zero without causing a false convergence shortcut.
Ward compares square-root merge heights. Mean Shift uses anchor-centered means.
GMM uses positive regularization, eigen-resolution checks, Cholesky solves and
row-normalized shifted exponentials. An explicit extreme-query test verifies equal
huge negative log scores still yield responsibilities [0.5,0.5], rather than a row
sum of two after a rounded log-sum subtraction.

HDBSCAN uses a globally scaled inverse-distance lambda. Its positive multiplier
preserves finite EOM choices and membership ratios; raw public lambda/stability
units therefore differ from unscaled 1/d. Zero-distance duplicates use extended-real
lifetimes, with equal infinite endpoints interpreted as zero duration and explicit
infinite-selection ties. Finite relative density>10^300 fails explicitly. Spectral
normalizes degrees in sequential divisions to handle uniform tiny affinity weights.
Unresolved covariance directions, zero embedding rows, isolated affinity vertices,
collapsed mixture mass and exhausted iteration budgets fail rather than returning
partial/unverified success. Expected negligible underflow is documented; invalid,
divide-by-zero and overflow errors remain checked. Numerical precision cannot
recover differences already lost in input float64 values.

## 9. Independent oracle results

Targeted oracle selection: **22 passed / 184 deselected**. Oracles include exact
centroid/SSE values, Ward identities, full DIANA decision traces, DBSCAN support,
HDBSCAN lifetimes and exhaustive nonoverlapping selections, KDE gradients,
independent Gaussian moments/densities, graph projectors/cut and hand-computed
silhouettes/pair agreement. They do not call an implementation helper as the sole
source of expected values. New metric oracles check singleton silhouettes, explicit
noise coverage and degenerate ARI partitions.

## 10. Independent reference comparisons

Targeted reference selection: **23 passed / 183 deselected**, with installed
scikit-learn 1.8.0 and SciPy 1.18.1. Align explicit Lloyd centers/stopping, Euclidean
linkage heights, self-inclusive density support, exact dense HDBSCAN/EOM/root
exclusion, flat Mean Shift neighborhoods and full GMM initial means/weights/global
covariance. Gaussian densities are independently checked with SciPy. Spectral
checks compatible graph partitions and eigenspace projectors rather than falsely
requiring the same eigenvector signs or every library’s rounding convention.

No installed direct DIANA reference is substituted by a different divisive method;
its independent complete splinter-trace oracle follows the primary R/cluster
algorithm definition. [Source verification](../../clustering-evidence/reference-sources.json)
records actual retrievals and the initial author-PDF timeout, with title/authorship
verified through the primary host’s search metadata. No external code/prose copied.

A separate [reproducible reference experiment](../../clustering-evidence/reference-audit-results.json)
checks ten additional HDBSCAN normal datasets, seeds 16200..16209, n=18,p=2:
all partitions have adjusted Rand=1, and the largest strength difference is below
2.6e-15. These are separate audit cases, **not added to pytest totals**.

## 11. Randomized test results

Fixed seeds 16011..16013 cover Lloyd references; 16021..16023 complete DIANA traces;
16024..16026 DBSCAN partitions/cores; 16031..16034 HDBSCAN references/EOM;
16035..16036 Mean Shift; 16041..16044 mixture references and covariance regimes;
16100 cross-model contracts; 16101..16103 metric references. Numerical scale laws
map DBSCAN bandwidth/radius, K-Means/DIANA coordinates, spectral affinity/gamma and
GMM covariance regularization consistently. Tests do not assert row-permutation
invariance for ambiguous borders or equally optimal hierarchical trees.

## 12. Reproducibility and executed examples

All **16 example/equivalent JSON CLI executions** and **eight invalid-input CLI
checks** passed. [Example inputs/expected labels](../../clustering-evidence/example-inputs.json)
and [actual outputs](../../clustering-evidence/examples-results.json) are retained.
Dry runs independently justify centroids, splinter moves, core support, persistence,
mode order, Gaussian groups and the two-clique projector. Invalid CLIs exit 2 with
stderr and no labels JSON. No network dataset or model checkpoint is used.

The [executed benchmark](../../clustering-evidence/benchmark.json) uses seed 16027,
96 rows, two features, a fixed 64/32 train/test split, two Gaussian source groups
and uniform background. No fitted preprocessing or test-set tuning. All models fit
only training X; provenance labels are passed only to evaluation. Silhouette
excludes predicted noise and reports coverage; ARI includes all rows with -1 as a
label. Mean Shift singleton modes are not silently treated as a noise detector.
Only K-Means/Mean Shift/GMM have held-out assignment metrics, and GMM also has
held-out log likelihood and training AIC/BIC diagnostics. Transductive methods
report training partitions, not fabricated held-out classifier accuracy. Actual
fit/predict timings are observational; one construction/split establishes no winner.

## 13. Documentation checks

All eight lessons have exactly the established 25 numbered headings, in order,
with topic-specific equations, assumptions, essential mechanism, pseudocode,
executed dry run, justified time/space limits, application/selection criteria,
edge cases, numerical concerns, tests, comparisons and primary references.
Section 14 honestly states optional C++ absent. The generator preserves hand-written
lessons; 146 remaining managed pages are checked. All prior canonical lessons and
reports remain byte-identical. Current category navigation/approval guides alone
are refreshed. Local links and examples are validated.

## 14. Catalog and negative validation

Catalog retains 35/256/235, IDs, paths, membership ordering, prior statuses/approvals
and the blocked DPO record. Only B4 statuses/notes and development metadata changed.
Eight entries are tested after actual code, full lessons/examples and passing gates.
The existing 316 infrastructure tests execute genuine negative fixtures for missing
DSA Python/C++, missing ML Python/tests, valid optional absent C++, invalid partial
optional C++, duplicate IDs, unsafe paths, documentation drift and missing exact
README sections. [Negative-test mapping](../../clustering-evidence/negative-validation-matrix.json)
identifies actual test functions; final JUnit independently enumerates their results.
No validator rule, track policy, fixture or test was weakened/disabled.

## 15. B1 Regression regression checks

Baseline and final explicit gates both passed **281 B1 tests**, also included in
the final full run. Actual results are recorded in
[final command evidence](../../clustering-evidence/final-results.json) before delivery.
All seven canonical sources/tests/lessons and approved report/evidence/packages
are preserved byte-for-byte. No B1 fitting/metric behavior was rewritten.

## 16. B2 Classification regression checks

Baseline and final explicit gates both passed **398 B2 tests**, also included in
the full run; command evidence records actual execution. All eleven sources/tests/lessons and historical
review artifacts are preserved. Existing helpers are reused without mutation.

## 17. B3 Ensemble Methods regression checks

Baseline and final explicit gates both passed **253 B3 tests**, also included in
the final full run. Actual results are recorded in final command evidence. All eight canonical implementations, original tests/lessons, support and
review evidence/packages remain byte-identical. Phase 15 owner approval is explicit
in current catalog metadata; its generation-time package remains historical.

## 18. DSA regression checks

The final local --require-cpp run passed **3,141 tests**, with **zero
failures, errors or skips**. [JUnit-derived matrix](../../clustering-evidence/test-matrix.json):
B4 206, B1 281, B2 398, B3 253,
DSA 1,687 and infrastructure 316.
DSA includes **1,149 Python/shared-oracle tests** plus both C++ standards.
[Actual transcript](../../clustering-evidence/full-suite-attempt1.txt)
and [command records](../../clustering-evidence/final-results.json) preserve
interpreter, seed environment, elapsed time and exit status. No prior report is
substituted for this new execution. DSA code/tests/language policy are unchanged.

## 19. C++17 results

**269 DSA C++17 tests passed.** The final required-C++ run actually
compiled and executed them with the available Apple Clang toolchain. Infrastructure
also exercises compiler fixtures. No absent optional ML C++ is counted as a pass.

## 20. C++20 results

**269 DSA C++20 tests passed.** Both standards executed through the
unchanged fixtures in the same final run. Compiler availability/workflow configuration
alone is not used as execution evidence.

## 21. CI-equivalent checks

Targeted B4 **206 passed**; overlapping numerical/oracle/reference subsets **21/22/23**
passed. Catalog/generated checks and 316 infrastructure tests passed at each stage.
The final local required-C++ suite passed **3,141 tests**, zero failures/errors/skips. The actual final ZIP is
extracted and catalog/generated/scope/example/full-suite checks execute against it
using the external installed interpreter. Actual post-creation outputs live in the
external package JSON, avoiding recursive archive hashes. Hosted GitHub Actions
and other OS/Python/compiler matrices were **not triggered or verified**; local or
extracted results do not imply a hosted run. No unexecuted check is labeled passed.

## 22. Dependencies and compatibility

No dependency installation, upgrade or new framework. Reused Python 3.14.2,
NumPy 2.5.4, pytest 9.1.1, scikit-learn 1.8.0, SciPy 1.18.1 and PyYAML 6.0.3;
baseline/environment record actual platform and Apple Clang details. Runtime uses
NumPy/local/standard-library primitives only; sklearn/SciPy are independent test/
experiment references. Dependency manifests, hosted workflow, C++ fixtures, pytest
marker configuration and central track policy are unchanged. Shared prior helper
APIs remain byte-identical; no competing ML framework was introduced.

## 23. Files created

Eight solution/example/test sets; B4 support/conftest/metrics, cross-model/metric
tests and separate benchmark/reference audit; scope/conventions/checkpoints and
execution evidence; clustering runner/scope/example/package tools; this report
and artifacts/review-packages/clustering. The
[changed-file inventory](../../clustering-evidence/changed-files.json) compares with
the captured clean owner baseline. No large dataset, model weight or executable
is versioned or bundled.

## 24. Files modified

B4 planning lessons and required catalog status/notes; current guides/root README,
roadmap/getting-started/glossary; catalog generation/progress/index/category
navigation; review/package indexes. Prior canonicals, tests, reports, evidence,
ZIPs and sidecars are protected by [preservation proof](../../clustering-evidence/preservation-results.json).
The generator’s new B4 paragraph and B3-approved navigation do not alter validator
or language policy. No unrelated owner work was overwritten; HEAD/index baseline
is preserved except tracking the new report as AGENTS requires.

## 25. Confirmed defects

**No confirmed implementation defect required repair** in the completed B4 solvers
or approved prior algorithms. One initial reference-test assumption was incorrect:
equal single-linkage distances need not yield a unique internal merge order/count.
Heights agreed. The [finding](../../clustering-evidence/development-findings.json)
and failing batch1-attempt1 transcript remain preserved; it is not misreported as
an algorithm bug or silently discarded. Three initial sklearn HDBSCAN FutureWarnings
about its future copy default are also preserved in the first stage-3 transcript.

## 26. Fixes applied

The exact linkage-count comparison now uses a tie-free reference fixture. A
separate tied-case oracle checks heights, disjoint children, correct counts and full
membership rather than forbidding another valid merge order. HDBSCAN reference
calls explicitly set copy=True, resolving the FutureWarning without filtering or
suppressing it. Core algorithm definitions were not weakened to obtain green tests.
No prior approved source was changed. Subsequent targeted runs have no failures
or skips; every numbered attempt records actual exit status/output.

## 27. Known limitations

Dense bounded finite numeric data; naive pairwise/hierarchy work; no sample weights,
sparse/missing inputs, arbitrary metrics or production throughput guarantees.
K-Means needs K distinct observed rows and an assignment fixed point; local minima
remain, and original tiny SSE can underflow. DIANA is greedy direct splinter division,
not a global partition optimizer. Agglomerative ties/chaining/linkage assumptions
remain. DBSCAN ambiguous borders are first-reached, with one fixed density radius.

HDBSCAN fixes Euclidean alpha=1/EOM/root exclusion, normalized lambda units and
explicit duplicate infinity conventions; no leaf/epsilon selector, allow-single-root,
GLOSH or new-point prediction. Mean Shift fixes bandwidth/flat neighborhoods/all-row
starts and support suppression; any unfinished seed fails. GMM uses only full
regularized covariance, a collapsed-mass guard and local likelihood-tolerance EM;
unresolved covariance scales need rescaling/greater regularization, and covariance
regularization need not monotonically improve unregularized likelihood. Spectral
is dense RBF/precomputed Ng-Jordan-Weiss row normalization; isolated vertices,
K below graph components and unresolved embedding rows fail. Eigenspace/sign/tie
nonuniqueness and nonconvex rounding remain. No method is claimed semantically or
globally optimal. Numerical precision cannot recover lost float64 distinctions.

## 28. Unresolved blockers and unexecuted checks

No unresolved B4 implementation blocker. All final local gates passed; actual
extracted-package results are recorded in the external package JSON before delivery. Hosted CI and
other platform/version/compiler matrices remain unexecuted/unverified. The existing
DPO terminology blocker is unchanged and outside scope. New Phase 16 owner review
approval remains pending. External author-PDF direct-fetch limitations are recorded,
not reported as a failed algorithm check.

## 29. Exact reproduction commands

Activate .venv or install requirements-ml-test.txt in a separate environment, and
provide a C++17/C++20 compiler. From repository root:

```sh
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest machine-learning/unsupervised-learning/clustering -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
python -m pytest machine-learning/supervised-learning/regression -q
python -m pytest machine-learning/supervised-learning/classification -q
python -m pytest machine-learning/ensemble-methods -q
python -m pytest --require-cpp
python scripts/verify_clustering_scope.py --check-only
python scripts/verify_clustering_examples.py --check-only
python machine-learning/unsupervised-learning/clustering/experiments/benchmark.py
python machine-learning/unsupervised-learning/clustering/experiments/reference_audit.py
```

In a source export use --source-only with the scope verifier, since Git metadata
and historical archives are deliberately omitted. Old phase scope scripts describe
their original frozen phase state; the current verifier audits preservation against
the new baseline rather than weakening historical hashes.

## 30. Review package paths and integrity

artifacts/review-packages/clustering/algorithm-atlas-clustering-review.zip,
algorithm-atlas-clustering-review.zip.sha256 and algorithm-atlas-clustering-review.json.
The report path is docs/reviews/clustering/CLUSTERING-REVIEW-REPORT.md.
The ZIP contains all current source/tests/lessons/infrastructure and required
reports/evidence, including relevant B1/B2/B3 and DSA implementations. It excludes
.git, environments, caches, secrets, compiled binaries, large datasets/checkpoints
and nested historical ZIPs/sidecars. Previous artifact bytes remain unchanged.

The new no-overwrite packager checks required files, UTF-8, credential patterns,
unique safe regular paths, CRC, source-byte/per-file hashes and SHA-256. It extracts
the **actual ZIP**, runs catalog/generated/scope/examples/full --require-cpp checks
with external installed dependencies, then records actual output/status in the
external JSON. Source hashes are rechecked after execution. No recursive archive
hash, bundled environment, automatic dependency installer or invented CI result.

## 31. Owner approval

**Previous Phase 15 and earlier work approved. New Phase 16 B4 review: pending.**
Stop after verified delivery for explicit owner acceptance. No Phase 17, new ML
category, Deep Learning, AI, commit, push, tag, release or publication. No Git
identity changed; no unrelated staged/working changes discarded.
