# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

The owner explicitly approved all previously completed work and authorized a **Phase 13 — B1 Regression completion audit** on **2026-10-28 (Asia/Dhaka)**. Retain the seven existing implementations; audit and fix only confirmed Regression defects under [the audit scope](docs/regression-audit-scope.md). Preserve approved Classification/DSA implementations, all historical evidence/packages and the pre-existing working-tree/staged changes. Inventory stays 35/256/235.

Python/numerical tests and exact 25-section lessons remain mandatory for ML, with C++ optional. DSA retains Python/C++ and both C++17/C++20. Follow [the audit checkpoint](docs/regression-audit-checkpoints.md). Prior owner approval is recorded separately from the **new Regression review, which remains pending**. Stop after the regenerated report and verified ZIP/checksum/JSON. No other category, commit, push or release. Never set Git identity from public email.

## Work and validation

- Keep all original syllabus items in the catalog, reuse canonical topics, and document meaningful variants.
- Planning READMEs are scope records, not completed algorithm lessons. Implemented lessons require the 25 sections in `docs/development.md`, track-required code, examples, and meaningful tests; see `docs/ml-development.md`.
- Use actual evidence for status changes. Keep the Dynamic Policy Optimization topic blocked until its intended reference is clarified; see `docs/terminology-decisions.md`.
- Regenerate index/progress documentation after catalog changes with `python scripts/generate_catalog_docs.py`. Preserve hand-written lessons.
- Run `python scripts/validate_catalog.py`, `python scripts/generate_catalog_docs.py --check`, and `python -m pytest --require-cpp` after relevant changes. Report failures, skips, and missing tools precisely.
- Keep secrets, virtual environments, generated binaries, model weights, and large datasets out of version control.

Use the local `.venv` when available. A configured workflow is not evidence that hosted GitHub Actions has run.


## Review files and root organization

Future phase reports belong in `docs/reviews/<phase-name>/`; ZIPs, checksums and package JSON belong in `artifacts/review-packages/<phase-name>/`. Keep only essential project documentation, configuration and established source/infrastructure directories at the root. Update `development.completion_report`, live Markdown links, tracking checks and packaging paths whenever a report moves. Every completion report must exist, be nonempty, tracked and unignored.

The final review ZIP must contain the updated repository and required reports, excluding caches, virtual environments, secrets, binaries and unnecessary nested review archives/sidecars. Preserve genuine historical ZIPs and execution evidence; their internal snapshot paths/hashes remain historical. Do not force-add ignored artifacts. Existing phase-owner approval checkpoints remain mandatory; maintenance itself does not approve phases; the owner subsequently approved Phase 10 and authorized combined Phases 11 and 12 with separate owner checkpoints. Do not commit, push or publish without explicit owner authorization.
