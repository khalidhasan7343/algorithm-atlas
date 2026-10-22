# Phase 6 — Greedy checkpoints

Owner MD.Khalid Hasan explicitly approved Phase 5 in this session on 2026-10-22 (Asia/Dhaka). The eleven DP topics were checked against the verified Phase 5 archive manifest; completion does not rely on owner approval as a test certificate. Phase 6 authorizes four Greedy-owned canonical topics only. No commit, push or publication is authorized. Phase 6 human review is pending.

## Classification and preserved scope

A11 already has seven memberships: Activity Selection, Huffman Coding, Fractional Knapsack, Job Sequencing with Deadlines, plus Kruskal, Prim and Dijkstra. Implement the four Greedy-owned topics at their existing paths. The three graph algorithms also use the Greedy paradigm, but their graph paths and all statuses remain unchanged and planned; do not implement or duplicate them here. Preserve 256 syllabus entries and 235 canonical topics. Existing `related_algorithms` supports conceptual references; add no schema fields or memberships.

## Contracts fixed before implementation

- Activity Selection: integer half-open intervals [start,finish), start<finish; choose maximum count, sorting by finish/start/original index, return original indices in selection order. Empty returns []; invalid/zero-duration intervals rejected. Times within +/-10^9; n<=10000.
- Fractional Knapsack: positive integer weights and nonnegative values (both <=10^6), n<=10000, integer capacity 0..10^9. Reject zero/negative weights and negative values. Descending exact ratio, original-index ties; zero-value items remain unselected. Return exact rational total and per-item fractions. No floating-point approximation supplies decisions or outputs.
- Huffman Coding: unique byte symbols 0..255 with integer frequencies 1..10^9. Heap key (frequency,minimum subtree byte,creation index); left edge 0/right edge 1. Single symbol uses 0, empty alphabet has no codes. Encode/decode byte messages; <=10000 message bytes and <=1000000 bits. Reject malformed/truncated streams and unknown symbols. Ordinary deterministic tree codes, not canonical Huffman codes.
- Job Sequencing: independent unit-duration jobs with integer deadline 0..10^9 and profit +/-10^9; n<=10000. Negative deadlines invalid, deadline zero unschedulable, nonpositive profit omitted. Sort by descending profit/original index; place at latest available slot. A bounded horizon and disjoint sets with rank/path compression handle sparse large deadlines. Return profit and fixed-horizon slot indices/nulls.

## Batch order

1. Activity Selection and Fractional Knapsack; finish lessons, Python/C++17/C++20 tests and repository validation before Batch 2.
2. Huffman Coding and Job Sequencing with Deadlines; then final regression, report/archive/checksum and STOP for explicit owner review.

Resume: Batch 1 implementation and tests. Actual results follow below.

## Batch 1 actual algorithm gate

- activity-selection: `7 passed in 3.90s`; includes Python, C++17 and C++20.
- fractional-knapsack: `7 passed in 2.93s`; includes Python, C++17 and C++20.

Next: catalog/generated/infrastructure validation, then Batch 2.

Batch 1 repository gate passed: catalog/local links, generated-document drift check and 236 infrastructure tests. Batch 2 may proceed.

## Batch 2 actual algorithm gate

- huffman-coding: `10 passed in 5.45s`; includes Python, C++17 and C++20.
- job-sequencing-with-deadlines: `9 passed in 4.40s`; includes Python, C++17 and C++20.

Next: catalog/generated/infrastructure validation, then final regression, review report and package; STOP for owner review.

Batch 2 repository gate passed catalog/local links, generated-document check and **236 infrastructure tests in 2.46s**. Preservation audit: **263 prior files byte-identical**, all 256/235 counts and graph paths/statuses preserved. Final regression and archive checks are in progress.

## Final regression and examples

Final Greedy runs: **13 Python passed**, **10 C++17 passed**, **10 C++20 passed**. Language marker deselections are not passes. All **8/8 documented examples** matched exact outputs. Full repository: **1389 passed in 174.60s**, no failures/errors/skips/timeouts. This includes all previously completed categories. Sanitizer, final report/configuration, clean tracked snapshot and archive checks follow.

## Final configuration, sanitizer and tracking

C++20 ASan+UBSan with recovery disabled: **10 passed, 13 deselected in 9.38s**. Final catalog/local-link and generated checks passed; infrastructure **236 passed in 2.54s**. Whitespace checks passed. All eight review reports are nonempty, tracked and not ignored. A clean export of the actual staged Git index passed catalog/generated-document/preservation checks. Phase 6 files were staged for the required tracking check; previous staged Phase 5 work is preserved. No commit, push or publication occurred.

The packager verifies required files, exact source bytes, safe paths, CRC, SHA-256 and extracted catalog/generated/preservation checks. Actual package counts/hash are saved in the external ZIP verification JSON sidecar after packaging, avoiding a self-hash dependency. On success, **STOP for explicit owner review**; Phase 6 remains awaiting-review. No Graph or other-category implementation is authorized.
