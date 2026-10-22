# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

The owner explicitly approved Phase 6 on 2026-10-23 (Asia/Dhaka) and authorized **Phase 7 — Graph Algorithms only**, all fifteen A5 canonical topics. Follow the five sequential validated [batches](docs/graph-algorithms-checkpoints.md); finish documentation, Python/C++17/C++20 and repository checks before continuing automatically. Preserve previously approved implementations and genuine reports/evidence.

Keep 35 categories, 256 original memberships and 235 canonical topics. Complete Dijkstra/Prim/Kruskal and Bellman-Ford/Floyd-Warshall at their Graph canonical paths and update existing Greedy/DP cross-references without duplicates. Shared utilities must leave each algorithm independently understandable. Lessons require the exact 25 sections, graph/numeric/path/cycle contracts, correctness and meaningful independent/cross-algorithm tests.

After docs/reviews/graph-algorithms/GRAPH-ALGORITHMS-REVIEW-REPORT.md, the full review ZIP/SHA-256 and integrity checks, STOP for explicit owner review. Do not mark Phase 7 human-approved, begin another category, commit, push or publish. Every later scope also ends at an explicit owner review checkpoint. Never set Git identity from the public email.

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

The final review ZIP must contain the updated repository and required reports, excluding caches, virtual environments, secrets, binaries and unnecessary nested review archives/sidecars. Preserve genuine historical ZIPs and execution evidence; their internal snapshot paths/hashes remain historical. Do not force-add ignored artifacts. Existing phase-owner approval checkpoints remain mandatory; maintenance does not approve Phase 7 or authorize more algorithm work. Do not commit, push or publish without explicit owner authorization.
