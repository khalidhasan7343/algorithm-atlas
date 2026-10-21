# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

**Phase 1 (Sorting) has been reviewed and approved by the repository owner. Current authorization: Phase 2 — Searching category only.** Preserve all Sorting implementations and tests.

**Current checkpoint: all six Searching algorithms are implemented and tested;
Phase 2 is awaiting owner review.** The full suite passed 1,059 tests. See
`SEARCHING-REVIEW-REPORT.md` and `docs/searching-checkpoints.md`. Finish the review
package checks, then STOP. Do not begin another category without explicit approval.

The approved internal batches are:

1. Linear Search, Binary Search, Jump Search.
2. Interpolation Search, Exponential Search, Ternary Search.

Finish and test Batch 1 before implementing Batch 2; continue automatically after validation passes. Save actual results in `docs/searching-checkpoints.md`, update `catalog.yaml`, and regenerate documentation after each batch. Read that checkpoint before resuming interrupted work.

All searches must define first/any-match semantics, test duplicates and missing targets, and document ordering requirements. Sorted APIs must distinguish validation cost from search cost. Check C++ index/overflow boundaries, interpolation equal endpoints and division, exponential expansion, and the intended Ternary Search setting.

After all six searches pass the applicable suite and catalog/link checks, prepare `SEARCHING-REVIEW-REPORT.md` and `algorithm-atlas-searching-review.zip`, then **stop for explicit human review and approval**. No other category is authorized. Sorting approval is recorded in the Searching checkpoint; historical Sorting reports remain historical evidence.

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
