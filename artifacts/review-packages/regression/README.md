# Phase 13 — Regression review package

Owner: **MD.Khalid Hasan** · [MIT](../../../LICENSE) · **Owner approval pending**.

Review [the report](../../../docs/reviews/regression/REGRESSION-REVIEW-REPORT.md)
and [checkpoints](../../../docs/regression-checkpoints.md) for the seven B1
canonicals and Python-first ML foundation. DSA retains both languages and C++17/20.

The package script creates `algorithm-atlas-regression-review.zip`, its
`.zip.sha256` checksum and `algorithm-atlas-regression-review.json` metadata here.
Run `shasum -a 256 -c algorithm-atlas-regression-review.zip.sha256` from this folder.
Metadata records safe-entry/CRC/source-hash checks and actual extracted-source
test outputs. Historical ZIPs/sidecars, environments, caches, binaries and secrets
are excluded; original historical artifacts remain unchanged in the working tree.

Extract the archive and install `requirements-ml-test.txt` in a separate virtual
environment, with a C++ compiler available. Run the report's reproduction commands.
The package verifier uses the existing external interpreter for extraction tests;
the archive contains no environment or automatic dependency installer.

Stop for owner approval before another ML category. No commit, push or publication.

The package captured in externally advanced commit `5a3799b` is preserved verbatim
in `history/2026-10-27/`, with its original basename, checksum and metadata. The
current package corrects setup/glossary guidance and includes final continuation
evidence. Historical archives/sidecars remain outside the final source ZIP.
