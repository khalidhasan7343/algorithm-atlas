# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

The owner explicitly approved Phase 5 on 2026-10-22 (Asia/Dhaka) and authorized **Phase 6 — Greedy: four canonical topics only**. Batch 1: Activity Selection, Fractional Knapsack. Batch 2: Huffman Coding, Job Sequencing with Deadlines. Finish and test each [batch](docs/greedy-checkpoints.md) before continuing automatically. Preserve all earlier categories and review evidence.

A11 retains seven memberships. Dijkstra, Prim and Kruskal are graph algorithms that also use the Greedy paradigm; preserve their existing Graph canonical paths and statuses, add only conceptual references, and do not implement or duplicate them in Phase 6. Keep all 256 syllabus entries and 235 canonical topics. Use only schema-supported references.

Each new lesson needs the exact 25 sections, greedy-choice/exchange correctness, numeric/resource contracts, Python/C++17/C++20 tests and independent oracles. Record actual results, regenerate documentation, prepare GREEDY-REVIEW-REPORT.md and the full review ZIP/SHA-256, then STOP for explicit owner review. Do not mark Phase 6 human-approved, begin another category, commit, push or publish. Every later scope also requires owner approval at its completion checkpoint. Never set Git identity from the public email.

## Work and validation

- Keep all original syllabus items in the catalog, reuse canonical topics, and document meaningful variants.
- Planning READMEs are scope records, not completed algorithm lessons. Implemented lessons require the 25 sections in `docs/development.md`, Python/C++ code, examples, and meaningful tests.
- Use actual evidence for status changes. Keep the Dynamic Policy Optimization topic blocked until its intended reference is clarified; see `docs/terminology-decisions.md`.
- Regenerate index/progress documentation after catalog changes with `python scripts/generate_catalog_docs.py`. Preserve hand-written lessons.
- Run `python scripts/validate_catalog.py`, `python scripts/generate_catalog_docs.py --check`, and `python -m pytest --require-cpp` after relevant changes. Report failures, skips, and missing tools precisely.
- Keep secrets, virtual environments, generated binaries, model weights, and large datasets out of version control.

Use the local `.venv` when available. A configured workflow is not evidence that hosted GitHub Actions has run.
