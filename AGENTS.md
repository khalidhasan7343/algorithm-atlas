# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

**Phase 2 (Searching) is explicitly approved by the owner. Current authorization:
Phase 3 — Recursion & Backtracking category only.** Preserve approved Sorting
and Searching implementations, tests, and individual lessons.

Use catalog.yaml as authoritative for names, IDs, paths, and topic membership.
The internal batches are:

1. Permutations, Combinations, Power Set Generation.
2. N-Queens, Sudoku Solver, Rat in a Maze.
3. Graph Coloring, Hamiltonian Path, Subset Sum using Backtracking.

Complete and test each batch before starting the next. Record actual gates in
`docs/recursion-backtracking-checkpoints.md`, update catalog statuses honestly,
and regenerate docs. Define deterministic ordering, duplicates, mutation, invalid
inputs, and state restoration. Distinguish impossible problems from invalid data.

After all nine topics pass applicable checks, create
`RECURSION-BACKTRACKING-REVIEW-REPORT.md`, the requested review ZIP and SHA-256,
verify the package, then **STOP for explicit human review and approval**. Do not
mark Phase 3 human-approved. Graph Coloring/Hamiltonian Path are A3 topics;
no A5 Graph Algorithms or other category implementation is authorized.

At the end of every subsequent authorized phase or category scope, stop for explicit user review before developing beyond that scope. The user's latest explicit authorization controls these checkpoints.

Do not push, publish, or create commits on the maintainer's behalf without explicit authorization. Do not set Git identity from the public contact email.

## Work and validation

- Keep all original syllabus items in the catalog, reuse canonical topics, and document meaningful variants.
- Planning READMEs are scope records, not completed algorithm lessons. Implemented lessons require the 25 sections in `docs/development.md`, Python/C++ code, examples, and meaningful tests.
- Use actual evidence for status changes. Keep the Dynamic Policy Optimization topic blocked until its intended reference is clarified; see `docs/terminology-decisions.md`.
- Regenerate index/progress documentation after catalog changes with `python scripts/generate_catalog_docs.py`. Preserve hand-written lessons.
- Run `python scripts/validate_catalog.py`, `python scripts/generate_catalog_docs.py --check`, and `python -m pytest --require-cpp` after relevant changes. Report failures, skips, and missing tools precisely.
- Keep secrets, virtual environments, generated binaries, model weights, and large datasets out of version control.

Use the local `.venv` when available. A configured workflow is not evidence that hosted GitHub Actions has run.
