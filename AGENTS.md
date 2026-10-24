# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

The owner officially approved completed Phase 10 on 2026-10-24 (Asia/Dhaka), satisfying the prerequisite for **combined Phase 11 — Number Theory and Phase 12 — Two Pointers & Sliding Window**. Phase 9 remains owner-approved. Implement only the seven A9 and three A10 canonicals in the four sequential stages in [locked scope](docs/number-theory-window-scope.md). Preserve prior implementations/history and 35 categories, 256 memberships and 235 canonicals.

Follow separate [Phase 11](docs/number-theory-checkpoints.md) and [Phase 12](docs/two-pointers-sliding-window-checkpoints.md) checkpoints, reports and ZIP/checksum/JSON packages in their established review folders. Finish both categories before presenting the combined review; their owner approvals remain independent and pending. Exact 25-section lessons and Python/C++17/C++20 tests/gates are required at each stage. No repeated Phase 10 approval request. After both packages pass integrity checks, STOP for explicit owner review. No Phase 13, commit, push or publication. Never set Git identity from public email.

## Work and validation

- Keep all original syllabus items in the catalog, reuse canonical topics, and document meaningful variants.
- Planning READMEs are scope records, not completed algorithm lessons. Implemented lessons require the 25 sections in `docs/development.md`, Python/C++ code, examples, and meaningful tests.
- Use actual evidence for status changes. Keep the Dynamic Policy Optimization topic blocked until its intended reference is clarified; see `docs/terminology-decisions.md`.
- Regenerate index/progress documentation after catalog changes with `python scripts/generate_catalog_docs.py`. Preserve hand-written lessons.
- Run `python scripts/validate_catalog.py`, `python scripts/generate_catalog_docs.py --check`, and `python -m pytest --require-cpp` after relevant changes. Report failures, skips, and missing tools precisely.
- Keep secrets, virtual environments, generated binaries, model weights, and large datasets out of version control.

Use the local `.venv` when available. A configured workflow is not evidence that hosted GitHub Actions has run.


## Review files and root organization

Future phase reports belong in `docs/reviews/<phase-name>/`; ZIPs, checksums and package JSON belong in `artifacts/review-packages/<phase-name>/`. Keep only essential project documentation, configuration and established source/infrastructure directories at the root. Update `development.completion_report`, live Markdown links, tracking checks and packaging paths whenever a report moves. Every completion report must exist, be nonempty, tracked and unignored.

The final review ZIP must contain the updated repository and required reports, excluding caches, virtual environments, secrets, binaries and unnecessary nested review archives/sidecars. Preserve genuine historical ZIPs and execution evidence; their internal snapshot paths/hashes remain historical. Do not force-add ignored artifacts. Existing phase-owner approval checkpoints remain mandatory; maintenance itself does not approve phases; the owner subsequently approved Phase 10 and authorized combined Phases 11 and 12 with separate owner checkpoints. Do not commit, push or publish without explicit owner authorization.
