# Sorting development checkpoints

The user approved Phase 0 and authorized **only the complete Sorting category** in Phase 1. Internal batches continue automatically after their checks pass. Searching and every other category require separate approval. No commits or pushes are authorized.

## Batch order and resume rules

| Batch | Algorithms | Current checkpoint |
| --- | --- | --- |
| 1 | Bubble Sort, Selection Sort, Insertion Sort, Merge Sort | Passed: 207 full-suite tests; catalog/links and generated docs valid. |
| 2 | Quick Sort, Heap Sort, Counting Sort, Radix Sort | Passed: 359 full-suite tests; catalog/links and generated docs valid. |
| 3 | Bucket Sort, Shell Sort, Tim Sort | Passed: 655 full-suite tests; all 11 sorts complete, awaiting user review. |

Read the `development` block and individual statuses in [catalog.yaml](../catalog.yaml) before resuming. Test any unfinished current-batch work before advancing. A saved checkpoint records the exact commands and actual outcomes, remaining work, and next authorized batch. `tested` records evidence; `reviewed` requires human review and will not be assigned automatically.

## Initial checkpoint

- Scope: 11 sorting algorithms; no implementations outside `dsa/sorting/`.
- Active work: Batch 1 documentation, Python/C++ implementations, and tests.
- Baseline infrastructure: 79 previously passing tests; fresh batch results will be recorded below when executed.
- Current blockers: none for Sorting. Dynamic Policy Optimization remains a separate blocked future topic.
- Next action: complete Batch 1, execute its Python/C++ tests, validate the catalog and relative links, and save the results before starting Batch 2.

[Progress](progress.md) · [Development standards](development.md) · [Sorting](../dsa/sorting/README.md)

## Batch 1 checkpoint — complete and validated

Completed Bubble Sort, Selection Sort, Insertion Sort, and Merge Sort. Each has a 25-section lesson, reusable Python/C++ API, runnable CLI, Python tests, and compiled/executed C++17/C++20 tests. No human `reviewed` status is assigned. Library functions return new containers; their docs distinguish core workspace from returned-copy memory. Stability and Selection Sort's instability are explicitly tested.

Commands and actual results:

```text
.venv/bin/python -m pytest --require-cpp
207 passed in 10.88s; 0 failures, 0 skips

.venv/bin/python scripts/validate_catalog.py
Passed: 35 categories, 256 syllabus entries, 235 canonical topics,
293 Markdown files, 3,241 local links; zero errors

.venv/bin/python scripts/generate_catalog_docs.py --check
273 generated pages checked; zero drift
```

The full suite includes 126 Batch 1 algorithm test cases and 81 repository checks. Dedicated runs also passed: Bubble/Selection 72, Insertion 34, Merge 20. Many C++ driver cases run inside each collected pytest test; the totals above count pytest cases, not every generated input.

Catalog completion: **4 of 11 sorting algorithms**, **4 of 235 canonical topics**. Remaining Sorting work: Quick, Heap, Counting, Radix, Bucket, Shell, Tim. The Batch 1 gate is passed; resume with Batch 2 automatically. No other category is authorized.

## Batch 2 checkpoint — complete and validated

Completed Quick Sort, Heap Sort, Counting Sort, and Radix Sort after the saved Batch 1 gate. Each has all 25 documentation sections, working Python/C++ APIs and CLIs, and Python plus executed C++17/C++20 tests. Counting Sort's default range limit and Radix Sort's signed-width differences are explicit contracts rather than hidden fallbacks. Quick Sort bounds recursion without claiming a worst-case runtime guarantee; Heap Sort uses iterative sift-down.

```text
.venv/bin/python -m pytest --require-cpp
359 passed in 25.82s; 0 failures, 0 skips

.venv/bin/python scripts/validate_catalog.py
Passed: 35 categories, 256 syllabus entries, 235 canonical topics,
293 Markdown files, 3,267 local links; zero errors

.venv/bin/python scripts/generate_catalog_docs.py --check
269 generated pages checked; zero drift
```

The full suite includes 278 sorting cases plus 81 infrastructure cases. Dedicated Batch 2 results: Quick 34, Heap 22, Counting 52, Radix 44. C++ drivers additionally check many generated vectors inside their collected test cases. An independent Quick Sort audit exercised 15,755 exhaustive Python inputs and found no discrepancy; this is additional evidence and is not included in the pytest totals.

Catalog completion: **8 of 11 sorting algorithms**, **8 of 235 canonical topics**. Remaining Sorting work: Bucket, Shell, Tim. The Batch 2 gate is passed; resume with Batch 3 automatically. No searching or other category work is authorized.

## Batch 3 and final Sorting checkpoint — complete, awaiting review

Completed Bucket Sort, Shell Sort, and Tim Sort. Each has all 25 required lesson sections, reusable Python/C++ implementations, runnable CLIs, and comprehensive Python plus C++17/C++20 tests. Tim Sort includes natural runs, binary insertion, corrected four-run stack collapse, and actual galloping; its educational simplifications are documented. Bucket Sort's finite `[0, 1]` domain and Shell Sort's Knuth gap sequence are explicit.

Fresh full validation on 2026-10-21, before preparing the external review package:

```text
.venv/bin/python -m pytest --require-cpp
655 passed in 37.54s; 0 failures, 0 skips

.venv/bin/python scripts/validate_catalog.py
Passed: 35 categories, 256 syllabus entries, 235 canonical topics;
zero errors. Final packaging-document counts are in SORTING-REVIEW-REPORT.md.

.venv/bin/python scripts/generate_catalog_docs.py --check
266 generated pages checked; zero drift
```

The full suite includes **480 Sorting cases** and **175 infrastructure cases**, including checkpoint metadata validation. Every sorting algorithm contributes four C++ pytest cases: API and CLI checks under each of C++17 and C++20. Seeded/exhaustive driver inputs inside those cases are not counted as extra pytest cases. Dedicated Batch 3 runs passed Bucket 110, Shell 23, and Tim 69 tests.

The earlier implementation audit also passed all 24 selected C++20 cases with AddressSanitizer and UndefinedBehaviorSanitizer enabled, with no diagnostics. Independent Tim Sort checks exercised stability, gallop bounds, and pending-run stack invariants; these additional audit inputs are separate from the pytest totals.

Catalog completion: **11 of 11 Sorting algorithms**, **11 of 235 canonical topics**. **No Sorting implementation remains unfinished.** No automatic human `reviewed` status has been assigned. Searching and every other category remain outside the approved implementation scope.

**Resume action: wait for the user's review and explicit approval.** The external review handoff is [docs/reviews/sorting/SORTING-REVIEW-REPORT.md](reviews/sorting/SORTING-REVIEW-REPORT.md). No further implementation, commit, or push is authorized by this checkpoint.

## Final independent verification checkpoint — awaiting human review

The user authorized a Sorting-only independent audit and confirmed corrections.
The original 11 suites ran separately first: 480 passed in total, no failures,
skips, or timeouts. Review found one documentation mismatch: Bubble's README
named `from_chars` while its C++ parser uses `stoll`. The description is corrected;
all 22 implementation files remain unchanged from the baseline commit.

The independent suite adds 76 protective cases: exhaustive oracles, seed 20261021,
integer boundaries, stability, Quick's adversary/recursion, Tim's subrange
gallops/run-stack invariants, documented dry runs, and malformed CLIs.

```text
Sorting Python:       488 passed, 68 deselected in 5.75s
Sorting C++17:         34 passed, 488 deselected in 18.33s
Sorting C++20:         34 passed, 488 deselected in 21.21s
Infrastructure:       175 passed in 2.03s
Full repository:      731 passed in 41.19s
Selected ASan/UBSan:   14 passed, 117 deselected in 13.48s (C++20)
Catalog/local links:  passed
Generated docs:       266 pages checked, zero drift
```

Every bounded command completed within 120 seconds. No failures, skips, or
sanitizer diagnostics occurred. Hosted CI was not run. `tested` is not human
`reviewed` status. See the [final audit report](reviews/sorting/SORTING-FINAL-AUDIT-REPORT.md)
and [execution evidence](audit-evidence/README.md). The final external package is
`artifacts/review-packages/sorting/algorithm-atlas-sorting-final-review.zip`.

**Resume action: STOP and wait for explicit human review and approval.** No
Searching, other-category implementation, commit, push, or publication is authorized.
