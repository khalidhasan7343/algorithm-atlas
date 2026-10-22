# Algorithm Atlas working instructions

## Read before changing the project

Read `README.md`, `CONTRIBUTING.md`, `docs/progress.md`, and the relevant records in `catalog.yaml`. The project owner and maintainer is **MD.Khalid Hasan**; preserve the attribution and MIT licensing. The target repository is `https://github.com/khalidhasan7343/algorithm-atlas`.

## Mandatory phase checkpoint

**The owner confirms previous phases complete and explicitly authorizes
Phase 4 — Divide & Conquer only.** Preserve previously completed Sorting,
Searching, and Recursion & Backtracking work.

The authoritative A4 catalog has seven memberships: Merge Sort, Quick Sort,
Binary Search (three reused canonical topics), plus four new canonical topics.
The user's list counted six; preserve all seven and document the discrepancy.
Never duplicate the three existing implementations.

Batch 1: Maximum Subarray using Divide and Conquer; Karatsuba Multiplication.
Batch 2: Closest Pair of Points; Strassen's Matrix Multiplication.
Finish/test each batch before continuing automatically. Record actual results
in docs/divide-conquer-checkpoints.md; update catalog/progress/generated docs.
All new lessons need 25 sections, recurrence, correctness, numeric contracts,
Python/C++17/C++20 tests and independent expected values. Preserve prior code
unless a confirmed defect requires correction.

After completion create DIVIDE-CONQUER-REVIEW-REPORT.md, the requested review
ZIP and SHA-256; verify integrity/completeness, then STOP for explicit owner
review. Do not mark Phase 4 human-approved, start another category, commit,
push, or publish. User authorization supersedes previous phase wording.

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
