# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

The owner **MD.Khalid Hasan** explicitly approved the verified Phase25 B13 handoff on **2026-11-01 Asia/Dhaka** and authorized **Phase26 — Machine Learning B1–B13 Final Comprehensive Audit**. This is audit/stabilization only:seven workstreams;no new category or canonical. See [scope](docs/ml-final-audit-scope.md) and [checkpoints](docs/ml-final-audit-checkpoints.md). Preserve inventory35 categories/256 memberships/235 canonicals,all prior approvals,historical reports/evidence/packages,DSA source and existing staged work. Preserve DPO identity,path,four blocked statuses,research and owner-approved remain-blocked decision.

Independently inspect every implemented ML canonical,math,oracles/tests,exact25-section lessons,numerics,resources,security,dependencies,CI and shared ownership. Make only minimal confirmed in-scope fixes;record reproductions and rerun affected checks. Request owner input before altering canonical identity,approved mathematical scope,public API contracts or blocker decisions. ML Python/NumPy mandatory,C++ optional;DSA Python/C++17/C++20 mandatory. No downloads or pretrained frameworks. Deliver tracked36-part report and verified ZIP/checksum/JSON,then STOP. **Phase26 audit and final B Track owner approval pending.** No C1,nextphase,commit,push,tag,release or publication. Never set Git identity from public email.


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
