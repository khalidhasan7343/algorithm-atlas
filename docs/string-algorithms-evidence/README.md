# Phase 9 execution evidence

This directory contains observed commands and deterministic reference evidence.
[Checkpoints](../string-algorithms-checkpoints.md) record sequential gates;
[the review report](../reviews/string-algorithms/STRING-ALGORITHMS-REVIEW-REPORT.md)
explains final results and limits. Phase 9 owner approval remains pending.

- `batch1-results.json` through `batch3-results.json` and matching text logs:
  real per-batch Python/C++17/C++20 pytest runs.
- `batchN-configuration-results.json`: per-batch catalog, generated-doc and
  infrastructure gates. Initial failed integration logs are retained explicitly.
- `final-results.json` and `final-*.txt`: separate language selections and the
  complete discovered repository suite, including all eight prior categories.
- `cross-matrix-batch*.json`: independently executed semantic comparisons.
- `oracle-inventory.json`: seeds and vector counts; `regression-inventory.json`
  counts collected tests and points to execution evidence (collection is not a pass).
- `complexity-results.json`: code-path complexity audit and bounded performance
  observations, with no machine-dependent runtime pass/fail thresholds.
- `examples-results.json`: exact lesson input/output executed in both languages
  and both C++ standards.
- `sanitizer-results.json`: local C++20 ASan/UBSan execution.
- `approved-baseline.json`, `catalog-baseline.yaml`, `preservation-results.json`:
  original identities and protected historical bytes, checked without changing
  approval-time artifacts. Current navigation exceptions are named explicitly.
- `tracking-results.json`, `changed-files.txt`: nonempty/unignored report and
  completion-pointer checks plus source/artifact manifest. The new report and
  source are ready to track; the Git index was not changed.

Package extraction, per-file hashes, CRC and SHA-256 verification are recorded
in the external package JSON under artifacts/review-packages/string-algorithms/.
No commit, push, publication or hosted GitHub Actions pass is claimed.
