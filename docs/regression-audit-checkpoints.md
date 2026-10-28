# B1 Regression — completion audit checkpoint

The owner approved all previous work and authorized only the B1 completion audit
on **2026-10-28 (Asia/Dhaka)**. Follow [the scope lock](regression-audit-scope.md).
Earlier owner approval does not approve new Regression changes. Current review
approval remains **pending**.

## Baseline and retained work

Branch main, HEAD `f2cc7c295e0f3fcf83dcb67ab3e6cf8d9c2e1f7e`. The nonclean
starting tree contains approved Classification work, its staged completion
report and untracked source/package files. No cleanup/reset or staging changes.
[The baseline](regression-audit-evidence/baseline.json) captures 1,802 existing
file hashes, exact status and staged-diff hash. All seven B1 solvers already exist.

Before broader tests, the original Regression suite passed **214 tests in 1.21s**;
catalog/link and 162-page generated-documentation checks passed. Existing
dependency versions are reused without installation.

## Confirmed metric defects

Independent cases reproduced R²=1 instead of 0.625 for tiny nonconstant targets,
R²=1 instead of 0 for tiny imperfect constant predictions, a large negative R²
for exactly constant decimal targets due to rounded mean, and intermediate-square
overflow producing infinite MSE despite a finite correct mean. New regression
checks initially had **4 failed / 214 passed**; transcripts and independent
[observations](regression-audit-evidence/metric-investigation.json) are preserved.

The targeted correction scales error norms, detects actual constant targets and
forms R² before tiny squared units disappear. RMSE and MAE complete the requested
evaluation set. All seven existing implementations are retained. A separate confirmed CART
squared-error-underflow defect required a targeted split-calculation repair; the
other six fitting kernels remain byte-identical. Final numerical/reference,
Classification, DSA, docs and packaging results are recorded before handoff.

## Additional CART underflow defect

A piecewise target [0,0,10⁻²⁰⁰,10⁻²⁰⁰] incorrectly produced one leaf because its
squared-error diagnostic underflowed to zero. Independent expected labels/optimal
threshold reproduce the failure; the expanded suite had **1 failed / 280 passed**.
The tree now normalizes targets locally for split scoring, detects pure targets
by equality and compares root gains to preserve original threshold units. Its
original diagnostic can still underflow when squared units are unrepresentable,
but never controls split/purity decisions. Evidence and prior tree bytes are retained.

## Final local gates

The final run passed **2,682 tests**, with **0 failures, 0 errors and 0 skips**:
B1 281, B2 398, DSA 1,687 (Python 1,149; C++17 269; C++20 269),
and infrastructure 316. B1 numerical/reference subsets passed 95/42 tests;
they overlap and are not added to the full count. Catalog/link and generated
162-page checks pass. All seven lessons retain exactly 25 sections and their
examples/invalid-input CLI checks pass. See the [matrix](regression-audit-evidence/test-matrix.json)
and [final transcripts](regression-audit-evidence/final-results.json).

The active catalog now awaits review. Historical phase approvals remain approved;
the new review is pending. Actual archive-extraction results and checksum/source
integrity are recorded in the package JSON after archive creation. Hosted CI and
other platforms were not run or verified.

## Owner review boundary

Update `docs/reviews/regression/REGRESSION-REVIEW-REPORT.md` and regenerate the
Regression ZIP/checksum/JSON after preserving their prior approved bytes. Stop
for explicit owner acceptance of the current review. No other category, commit,
push, release or publication.
