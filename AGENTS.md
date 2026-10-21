# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

**Phase 0 is approved. The current authorization is Phase 1 — Sorting category only.** The user approved all 11 sorting algorithms in three sequential internal batches:

**Current checkpoint: all 11 Sorting algorithms are implemented and tested; human review remains pending.** The latest authorized work is independent Sorting verification and confirmed corrections only, recorded in `SORTING-FINAL-AUDIT-REPORT.md`; `SORTING-REVIEW-REPORT.md` preserves the original handoff. After verification and packaging, stop for review. Do not start Searching without explicit user approval. Packaging this snapshot does not authorize another category.

1. Bubble Sort, Selection Sort, Insertion Sort, Merge Sort.
2. Quick Sort, Heap Sort, Counting Sort, Radix Sort.
3. Bucket Sort, Shell Sort, Tim Sort.

Finish and test each batch before starting the next. Fix failures, update `catalog.yaml`, regenerate `docs/progress.md`, and record actual results in `docs/sorting-checkpoints.md` after each batch. Continue automatically between these internal batches; no further approval is needed for them. Read the checkpoint and catalog development state before resuming interrupted work.

After all 11 sorting algorithms pass the full applicable suite and catalog/link checks, prepare a detailed completion report and **stop for user review**. Searching and every other category remain unauthorized. Do not infer approval for another category from passing tests or a next planned batch.

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
