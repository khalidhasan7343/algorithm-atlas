# Phase 15 — B3 Ensemble Methods review report

Owner/maintainer: **MD.Khalid Hasan** · [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas) · [MIT](../../../LICENSE).
Current Phase 15 owner approval: **pending**. Prepared for owner review on **2026-10-30 (Asia/Dhaka, client date)**.
Execution evidence retains its original recorded timestamps.

## 1. Phase identity and authorization

Phase 15 implements only catalog category B3 Ensemble Methods. The owner explicitly
said “I approved previous now follow this” immediately after the completed latest
Regression audit handoff. [Approval evidence](../../ensemble-methods-evidence/approval-verification.json)
verifies both latest B1/B2 package hashes and passed extraction results before
proceeding. The current catalog records the latest B1 audit as approved separately
from the historical Phase 13 approval and from the new pending Phase 15 review.
Old report/package generation-time pending statuses remain historical bytes.
No further category, commit, push, tag, release or publication is authorized.

## 2. Repository discovery and starting state

Branch main; starting HEAD `d5bd29d7444f8890b5384a2be4e9d428a33653d1`.
The owner had advanced the repository since the earlier handoff; this Phase 15
started from a **clean working tree**, not the earlier nonclean audit tree.
[Baseline](../../ensemble-methods-evidence/baseline.json) records 1,913 pre-existing
file hashes, exact Git/index status, compiler, Python/platform and dependencies.
No destructive Git command, identity change, dependency installation or download.

Read AGENTS, catalog, README, CONTRIBUTING, development/ML guidelines, progress,
roadmap/index, pytest configuration/fixtures, ignore rules, CI, prior B1/B2 code
and reports, track policy, validators, generators and package utilities. Existing
canonical ML contracts/metrics are reused, and DSA language policy is unchanged.

## 3. Verified catalog scope

B3 is **Ensemble Methods**, slug `ensemble-methods`, at
`machine-learning/ensemble-methods/`. Eight items own eight distinct canonicals,
with **no cross-category memberships**. All were planning records at baseline.
Inventory remains **35 categories, 256 memberships, 235 canonicals**; after these
eight tested completions, 123 are complete and 112 remain including blocked DPO.
No Extra Trees, LightGBM or later-category algorithm was invented or implemented.
[Scope lock](../../ensemble-methods-scope.md).

## 4. Algorithm inventory and implemented variants

| Canonical ID | Implemented public models | Core mechanism |
| --- | --- | --- |
| bagging | BaggingClassifier, BaggingRegressor | Bootstrap independent bases; hard votes/scalar means; optional OOB coverage |
| random-forest | RandomForestClassifier, RandomForestRegressor | Canonical bootstrap reuse; fresh node feature subsets; mean leaf probabilities/scalars |
| adaboost | AdaBoostClassifier | Discrete multiclass SAMME; weighted-Gini trees and log example weights |
| gradient-boosting-machine | GradientBoostingRegressor | Mean initialization, squared-loss residual trees and shrinkage |
| xgboost | XGBoostRegressor | Exact dense second-order squared-loss splits, L2/gamma and Hessian bounds |
| catboost | CatBoostRegressor | Ordered TS plus original naive prefix ordered boosting Algorithm 1; symmetric trees |
| voting-classifiers | VotingClassifier | Hard/soft fixed weighted aggregation with label-column alignment |
| stacking | StackingClassifier, StackingRegressor | OOF probability/scalar features, separate meta-fit, fresh full-data bases |

XGBoost/CatBoost implement the named mathematical mechanisms with explicit bounded
subsets; production framework feature/API parity is not claimed. CatBoost is the
original direct prefix-model formulation, not plain GBM relabeled as CatBoost.

## 5. Existing implementations and canonical reuse

All eight B3 implementations are new. No pre-existing B3 solver was overwritten.
Original planning READMEs were replaced by full lessons. The B3 weighted tree is
shared ensemble infrastructure, not a second canonical CART lesson. Random Forest
reuses the canonical Bagging sampling/aggregation loop and adds per-node feature
sampling. Voting/Stacking defaults reuse canonical Gaussian NB, Linear Regression
and Ridge where appropriate. B1/B2/DSA code, original tests/lessons, reports,
evidence and all historical packages remain byte-identical to the baseline.
[Preservation proof](../../ensemble-methods-evidence/preservation-results.json).

## 6. Python implementations and language policy

Each actual catalog folder contains a nonempty Python solution, executable example
and meaningful tests. Core source imports NumPy and standard-library/local helpers;
no sklearn/XGBoost/CatBoost framework estimator wrapper. Public APIs and bounds
are in [contracts](../../ensemble-methods-conventions.md). ML requires Python,
mathematical/numerical tests and exact lessons; optional C++ is absent for all eight
and cpp_status remains planned. No dummy C++ source/test. DSA Python/C++ and both
C++17/C++20 remain mandatory through the unchanged track-aware policy.

## 7. Mathematical verification

Independent checks establish weighted Gini partitions, scalar/class aggregation,
SAMME errors/alphas/normalizations, negative-gradient stages, finite-difference
first/second derivatives, Newton leaf stationarity and exhaustive regularized
split gains. CatBoost tests ordered statistics and target exclusion by altering
current/future targets while checking all preceding prefix models. Constant-feature
prefix means are calculated independently through multiple rounds; symmetric-tree
splits are enumerated on a tiny exact dataset. Stacking verifies held-out row
exclusion, exact OOF coverage and independent meta-model rational predictions.
These are bounded numerical checks, not formal exact-real or universal accuracy proofs.

## 8. Bootstrap and sampling verification

An independent local RNG reconstructs actual bootstrap indices and subsequent
estimator seeds. Tests check replacement/repeats, sample sizes, independent model
identities, single-base behavior and OOB sets. Forest node candidates have the
requested distinct feature count and contain each chosen feature. XGBoost row and
tree-column samples are without replacement, with ceil fraction sizes. All random
state is local; global NumPy RNG and caller arrays remain unchanged.

## 9. Ensemble aggregation verification

Hard vote fractions and regression means are calculated from independently
collected base outputs. Forest probability columns are aligned by class identity,
including missing bootstrap classes. Voting tests reversed class arrays, unequal
weights and exactly representable ties. Soft combinations are finite normalized
convex combinations. Stacking checks each probability block and final meta-output.
Equal computed scores use sorted class order; near decimal ties can differ in float64.

## 10. Boosting update verification

SAMME uses alpha=eta[log((1-e)/e)+log(K-1)] and error-only log-weight increments.
The perfect weak learner uses finite alpha=1 and stops; at/worse-than-chance first
learners raise, later ones stop without being accepted. GBM residuals are y-F and
updates F+=eta*h; zero residuals stop before another tree. XGBoost uses g=F-y,
h=1, leaf -G/(H+lambda) and the parent/children score difference minus gamma.
CatBoost independently fits every nonempty prefix each round, using residuals
from the preceding-prefix model; the empty prefix stays at a fixed prior.

## 11. Numerical stability

Final targeted B3 numerical selection: **24 passed, 229 deselected**.
Weight normalization scales by maximum before summing. AdaBoost stores log weights
and never forms an infinite perfect-learner coefficient. Zero weights stay zero;
negligible normalized contributions may underflow as documented. Tree squared
errors use local target scaling; midpoint guards prevent invalid empty partitions.
Finite checks reject unresolved overflow/invalid updates. Large finite inputs,
tiny/constant targets, invalid probabilities, empty/mismatched data and failed
refits are exercised. Numerical bounds and unsupported features are explicit.

## 12. Independent oracle results

Final targeted oracle selection: **19 passed, 234 deselected**. Oracles cover
sampling/OOB, vote/probability/scalar aggregation, weighted impurity, exact boosting
stages, exhaustive Newton gains, ordered categorical statistics/prefix invariance,
symmetric tree partitioning, label alignment and OOF leakage exclusion. They do
not use an implementation helper as the sole source of the expected value.

## 13. Independent reference comparisons

Final targeted reference selection: **16 passed, 237 deselected**, using existing
scikit-learn 1.8.0 only in tests. Fits align actual bootstrap cohorts, tree depth,
SAMME variant/rate, squared-loss normalization, explicit stacking folds and class
columns. XGBoost at lambda=gamma=0/full sampling is compared with compatible
external GBM; general regularized gains use independent mathematical oracles.
CatBoost's original direct Algorithm 1 has independent prefix/statistic oracles;
no fabricated equality with the optimized production Algorithm 2 is asserted.

A seeded weighted-tree reference test initially overconstrained off-training
routing. The [investigation](../../ensemble-methods-evidence/weighted-tree-reference-investigation.json)
shows two equal-scoring feature rules with identical positive-weight training
partitions/predictions but different valid routing for one query. The corrected
comparison checks training predictions/objectives and query invariants, retaining
both the failure and tie-policy explanation. Source was unchanged for that finding.
[Primary-source verification](../../ensemble-methods-evidence/reference-sources.json)
records successful retrievals and publisher fetch limitations precisely.

## 14. Seeded randomized tests

Seeds 15001/15002 cover sampling and feature diversity; 15031/15032 cover Newton
gains and subsampling; 15100 covers cross-model deterministic/state contracts;
15111/15112/15113 cover independent weighted-tree references. Tests use small
bounded synthetic arrays, explicit tolerances, no network datasets or checkpoints.
Several marker groups overlap and are not summed as disjoint test totals.

## 15. Reproducibility and examples

All **16 example/equivalent CLI executions** and **eight invalid-shape CLI checks**
passed. [Inputs](../../ensemble-methods-evidence/example-inputs.json) and
[executed results](../../ensemble-methods-evidence/examples-results.json) are retained.
Known outputs include GBM [0.25,3.75], XGBoost [1.5,2.5], CatBoost [0,4] and
Stacking [146/173,562/173]. Stacking's rational oracle follows independently derived
OOF rows and Ridge equations. Invalid CLIs exit 2 with stderr and no prediction JSON.
Repeated fits retain predictions and class order; failing refits preserve fitted state.

The [experiment](../../ensemble-methods-evidence/benchmark.json) uses seed 15027,
64 observations, a fixed 48/16 train/test split and two features. It reports actual
fit/predict timings, classification accuracy/precision/recall/F1/confusion/log-loss
and regression MSE/RMSE/MAE/R2 separately on train/test. Single-base/3/9-model
comparisons are descriptive. CatBoost explicitly replaces feature 1 by its sign
category, so its feature view differs; it is not a controlled universal ranking.
No fitted preprocessing or test-set tuning is used. On this split nine forest
regressors have worse RMSE than three, illustrating why larger need not improve.

## 16. Documentation verification

Every B3 canonical has exactly the existing 25 numbered headings in order, with
specific equations, training/prediction, pseudocode, executed dry run, meaningful
complexity bounds, hyperparameters, edge cases, numerical/resource limits,
comparisons, exercises, references and maintainer attribution. Section 14 honestly
states optional C++ absent. Local links and generated navigation are validated.
All B1/B2/DSA lessons remain byte-identical; current category navigation alone is updated.

## 17. Catalog validation

Catalog/link validation passes with the original 35/256/235 inventory. Only B3
status/notes and active development/approval metadata changed. B3 IDs, paths,
ordering, difficulty, related topics, memberships and optional C++ status are
preserved; all other algorithm records are identical. Eight records are tested
only after actual source/tests/lessons/examples and passing gates exist. Generator
check covers 154 generated pages; eight new lessons are hand-authored and preserved.

## 18. B1 Regression regression results

Both discovery and final explicit gates passed **281 B1 tests**, also included
in the final full run. Actual commands/results are recorded in [final results](../../ensemble-methods-evidence/final-results.json)
before handoff. Prior B1 code/tests/lessons and both latest/historical package
bytes are preserved. Earlier approvals are recorded independently of Phase 15.

## 19. B2 Classification regression results

Both discovery and final explicit gates passed **398 B2 tests**, also included
in the final full run. Actual results are recorded in final-results.json. All eleven canonical implementations,
original tests/lessons and review/evidence/package bytes remain unchanged.

## 20. DSA regression results

The final local full run passed **2,935 tests**, with **zero failures,
errors and skips**. [The JUnit-derived matrix](../../ensemble-methods-evidence/test-matrix.json)
contains B3 253, B1 281, B2 398,
DSA 1,687 and infrastructure 316.
DSA comprises 1,149 Python/shared-oracle tests and the required
C++ tests below. [The actual full transcript](../../ensemble-methods-evidence/full-suite-attempt2.txt)
and [final command records](../../ensemble-methods-evidence/final-results.json)
retain interpreter, seed environment, elapsed time and exit status.
No DSA source/test or language policy changed.

## 21. C++17 and C++20 validation

**C++17: 269 DSA tests passed. C++20: 269 DSA tests passed.**
The final command used --require-cpp and both standards actually compiled and
executed through the existing fixtures with Apple Clang. Infrastructure also
exercised the toolchain. Optional absent ML C++ is not counted as a C++ pass.

## 22. CI-equivalent checks

All 253 targeted B3 tests pass. Numerical/oracle/reference subsets pass 24/19/16;
they overlap. Catalog, generated documentation and 316 infrastructure tests pass
locally. The final required-C++ full run passed 2935 tests with zero failures/errors/skips. The package's
external JSON records actual catalog/generated/scope/example/full-suite commands
against the extracted immutable ZIP. Hosted GitHub Actions and other platform/
Python/compiler matrices were not triggered or verified. Local/extracted results
do not claim a hosted CI run. No unexecuted check is labeled passed.

## 23. Dependencies added or changed

None installed or upgraded. Reused Python 3.14.2, NumPy 2.5.4, pytest 9.1.1,
scikit-learn 1.8.0, SciPy 1.18.1 and PyYAML 6.0.3; exact platform/compiler details
are in baseline/environment evidence. Runtime remains NumPy/local/standard-library.
The new oracle marker is registered in pyproject.toml; dependency manifests and
hosted CI configuration are unchanged. Production XGBoost/CatBoost packages are
not dependencies, and no heavyweight library was installed to hide missing logic.

## 24. Files created

Eight solution/example/test sets, B3 support/tree/contracts tests/experiment,
scope/checkpoint/conventions documentation and execution/evidence files;
validation, scope, example and package scripts; this completion report; and the
Ensemble Methods package folder. [Changed-file inventory](../../ensemble-methods-evidence/changed-files.json)
compares against the clean owner baseline, not an earlier phase snapshot.

## 25. Files modified

Only authorized B3 lesson/status metadata, active guides/approval navigation,
category/index/progress generation, review/package indexes and the registered
oracle test marker. All prior canonical implementations/tests/lessons and all
old reports/evidence/package bytes are protected by the baseline verifier.
Track policy, C++ fixtures, dependency manifests and hosted workflow remain unchanged.

## 26. Bugs found and fixed

Two confirmed **new B3 implementation defects** were repaired. First, a common classifier prediction
method read classes_ before validating fit state, raising AttributeError. Five
contract cases initially failed; the method now validates probability state first.
Second, valid observed targets at the 10^12 boundary can create larger internal
GBM residuals. The internal weighted tree now accepts finite residual targets up to
10^15 while all public observed-target caps remain unchanged. An independent
two-stage analytical regression test reproduces and verifies this repair.
The earlier 2,934-pass full run predates this added test/repair and is retained
as superseded evidence, not substituted for the final rerun.
[Development findings](../../ensemble-methods-evidence/development-findings.json)
also preserve three test-oracle corrections: exact decimal ties, a preliminary
Stacking expected-value assumption corrected via rational algebra, and valid
weighted-tree split ties. These are distinguished from implementation defects.
Failed transcripts remain; no failing attempt was relabeled as passing. An intermediate catalog/link check also failed while the final-results evidence path did not yet exist; the actual runner created it before final validation. That catalog attempt is retained. A whitespace check found extra end-of-file blank lines in eight new lessons; they were trimmed before source freeze.

## 27. Known limitations

Dense finite numeric arrays and explicit resource caps; single-output regression;
no sparse/missing-value or production-scale optimized learners. Factories must be
fresh and deeply independent; identity/common fitted attributes are checked, not
arbitrary hidden shared state. Probabilities are model/vote quantities, not guaranteed
calibrated. Greedy zero-gain tree stopping and deterministic tie policy can differ
from external trees. Extreme weight ratios/small gains can be unresolved in float64.

GBM/XGBoost/CatBoost expose regression only; SAMME is discrete classification only.
XGBoost has only half squared loss and L2/gamma exact splits, without missing/sparse
routing, L1, histograms, ranking, GPU/DART/distributed features. CatBoost directly
implements original prefix Algorithm 1 with one shared permutation and ordered TS,
not production Algorithm 2; n<=64,p<=8,T<=16,d<=3 and O(T*p*2^d*d*n^3) conservative
fit bound. Prefix-zero remains fixed, so loss need not decrease monotonically.
Stacking retains fold models, requires minority count>=folds and has no passthrough,
prefit shortcut or nested tuning. Single synthetic split/timings establish no winner.

## 28. Unresolved issues

No unresolved B3 implementation blocker. All final local gates passed; actual
extracted-ZIP outcomes are recorded in the external package JSON before delivery. The existing DPO terminology
blocker remains outside scope. Hosted CI and other platform/compiler matrices
remain unexecuted/unverified; publisher fetch limitations are recorded separately.
New Phase 15 review owner approval remains pending.

## 29. Reproduction commands

Activate the existing .venv or install requirements-ml-test.txt in a separate
Python environment; provide a C++17/C++20 compiler. From repository root:

```sh
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest machine-learning/ensemble-methods -q
python -m pytest machine-learning/ensemble-methods -m numerical -q
python -m pytest machine-learning/ensemble-methods -m oracle -q
python -m pytest machine-learning/ensemble-methods -m reference -q
python -m pytest machine-learning/supervised-learning/regression -q
python -m pytest machine-learning/supervised-learning/classification -q
python -m pytest --require-cpp
python scripts/verify_ensemble_methods_scope.py --check-only
python scripts/verify_ensemble_methods_examples.py --check-only
python machine-learning/ensemble-methods/experiments/benchmark.py
```

Use --source-only with the scope verifier in a source export without .git or
historical archives. Old phase scope verifiers describe their original frozen
phase/catalog snapshots; the current Phase 15 verifier checks preservation instead.
No network dataset or model download is needed by these commands.

## 30. Review package details

Deliverables: artifacts/review-packages/ensemble-methods/algorithm-atlas-ensemble-methods-review.zip,
its .zip.sha256 and algorithm-atlas-ensemble-methods-review.json. The ZIP includes
all current source/tests/lessons/infrastructure, this report and required evidence,
including prior B1/B2/DSA code. It excludes .git, environments, caches, secrets,
binaries, large data/checkpoints and nested historical review archives/sidecars.

The new package script refuses existing outputs, checks required payloads, UTF-8,
credential patterns, safe unique regular paths, CRC, per-file source hashes and
SHA-256. It extracts the actual ZIP and runs catalog/generated/scope/examples/full
required-C++ checks with the external installed interpreter. Actual post-creation
outputs and final tracking status live in the external JSON, avoiding recursive
archive hashes. All prior review packages remain byte-identical.

## 31. Owner approval status

**Prior B1 audit/B2/DSA work approved; new Phase 15 B3 review approval pending.**
Stop after verified delivery for explicit owner review. No Phase 16, next ML
category, Deep Learning, AI, commit, push, tag, release or publication. No Git
identity was changed and no unrelated owner work was overwritten.
