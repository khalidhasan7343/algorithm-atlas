# Phase 13 — Regression review report

Owner and maintainer: **MD.Khalid Hasan** · Repository: [algorithm-atlas](https://github.com/khalidhasan7343/algorithm-atlas) · [MIT License](../../../LICENSE).

Prepared 2026-10-27 (Asia/Dhaka). **Owner approval: pending.** This report covers
ML foundation and the first ML category only. Its final execution totals and
package verification are recorded below and in the linked evidence.

## 1. Phase and authorization

**Phase 13 — ML Foundation and Supervised Learning — Regression** follows the
existing Phases 11/12 sequence. The owner's new request confirms DSA implementation
complete and authorizes ML foundation plus B1 only, superseding the former
no-Phase-13 boundary. It does not retroactively change the conditional DSA audit
recommendation or the independent pending approvals for Phases 11 and 12.
No second ML category, Deep Learning, AI, commit, push or release is authorized.

## 2. Category identity

Catalog category **B1**, **Supervised Learning — Regression**, slug `regression`,
path `machine-learning/supervised-learning/regression`. It is the first ML category
in catalog order. Baseline inspection found seven planned canonicals, no existing
implementations and no cross-category memberships for these seven IDs. The
[scope table](../../regression-scope.md) was established before implementation.

## 3. Baseline and inventory

Started on clean branch `main`, HEAD `3bca5e03e254167d20f19af68797fca68ff27bbf`.
The [baseline](../../regression-evidence/baseline.json) captures the original
catalog/development state, versions, compilers and hashes of 1,551 tracked files.
Inventory remains **35 categories, 256 memberships, 235 canonicals**. There are
97 DSA canonicals; all remain implemented with Python and C++. Seven ML
canonicals bring track-required completed topics to 104; 131 remain, including
the unchanged blocked Dynamic Policy Optimization topic.

## 4. Complete canonical list

All paths below are relative to the category root. Every topic has its own
solution, example, Python test file and authored 25-section lesson.

| Canonical ID | Essential algorithm | Python / tests | C++ |
| --- | --- | --- | --- |
| linear-regression | Centered, rank-revealing least squares | tested | optional, absent |
| ridge-regression | Augmented least squares with unpenalized intercept | tested | optional, absent |
| lasso-regression | Cyclic soft-threshold coordinate minimization | tested | optional, absent |
| elastic-net | Explicit L1/L2 coordinate minimization | tested | optional, absent |
| polynomial-regression | Graded multivariate monomials + canonical OLS | tested | optional, absent |
| support-vector-regression | Epsilon-SVR dual, linear/RBF kernels, bounded ADMM | tested | optional, absent |
| decision-tree-regression | Greedy squared-error CART with explicit nodes | tested | optional, absent |

## 5. Python implementation and API

Dense single-output float64 estimators expose `fit(X,y)`, `predict(X)` and R²
`score(X,y)`. Polynomial Regression also exposes fitted `transform(X)`. X must be
two-dimensional and y one-dimensional; ambiguous reshaping is rejected. Fit
returns self; predictions have shape `(m,)`. Shared support handles array and
parameter contracts, finite arithmetic, metrics and JSON CLI dispatch, without
implementing a solver. Successful state is owned by the model; failed refits
preserve the last successful fit. Algorithms are deterministic and do not change
global random state. NumPy supplies decomposition/array primitives; no core
solution imports scikit-learn, SciPy, a deep-learning framework or a remote service.

## 6. Track-aware language policy

The [central policy](../../../scripts/track_policy.py) uses validated canonical
track paths rather than hardcoded topic IDs. DSA still requires Python, C++, both
test files and C++17/C++20 execution. Classical ML requires Python, meaningful
numerical tests and mathematical lessons. C++ source/tests are optional but must
form a nonempty pair with truthful statuses if supplied. All seven B1 records
leave `cpp_status: planned`, honestly recording that optional deliverable as
absent. No dummy C++ files or weakened DSA fixtures were introduced. Deferred
Deep Learning/AI retains the previous structural policy until separately authorized.

## 7. Mathematical correctness

OLS tests verify analytical coefficients, residual orthogonality and minimum-norm
rank-deficient fits. Ridge tests verify its summed-loss objective and normal
stationarity without implementing unstable normal-equation inversion. Polynomial
tests verify interaction order, exact quadratic responses and reuse of canonical
OLS. Lasso/Elastic Net test scalar soft-threshold solutions, objective descent,
KKT residuals and penalty endpoints; pure-L2 Elastic Net maps to Ridge alpha=nα.
SVR tests verify the known primal/dual value 0.405 for the worked linear example,
zero-sum/box feasibility and numerical gap/residual checks. CART checks mean-leaf
optimality, independently enumerated split scores, normalized gain and XOR
interaction behavior. These are numerical checks, not formal proofs of arbitrary
floating-point input accuracy or statistical generalization.

## 8. Numerical validation

The final ML run passed **214 tests in 1.55s**. The explicitly marked numerical
selection passed **29 tests, 185 deselected, in 0.53s**. Invalid input, ownership,
parameter and shape cases are also part of the full ML suite. Coverage includes
singular/near-singular and constant columns, repeated observations, large offsets,
nonfinite data, resource limits, adjacent representable tree thresholds and
RBF distance cancellation/legitimate underflow. Arithmetic overflow, invalid
operations and division by zero fail explicitly. See
[final results](../../regression-evidence/final-results.json) and
[numerical transcript](../../regression-evidence/numerical-attempt1.txt).

## 9. Independent references and gradients

**40 reference tests passed, 174 deselected, in 0.58s**, using scikit-learn 1.8.0.
Comparisons align objective scaling, intercept handling, kernel parameters and
rank conventions. Nonunique solutions are compared through predictions/objectives.
Finite differences check OLS/Ridge smooth gradients and Lasso/Elastic Net away
from L1 kinks. SVR differences check only the smooth dual quadratic; feasibility
and primal/dual tests cover the nonsmooth constrained solution. Gradients are
inapplicable to discrete CART split search. Tiny exact solutions and a separate
brute-force CART split oracle supplement library comparisons. The
[primary references](../../regression-evidence/reference-sources.json) were retrieved;
lessons link versioned official documentation and original optimization papers.

## 10. Seeded randomized checks

Tests use local NumPy generators and fixed seeds, including 13011/13012 for OLS,
13061/13062 for SVR, and 13071/13072 for tree checks. Source tests record their
own full seeds, dataset sizes and tolerances. CART enumerates 80 independent
12×3 split datasets. SVR tests both kernels on 12/25-row datasets against LIBSVM
predictions at matched C, epsilon and gamma, with 2e-4 absolute/relative tolerance.
Shared contract tests repeat all seven fits and verify exact deterministic
predictions, shapes, constant-target scoring and unchanged caller/global RNG state.

## 11. Iteration and convergence

Lasso/Elastic Net stop at a scaled maximum KKT violation and record objective
history, iterations and stopping threshold. Exhausted budgets raise ConvergenceError.
SVR requires ADMM residual checks plus a projected feasible dual and a scaled
primal/dual gap; its eigendecomposition is a numerical primitive, with explicit
roundoff handling. Fixed rho and bounded iterations do not promise convergence
on every allowed dataset. OLS/Ridge are direct solves; CART's `converged_` means
bounded tree construction completed, not global tree optimality. Tests exercise
successful stopping, iteration exhaustion and preservation of previous state.

## 12. Examples and held-out experiment

All **7 authored examples**, **7 JSON prediction CLI calls** and **7 invalid-shape
CLI calls** passed. Outputs match independent analytical values: OLS 7, Ridge 2,
Polynomial 9, Lasso 3, Elastic Net 26/11, SVR 1.8, and CART [1,5].
The [benchmark evidence](../../regression-evidence/benchmark.json) records seed
13027, 48 training / 24 held-out rows, two features, fixed hyperparameters, iteration
diagnostics, fit timing and MSE/MAE/R² for all models. Scaling is fitted solely on
training rows. Held-out MSE values are approximately 0.081993 (OLS), 0.085858
(Ridge), 0.086004 (Lasso), 0.090514 (Elastic Net), 0.006557 (Polynomial), 0.010999
(SVR) and 0.137672 (CART). This response contains a quadratic term; a single
illustrative split establishes no general model superiority or timing guarantee.

## 13. Documentation and links

All seven lessons contain exactly the existing 25 headings in order, including
an honest optional/absent C++ section. They explain objective, derivation,
training/inference, shapes, state, bounded complexity, dry run, numerical failure,
bias/variance, leakage and limits. Catalog validation checks local Markdown links
repository-wide. Generated documentation covers 173 managed planning/category/index
pages with zero drift; authored lessons are preserved. Planning pages in later ML
categories only describe the new language policy; their algorithm statuses and
implementation scope remain unchanged.

## 14. Catalog and policy validation

Catalog/link validation passed with inventory 35/256/235. Fourteen new policy
tests verify valid Python-only ML, optional paired C++, missing DSA C++, missing
Python/tests, partial optional C++, duplicate IDs and unsafe paths. The configuration
gate passed **316 infrastructure tests in 3.71s**. Schema version, IDs, canonical
paths, category order and every out-of-scope algorithm record remain identical.
The [preservation verifier](../../../scripts/verify_regression_scope.py) matched
**1,241 protected files**, including all 97 canonical DSA lessons/source/tests,
historical evidence, reports and artifacts. Only the review index may be extended.

## 15. DSA regression execution

The full repository suite with `--require-cpp` passed **2,217 tests in 435.81s**:
**1,687 DSA tests** (1,149 Python, 269 C++17, 269 C++20), 316 infrastructure
checks (including two toolchain checks per C++ standard) and 214 ML tests.
**Zero failures, errors or skips.** The unchanged root fixtures enforce compiler
availability and both standards. [JUnit-derived counts](../../regression-evidence/test-matrix.json)
and the [full transcript](../../regression-evidence/full-suite-attempt1.txt) record
actual execution; no hosted result is inferred.

## 16. CI-equivalent checks

Actual local environment: Python 3.14.2, macOS arm64, Apple Clang 21 selected via
g++. Catalog, generated-doc and ML/reference checks passed. The full required suite passed 2,217 tests with zero failures/skips. Actual-ZIP
extraction results are recorded in the external package metadata after freezing.
CI retains its Python 3.11/3.12/3.13/3.14 matrix, CXX=g++ and `pytest --require-cpp`;
it now installs ML test requirements and allows 20 minutes. **Hosted GitHub Actions
was not triggered or verified.** Local validation does not establish that matrix.

## 17. Dependencies

Runtime: `requirements-ml.txt`, NumPy>=2.3.4,<3. Development references:
`requirements-ml-test.txt` includes existing pytest/PyYAML dependencies and
scikit-learn>=1.8,<1.9. Installed versions: NumPy 2.5.4, scikit-learn 1.8.0,
SciPy 1.18.1, pytest 9.1.1 and PyYAML 6.0.3; transitive joblib/threadpoolctl/
cloudpickle versions are captured in the local environment where available.
The original pytest/PyYAML versions and `requirements-dev.txt` are unchanged.
Initial sandbox package-index DNS failure was resolved by an approved installation
retry. DSA-only setup still needs only `requirements-dev.txt`; no ML datasets or
frameworks are downloaded during testing.

## 18. Files created

Created seven sets of `python/solution.py`, `python/example.py` and
`tests/test_python.py`; category support/conftest, shared contract tests and the
held-out experiment; ML dependency files; track-policy and verification/packaging
scripts; policy tests; ML development/scope/checkpoint documentation; this report
and preserved evidence. Exact new paths are listed in
[changed-files.json](../../regression-evidence/changed-files.json). Artifact names
are listed in section 23 and externally record every packaged source hash.

## 19. Files modified

Catalog development metadata and only B1 algorithm statuses/notes; central validator
and generator; pytest marker configuration; CI dependency/cache/timeout settings;
AGENTS, README, CONTRIBUTING, development/roadmap/progress/index documentation;
the seven canonical planning READMEs replaced by genuine lessons; generated ML
planning/category policy text; A9/A10 category authorization notes; review/package
indexes. The exact list is in changed-files.json. No canonical DSA implementation,
test, lesson, historical report/evidence/archive, root compiler fixture, license
or original dependency file was changed.

## 20. Known limitations and boundaries

Dense single-output float64 only; no sparse inputs, sample weights, missing-data
handling or statistical confidence intervals. Inputs/expansions have explicit
sample/feature/cell/magnitude budgets. Ill conditioning and rank cutoffs limit
coefficient accuracy. Iterative convergence can fail explicitly. SVR uses a dense
kernel and at most 256 training observations; its feasibility/gap certificate is
approximate floating point. CART is greedy, discontinuous and tie-sensitive, with
bounded depth and no pruning. No algorithm promises causal identification,
generalization or dominance. Optional ML C++ is absent. Hosted CI and other local
Python/platform combinations are unexecuted. No unresolved scope blocker remains;
the separate DPO terminology blocker remains outside this category.

## 21. Defects and failed attempts

The first Batch 1 run had **1 failed / 43 passed**: scikit-learn Ridge(alpha=0)
retained a tiny singular direction, yielding coefficient norm ≈3.39×10¹³ rather
than the documented minimum-norm solution. Independent scikit-learn OLS matched
Atlas's norm ≈0.13517 and SSE ≈12.30088. The alpha-zero oracle was corrected to
the matching OLS convention; positive-alpha tests still use Ridge. The original
failure and [investigation](../../regression-evidence/ridge-reference-investigation.json)
remain preserved. The initial infrastructure probe had **2 failed / 296 passed**
while B1 status integration and a legacy generator-state fixture were incomplete;
both were corrected and the 316-test gate passed. The historical generator fixture
now honors its explicit legacy scope. Polynomial predict-before-fit was corrected
to issue the documented ValueError; huge scalar conversion errors are normalized
to ValueError. The first final-report link gate also caught a missing changed-files inventory;
it was generated and catalog/link validation then passed. Its failed transcript
is preserved. No failed attempt was silently relabeled as passing.

## 22. Reproduction commands

From the repository root, using the local virtual environment when available:

```sh
python -m pip install -r requirements-ml-test.txt
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
python -m pytest machine-learning/supervised-learning/regression -q
python -m pytest machine-learning/supervised-learning/regression -m numerical -q
python -m pytest machine-learning/supervised-learning/regression -m reference -q
python scripts/verify_regression_scope.py --check-only
python scripts/verify_regression_examples.py --check-only
python machine-learning/supervised-learning/regression/experiments/benchmark.py
```

Source exports omit historical ZIPs: use `--source-only` with the scope verifier.
DSA-only development: install `requirements-dev.txt`, run `pytest tests dsa --require-cpp`.
The stage runner preserves numbered transcripts; it does not overwrite failures.
The package script refuses to overwrite an existing final archive or sidecar.

## 23. Review package locations

Files under `artifacts/review-packages/regression/`:

- `algorithm-atlas-regression-review.zip`
- `algorithm-atlas-regression-review.zip.sha256`
- `algorithm-atlas-regression-review.json`

The [package directory](../../../artifacts/review-packages/regression/README.md)
links these deliverables. ZIP includes current source, configuration, all lessons,
tests, report, relevant infrastructure and historical text evidence. It excludes
.git, environments, caches, secrets, compiled binaries, datasets/checkpoints and
historical/nested ZIPs/sidecars. Historical originals remain unchanged locally.

## 24. Integrity and extraction verification

Before handoff, the package script checks unique safe regular-file paths, CRC,
required contents, high-confidence credential patterns and exact source bytes;
it extracts the actual archive into a fresh temporary folder without .git and
reruns catalog, generated docs, scope, examples and the full `--require-cpp` suite.
Dependencies come from the existing external development interpreter, not a bundled
environment. The external JSON records actual extraction outputs after archive
creation, avoiding a self-referential checksum. Final status is authoritative in
that sidecar; the ZIP's report describes the verification protocol and local
pre-package results. A separate SHA-256 command verifies the completed archive.

## 25. Owner checkpoint

**Owner approval: pending.** The category may be implemented/tested without being
owner-reviewed or approved. Stop after verified package delivery. Do not begin
Classification or any other ML/Deep Learning/AI category. No commit, push, release
or publication has been performed. Independent historical owner checkpoints remain
unchanged.
