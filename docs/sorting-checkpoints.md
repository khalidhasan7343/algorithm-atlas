# Sorting development checkpoints

The user approved Phase 0 and authorized **only the complete Sorting category** in Phase 1. Internal batches continue automatically after their checks pass. Searching and every other category require separate approval. No commits or pushes are authorized.

## Batch order and resume rules

| Batch | Algorithms | Current checkpoint |
| --- | --- | --- |
| 1 | Bubble Sort, Selection Sort, Insertion Sort, Merge Sort | Passed: 207 full-suite tests; catalog/links and generated docs valid. |
| 2 | Quick Sort, Heap Sort, Counting Sort, Radix Sort | Passed: 359 full-suite tests; catalog/links and generated docs valid. |
| 3 | Bucket Sort, Shell Sort, Tim Sort | Authorized next; Batch 2 gate passed. |

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
