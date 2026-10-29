# Phase 15 — Ensemble Methods review package

Owner: **MD.Khalid Hasan** · [MIT](../../../LICENSE).
Previous work is owner-approved; **Phase 15 owner review is pending**.

Read [the completion report](../../../docs/reviews/ensemble-methods/ENSEMBLE-METHODS-REVIEW-REPORT.md),
[scope](../../../docs/ensemble-methods-scope.md), [contracts](../../../docs/ensemble-methods-conventions.md)
and [checkpoints](../../../docs/ensemble-methods-checkpoints.md). All eight actual
catalog B3 canonicals have from-scratch NumPy implementations, exact lessons,
examples and mathematical tests. XGBoost/CatBoost limits are explicit.

Run `python scripts/package_ensemble_methods_review.py` from the repository root
with the installed ML test environment. It refuses existing active outputs. Files:
`algorithm-atlas-ensemble-methods-review.zip`, its `.zip.sha256`, and
`algorithm-atlas-ensemble-methods-review.json`. Run
`shasum -a 256 -c algorithm-atlas-ensemble-methods-review.zip.sha256` here.
Metadata records safe paths/CRC/source hashes, actual extracted-source checks,
required-C++ full-suite output and the current pending owner review.

Extract the ZIP, use a separate environment with requirements-ml-test.txt and a
C++17/C++20 compiler, then follow reproduction commands in the report. The verifier
uses an external installed interpreter; environments, secrets, binaries, model/data
files and nested historical ZIPs/sidecars are excluded. Historical packages retain
their original bytes and handoff metadata. Stop for owner review; no next category,
commit, push, tag, release or publication.
