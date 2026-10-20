# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

The current checkpoint is **Phase 0 foundation, awaiting user review**. No algorithm implementations, including Bubble Sort, are authorized during Phase 0. Do not infer permission from a passing test suite or from the next planned batch.

Begin Phase 1 only after the user explicitly says:

> Phase 0 Approved. Start Phase 1.

At the end of every subsequent phase, stop for explicit user review and approval before developing the next phase. The user's latest explicit authorization controls these checkpoints. When authorized to transition, update the progress tracking, the generator's Phase 0 prose, and this checkpoint so future work resumes accurately.

Do not push, publish, or create commits on the maintainer's behalf without explicit authorization. Do not set Git identity from the public contact email.

## Work and validation

- Keep all original syllabus items in the catalog, reuse canonical topics, and document meaningful variants.
- Planning READMEs are scope records, not completed algorithm lessons. Implemented lessons require the 25 sections in `docs/development.md`, Python/C++ code, examples, and meaningful tests.
- Use actual evidence for status changes. Keep the Dynamic Policy Optimization topic blocked until its intended reference is clarified; see `docs/terminology-decisions.md`.
- Regenerate index/progress documentation after catalog changes with `python scripts/generate_catalog_docs.py`. Preserve hand-written lessons.
- Run `python scripts/validate_catalog.py`, `python scripts/generate_catalog_docs.py --check`, and `python -m pytest --require-cpp` after relevant changes. Report failures, skips, and missing tools precisely.
- Keep secrets, virtual environments, generated binaries, model weights, and large datasets out of version control.

Use the local `.venv` when available. A configured workflow is not evidence that hosted GitHub Actions has run.
