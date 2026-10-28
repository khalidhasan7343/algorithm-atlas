# Phase 13 B1 Regression — completion audit review

Owner/maintainer: **MD.Khalid Hasan** · [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas) · [MIT](../../../LICENSE).
Prepared 2026-10-28 (Asia/Dhaka). **Current review approval: pending.**

## 1. Phase identity and authorization

This is a completion/verification audit of **Phase 13 — B1 Supervised Learning — Regression**.
The owner explicitly approved all previously completed work and authorized this
Regression audit. Earlier Phase 13, Phase 14 Classification and DSA work is
owner-approved; approval of these newly changed Regression artifacts remains
pending. This is not a new sequential phase or permission to start another category.
No commit, push, release, other ML category, Deep Learning or AI work is authorized.

## 2. Exact catalog scope and inventory

Current catalog B1 is named **Supervised Learning — Regression**, slug `regression`,
under `machine-learning/supervised-learning/regression/`. Its seven distinct
canonicals have no cross-category memberships. All seven already had solutions,
examples, tests and exact 25-section lessons before this audit.

| Canonical ID | Existing implementation retained | Mathematical method |
| --- | --- | --- |
| linear-regression | yes; fitting kernel unchanged | Centered minimum-norm least squares |
| ridge-regression | yes; fitting kernel unchanged | Augmented least squares, summed L2 objective |
| lasso-regression | yes; fitting kernel unchanged | Mean-loss L1 cyclic coordinate descent |
| elastic-net | yes; fitting kernel unchanged | Explicit L1/L2 cyclic coordinate updates |
| polynomial-regression | yes; fitting kernel unchanged | Graded monomials, canonical OLS reuse |
| support-vector-regression | yes; fitting kernel unchanged | Epsilon-SVR dual, linear/RBF, bounded ADMM |
| decision-tree-regression | yes; targeted numerical repair | Greedy squared-error CART, mean leaves |

Inventory remains **35 categories, 256 memberships, 235 canonicals**; 115 are
track-required complete, 120 remain including the unchanged blocked DPO topic.
There are no new algorithm IDs, paths or duplicated canonical implementations.

## 3. Baseline, owner changes and existing versus new files

Started on `main`, HEAD `f2cc7c295e0f3fcf83dcb67ab3e6cf8d9c2e1f7e`, with the
previous Classification work present as modified/untracked files and its report
already staged. [Baseline evidence](../../regression-audit-evidence/baseline.json)
records all 1,802 pre-existing file hashes, status, staged-diff hash, environment
and catalog. Those owner changes are retained; no reset, cleanup or new staging.
The original seven implementations are retained; **zero new algorithms**.
The original [approved report bytes](../../regression-audit-evidence/approved-regression-report.txt)
and previous package bytes are preserved separately rather than overwritten as history.

## 4. Confirmed defects

| ID | Confirmed defect | Independent reproduction |
| --- | --- | --- |
| R1 | Tiny nonconstant R² became perfect after squared errors/variance underflowed | [2,4,6] versus [1,3,5], scaled by 10⁻²⁰⁰: expected 0.625, observed 1 |
| R2 | Constant-target detection depended on rounded mean/underflowed MSE | Constant 0.1 returned about −5.19×10³¹; tiny imperfect constants returned 1 instead of 0 |
| R3 | Individual residual squares overflowed before a finite mean could be formed | One 10¹⁵⁵ residual among 2,048: expected ≈4.8828125×10³⁰⁶, observed infinity |
| R4 | CART squared-error underflow falsely marked distinct targets pure | [0,0,10⁻²⁰⁰,10⁻²⁰⁰] incorrectly returned one leaf instead of threshold 1.5/two leaves |

[Findings](../../regression-audit-evidence/findings.json),
[metric observations](../../regression-audit-evidence/metric-investigation.json)
and [tree observations](../../regression-audit-evidence/tree-underflow-investigation.json)
retain expected and pre-fix results. **Four confirmed defects fixed; none unresolved.**

## 5. Targeted fixes

Shared Regression metrics now scale residual norms before accumulation. MSE
squares an averaged root error rather than overflowing individual squares; MAE
avoids a raw overflowing sum. R² compares normalized target deviations and root
errors, and detects constant targets/prediction equality directly. Added RMSE,
MAE and a common four-metric result for the requested evaluation contract.
Unrepresentable final results fail explicitly; tiny final MSE can round to zero
while RMSE remains representable, without falsely implying R²=1.

CART now detects actual target equality, scales targets locally for split scoring
and compares square-root gains to preserve the existing min_impurity_decrease
units. Original-unit SSE diagnostics may underflow but never control purity/split
selection. Pure constant values are retained exactly. The other six fitting
kernels remain byte-identical. No Classification/DSA implementation was changed.

## 6. Mathematical audit of all seven algorithms

OLS retains centered least squares, unpenalized intercept, numerical rank and
minimum-norm convention without explicit normal-equation inversion. Ridge's
objective is half summed RSS plus alpha/2 squared coefficients; its augmented
solve and zero-penalty convention are consistent with the lesson. Lasso uses
half mean RSS plus alpha L1, with exact coordinate soft threshold and scaled KKT
stopping. Elastic Net's mixing ratio distinguishes L1 threshold from L2 curvature;
its pure-L2 endpoint maps to Ridge alpha=n·alpha.

Polynomial feature order, interaction terms, degree validation and train/query
transformation agree with graded monomials and canonical OLS reuse. SVR's box/
zero-sum dual, epsilon tube, kernel construction, residual stopping and approximate
primal/dual certificate match the stated objective. CART selects squared-error
partitions and mean leaves, not classification Gini, retaining deterministic ties,
depth/leaf bounds and root-normalized gain. Correctness is numerical evidence,
not a formal guarantee for every ill-conditioned float64 input.

## 7. Numerical tests and failed-attempt evidence

The original Regression suite ran before broader tests: **214 passed in 1.21s**.
New metric tests first produced **4 failed / 214 passed**, including the expected
pre-fix overflow warning. The expanded CART check then produced **1 failed /
280 passed**. Both failed transcripts are preserved in numbered audit evidence.
The latest targeted result is **281 passed**; numerical selection **95 passed /
186 deselected**. Deselection is intentional marker filtering, not skipped tests.
[Final stage results](../../regression-audit-evidence/final-results.json) identify
actual commands/timestamps/results; no failed attempt was relabeled or discarded.

## 8. Seeded randomized coverage

Existing fixed-seed tests remain unchanged, including noisy/collinear OLS/Ridge,
coordinate-descent reference data, multivariate polynomial expansion, both SVR
kernels and CART split enumeration. Added seeds 13311/13321 cover metric references
and independent polynomial powers through degree eight. All RNGs are local;
shared contracts verify deterministic fits and unchanged caller/global RNG state.
Sample sizes, feature budgets, tolerances and iteration counts are bounded.
No dataset download or network dependency is used by tests.

## 9. Independent mathematical oracles

Closed-form metric ratios and large/tiny error units reproduce the scoring defects
without using another copy of the same failing formula. Finite differences verify
smooth OLS/Ridge gradients and coordinate-model objectives away from L1 kinks;
KKT checks cover nonsmooth zeros. Hadamard-column data give exact sparse Lasso/
Elastic Net solutions and explicit scaling identities. Polynomial monomials are
independently enumerated with Cartesian exponent tuples, checking linear/cubic/
degree-eight basis consistency. SVR tests analytic primal/dual values, outlier
responses, monotonic C trade-offs and a wide zero-loss epsilon tube. CART uses
independent exhaustive split enumeration and an exact tiny piecewise target oracle.

## 10. Independent reference comparisons

The latest reference selection passed **42 tests / 239 deselected** with installed
scikit-learn 1.8.0. Comparisons align objective normalization, intercepts, regularization
and kernel parameters; nonunique cases compare meaningful predictions/objectives.
Ridge alpha zero uses the documented OLS rank convention. Numerical edge cases
use exact identities rather than assuming a library with similar floating-point
formulas is an infallible oracle. [Primary-source checks](../../regression-audit-evidence/reference-sources.json)
record official mathematical/API references; no external source code/prose copied.

## 11. Convergence and computational complexity

Lasso/Elastic Net expose objective history, KKT residuals, tolerance and bounded
iterations. SVR exposes residuals, equality feasibility and a numerical primal/
dual gap. Exhaustion raises explicit ConvergenceError and preserves prior state;
no unconverged fit is returned as successful. Direct least squares has no iterative
convergence claim. CART completion means bounded greedy construction, not global
optimality. Existing time/space claims remain appropriate; metric and node target
normalization add linear work/storage within existing asymptotic bounds.

## 12. Evaluation definitions and held-out experiment

[Evaluation contracts](../../regression-evaluation.md) define single-output MSE
(squared target units), RMSE/MAE (target units) and dimensionless R². Constant
observations, including one sample, return R²=1 only for exact predictions, else 0.
Empty/multi-output/ambiguous/nonfinite input is rejected; no sample weighting.

The [experiment](../../regression-audit-evidence/benchmark.json) keeps seed 13027,
48 training/24 held-out observations, the same two features/response, fixed
hyperparameters and a scaler fitted solely on training rows for all seven models.
Training/test metrics remain separate. It now reports MSE, RMSE, MAE and R²,
plus timing and solver/tree diagnostics. One synthetic response contains a
quadratic term; no universal model ranking or timing superiority is claimed.

| Model | Held-out MSE | RMSE | MAE | R² |
| --- | ---: | ---: | ---: | ---: |
| Linear | 0.081993 | 0.286344 | 0.252326 | 0.925717 |
| Ridge | 0.085858 | 0.293015 | 0.256754 | 0.922215 |
| Lasso | 0.086004 | 0.293265 | 0.255425 | 0.922082 |
| Elastic Net | 0.090514 | 0.300856 | 0.259619 | 0.917997 |
| Polynomial | 0.006557 | 0.080976 | 0.064516 | 0.994059 |
| SVR | 0.010999 | 0.104874 | 0.083333 | 0.990036 |
| CART | 0.137672 | 0.371042 | 0.329273 | 0.875273 |

## 13. Documentation audit

All seven lessons retain exactly the existing 25 headings in order, correct
contracts/objectives/derivations, pseudocode, dry runs, complexity and limitations.
Six lessons are byte-identical; CART's substantive numerical steps were corrected
without stylistic rewriting. The category links the new metric/unit/edge-case
contract. Relative Markdown links and generated navigation are validated. Original
approved report/package snapshots retain their handoff-time statuses and hashes.

## 14. Executed examples

All seven original example scripts, seven equivalent JSON prediction calls and
seven invalid-dimension CLI checks passed after the tree repair. Outputs retain
known analytical values, and invalid CLI input exits 2 with stderr/no prediction
JSON. See [example transcript](../../regression-audit-evidence/examples-after-tree.txt).
Original examples and CLI implementation files were not rewritten or duplicated.

## 15. Catalog and language policy

Catalog categories, memberships, canonical IDs/paths and out-of-scope records
are preserved. Existing B1 implementation statuses remain tested, with C++ optional
and absent; no placeholder C++ is created. DSA still requires Python/C++, both
C++17 and C++20. Track policy, validator, root pytest fixtures, requirements and
CI checks are unchanged. Current development metadata separates previous owner
approval from the new pending audit review and records approval of prior work.

## 16. Classification regression

All **398 Classification tests passed** in the current audit's explicit run.
All eleven canonical sources/tests/lessons, support, metrics, benchmark and
historical evidence/package bytes are unchanged. The pre-existing staged
Classification report and its exact staged diff are preserved. Only current
approval/navigation metadata acknowledges the owner's explicit approval.

## 17. DSA regression and both C++ standards

The final local full run passed **2,682 tests in 431.43s**, with **zero failures,
errors or skips**. The [JUnit-derived matrix](../../regression-audit-evidence/test-matrix.json)
contains 281 B1, 398 B2, 1,687 DSA and 316 infrastructure tests. DSA includes
**1,149 Python, 269 C++17 and 269 C++20** tests. The final command used
`--require-cpp`; both standards actually compiled and executed with Apple Clang.
[Final transcript](../../regression-audit-evidence/full-suite-attempt2.txt) and
[command records](../../regression-audit-evidence/final-results.json) retain timing,
interpreter, environment and exit status. The earlier 2,680-test run predates the
two CART audit tests and is preserved as superseded evidence.

## 18. CI-equivalent checks

Catalog/link validation, generated documentation for 162 pages, 316 infrastructure
checks, the full required-C++ suite and separate B1 numerical/reference/B2 gates
passed locally. Numerical 95 and reference 42 are overlapping B1 subsets; do not
add them to the 2,682 full-suite total. No final test was skipped. Initial four
metric and one CART audit failures were repaired; their transcripts remain.

The package verifier independently extracts the actual final ZIP and reruns
catalog/generated/scope/example/full-suite checks with external installed
dependencies. Its actual outcomes are recorded in the external package JSON.
Hosted GitHub Actions, other operating systems and other compiler/Python matrices
were **not run or verified**. Local execution does not establish hosted CI success.

## 19. Dependencies

No dependency installation or upgrade. Reused NumPy 2.5.4, pytest 9.1.1,
scikit-learn 1.8.0, SciPy 1.18.1 and PyYAML 6.0.3; exact environment is captured.
Core code uses NumPy and standard-library/local helpers only. scikit-learn is an
independent test reference, never an implementation wrapper. DSA-only development
remains possible with requirements-dev.txt; full ML testing uses requirements-ml-test.txt.

## 20. Known numerical and model limitations

Dense single-output float64, finite magnitude/sample/feature/cell limits; no
multi-output, sample weights, sparse matrices or missing-value imputation.
Final squared quantities below the representable range can round to zero; RMSE
can retain tiny units and R² no longer treats such zero as exact fit. Unrepresentable
final metrics raise ValueError. CART original-unit SSE diagnostics can underflow,
but splitting/purity uses normalized data. Scale normalization cannot recover
input differences already lost in float64. Ill conditioning and numerical rank
cutoffs limit coefficient accuracy. Bounded coordinate/ADMM solvers may not
converge on every scale. SVR is dense with n≤256; polynomial degree/features are
bounded; trees are greedy. No universal calibration/generalization/performance
claim. There is no unresolved B1 blocker; the existing DPO terminology blocker
remains outside scope.

## 21. Files created

Two meaningful audit test modules; audit runner/preservation/package scripts;
new scope/checkpoint/evaluation documentation; original-state/failure/reference/
execution evidence, metric/tree investigation and historical text snapshots.
The old approved ZIP/checksum/JSON are relocated byte-identically into a named
history folder before regenerating the requested active filenames. Exact audit-only
paths are listed in [changed files](../../regression-audit-evidence/changed-files.json),
relative to the captured nonclean starting tree rather than the older Git HEAD.

## 22. Files modified and reasons

Regression support metrics, the existing benchmark's four-metric reporting, and
CART source/lesson for confirmed numerical defects. Existing solver/example/test
files otherwise remain unchanged. Current catalog/AGENTS/README/contribution/
development/roadmap/getting-started/glossary/ML-standard/index/category navigation
reflect the authorized audit and explicit prior approvals. The existing Regression
report/package README and review/package indexes are refreshed. No approved
Classification/DSA implementation is changed, no owner work discarded and no
pre-existing staged content altered. Preservation checks identify every exception.

## 23. Reproduction commands

With the existing .venv activated, from the repository root:

```sh
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest machine-learning/supervised-learning/regression -q
python -m pytest machine-learning/supervised-learning/regression -m numerical -q
python -m pytest machine-learning/supervised-learning/regression -m reference -q
python -m pytest machine-learning/supervised-learning/classification -q
python -m pytest --require-cpp
python scripts/verify_regression_completion_audit.py --check-only
python scripts/verify_regression_examples.py --check-only
python machine-learning/supervised-learning/regression/experiments/benchmark.py
```

A fresh environment requires requirements-ml-test.txt and a C++17/C++20 compiler.
Source exports omit historical archives: use --source-only with the audit verifier.
The new stage runner preserves numbered attempts in regression-audit-evidence;
old phase evidence is not overwritten. Packaging uses the new audit package script
and refuses existing active outputs without their prior preservation step.

## 24. Package, history and integrity

Active deliverables are `artifacts/review-packages/regression/algorithm-atlas-regression-review.zip`,
its `.zip.sha256`, and `algorithm-atlas-regression-review.json`.
The original approved set is retained under
`artifacts/review-packages/regression/history/approved-before-completion-audit-2026-10-28/`;
[historical mapping](../../regression-audit-evidence/historical-package.json) records
original/destination paths and exact digests. Older history and Classification
packages/evidence remain untouched.

The new ZIP includes current repository source/tests/lessons/infrastructure/report,
excluding .git, environments, caches, compiled binaries, secrets, data/checkpoints
and historical/nested ZIPs/sidecars. Its verifier checks CRC, unique safe regular
paths, required contents, source hashes and SHA-256, extracts the actual archive
without Git metadata, then runs catalog/generated/scope/example/full-suite checks
using external installed dependencies. Actual post-creation outputs live in the
external JSON, avoiding a self-referential archive hash. No hosted result is inferred.

## 25. Current review owner checkpoint

**Previous work owner approval: approved. Current revised Regression review:
pending.** Stop after integrity-checked delivery for explicit owner acceptance.
Do not start another category, commit, push, create a release or publish. No Git
identity was changed. The pre-existing owner work and staged report remain intact.
