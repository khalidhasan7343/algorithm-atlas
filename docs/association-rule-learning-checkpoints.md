# Phase 18 checkpoints

Latest Phase17 explicitly owner-approved; new Phase18 B6 authorized and review
pending. [Scope](association-rule-learning-scope.md). Baseline main at
c5a334e7750b55d6955edb50ed440587e00309e7, with accepted Phase17 staged/unstaged/untracked
changes preserved; this is not a clean checkout. The existing staged B5 report
must remain byte-identical. [Baseline](association-rule-learning-evidence/baseline.json)
holds2373 working-tree hashes and initial exact staged-diff digest.

Baseline gates passed: B1 281, B2 398, B3 253, B4 206, B5 162; catalog/generated
checks passed. All four new internal batches initially pending. Canonical catalog
batches1–3 progress only after code/lessons/examples/tests pass; batch4 rule utility
is a separate mandatory gate, not a fourth canonical. Numbered attempts preserve
all failures and actual execution timestamps. Final full-suite and actual ZIP
extraction checks remain pending until executed. Stop for owner review after delivery.

All three canonical gates passed: Apriori14, Eclat13, FP-Growth16. Mandatory
batch4 rules29 passed; full B6 audit162 passed, numerical5/oracle51/reference7
(overlapping selections). Three worked examples and their equivalent/invalid
CLIs passed, plus all three rule CLIs. Initial collection syntax failure is fixed
and retained. Canonical statuses are tested, completed_batches1..3, active null;
phase_records.18.rule_generation_status=tested. Final broader gates/package checks
remain pending until executed. New owner approval remains pending.

Final local validation completed: 3472 passed, zero failures/errors/skips.
B1/B2/B3/B4/B5 passed281/398/253/206/162; B6 passed162, with numerical5/oracle51/
reference7/randomized18 overlapping subsets. Infrastructure323 passed. DSA1687
includes Python/shared1149, C++17 269 and C++20 269. See [final records](association-rule-learning-evidence/final-results.json)
and [JUnit matrix](association-rule-learning-evidence/test-matrix.json). Actual ZIP
extraction checks run after archive creation and record outputs in external JSON;
the immutable source payload is not rewritten recursively. Stop for owner review
after verified delivery; Phase18 owner approval remains pending.
