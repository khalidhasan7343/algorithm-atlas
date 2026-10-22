# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

The owner explicitly approved Phase 7 and confirmed directory cleanup complete on 2026-10-23 (Asia/Dhaka). **Phase 8 — Tree Algorithms only** authorizes all fourteen A6 canonicals in five sequential validated [batches](docs/tree-algorithms-checkpoints.md). Preserve approved prior categories, historical reports/evidence, 35 categories, 256 memberships and 235 canonical topics. Fully implement deletion for AVL, Red-Black, B-Tree and B+ Tree, and verify structural invariants after every mutation in tests.

Finish each batch's 25-section lessons, Python/C++17/C++20 tests and repository gates before continuing automatically. No next category is authorized. Report: docs/reviews/tree-algorithms/TREE-ALGORITHMS-REVIEW-REPORT.md; ZIP/checksum/JSON: artifacts/review-packages/tree-algorithms/. After validation and package integrity checks, STOP for explicit owner review. Do not mark Phase 8 human-approved, commit, push or publish. Every later scope also ends at an explicit owner checkpoint. Never set Git identity from the public email.

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

The final review ZIP must contain the updated repository and required reports, excluding caches, virtual environments, secrets, binaries and unnecessary nested review archives/sidecars. Preserve genuine historical ZIPs and execution evidence; their internal snapshot paths/hashes remain historical. Do not force-add ignored artifacts. Existing phase-owner approval checkpoints remain mandatory; maintenance itself does not approve phases; the owner subsequently approved Phase 7 and authorized Phase 8. Do not commit, push or publish without explicit owner authorization.
