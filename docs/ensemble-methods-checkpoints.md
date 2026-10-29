# Phase 15 — Ensemble Methods checkpoints

[Scope lock](ensemble-methods-scope.md). Prior B1 audit and B2 Classification are
explicitly owner-approved; new Phase 15 review approval is **pending**.

## Discovery

The starting branch is main; HEAD and exact working-tree/hash/environment baseline
are in [baseline.json](ensemble-methods-evidence/baseline.json). The starting tree
is clean. All eight B3 entries are planned, with no implementation files. Existing
ML array/label/metric conventions and Python-first policy remain; DSA retains both
C++17/C++20. No dependencies are installed/upgraded.

## Stages and actual validation

Stage 1: Bagging and Random Forest — **27 passed** initially; later independent reference cases are included in the final combined suite.
Stage 2: AdaBoost and GBM — **21 passed** initially; later guard cases included in combined gates.
Stage 3: XGBoost and CatBoost — **21 passed** initially; added external zero-regularization comparison included in combined gates.
Stage 4: Voting and Stacking — **20 passed** after correcting one exact-tie test input assumption; the failed attempt is preserved.
Numbered transcripts preserve every executed attempt, including failures and corrections.
Final local outcomes are recorded below; actual ZIP extraction checks are in the external package JSON.

## Owner boundary

Stop after the completion report and integrity-checked ZIP/checksum/JSON for
explicit owner review. No next category, Git commit/push/tag or release.

## Integration evidence

The initial combined B3 run exposed one new shared predict-before-fit contract
bug (five failing cases); it was repaired only in B3 support. Initial voting and
stacking-example oracle assumptions were corrected with exact binary fractions
and independently derived Ridge rational predictions. See
[findings](ensemble-methods-evidence/development-findings.json). All failed attempts
remain in numbered transcripts. Prior B1/B2 baseline tests passed 281/398.
All eight lessons have exactly 25 sections; 16 example/CLI and eight invalid CLI
checks pass. [The held-out experiment](ensemble-methods-evidence/benchmark.json)
records actual train/test metrics and measured timings without superiority claims.
Final full-suite and archive-extraction outcomes are recorded before handoff.

A final boundary check confirmed a second new B3 defect: valid observed GBM targets
could yield residuals beyond the shared observed-target cap. One new analytical
case failed before repair. The internal tree now has a separate finite 10^15
derived-target bound; public observed-target limits remain 10^12. The earlier
2,934-pass broad run is preserved as superseded evidence. The full gate is rerun
after the fix. Targeted B3: 253 passed; numerical 24; oracle 19; reference 16.

## Final local validation

B3 **253 passed**; numerical **24 passed / 229 deselected**; oracle **19 passed /
234 deselected**; reference **16 passed / 237 deselected**. The marker selections
overlap. Final B1/B2 gates passed **281/398** unchanged.
The full required-C++ gate passed **2,935 tests**, zero failures/errors/skips:
DSA 1,687 (Python/shared 1,149; C++17 269; C++20 269),
B3 253, B1 281, B2 398, infrastructure 316.
See [matrix](ensemble-methods-evidence/test-matrix.json) and
[final command evidence](ensemble-methods-evidence/final-results.json).
Catalog/link and 154 generated-page checks pass. All eight lessons have 25 sections;
16 examples/equivalent CLIs and eight invalid-input CLI checks pass. Scope checks
preserve all 1,855 protected pre-existing files. Hosted CI/other platforms are not
run or verified. Current Phase 15 review approval remains **pending**.
