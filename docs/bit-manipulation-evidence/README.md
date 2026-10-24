# Phase 10 execution evidence

[Checkpoints](../bit-manipulation-checkpoints.md) record sequential gates and
owner approval of completed Phase 9. [The report](../reviews/bit-manipulation/BIT-MANIPULATION-REVIEW-REPORT.md)
explains the final handoff. Phase 10 owner approval is pending.

- `approval-verification.json`: actual A6/A7 completion checks and verified prior
  ZIP integrity, with explicit owner approval recorded separately from immutable
  historical handoff-time metadata.
- `batch1-results.json`, `batch2-results.json` and text logs: executed Python,
  C++17 and C++20 algorithm tests. Per-batch configuration records preserve
  catalog/link, generated-document and infrastructure gates.
- `final-results.json`, `final-*.txt`: separate language selections and full
  discovered repository regression execution. Deselection in a targeted run is
  distinct from a skip; collection alone is not execution.
- `oracle-inventory.json`, `oracle-matrix.json`: exact seeds/case counts and
  independent frequency, representation, recursive and existing-Power-Set checks.
- `examples-results.json`: exact lesson examples executed in all three language
  configurations; `sanitizer-results.json` records local C++20 ASan/UBSan.
- `regression-inventory.json`: collected counts, with final execution evidence
  named explicitly; `environment.json` records actual local tools.
- `catalog-baseline.yaml`, `approved-baseline.json`, `preservation-results.json`:
  fixed inventory and hashes of prior implementation/history, with current
  navigation exceptions named rather than rewriting historical reports.
- `tracking-results.json`, `changed-files.txt`: nonempty/unignored report checks,
  completion pointer, Git inclusion readiness and complete changed-file manifest.

The external package JSON records source export, extracted checks, source hashes,
ZIP CRC and SHA-256. No hosted GitHub Actions pass, commit or push is claimed.
