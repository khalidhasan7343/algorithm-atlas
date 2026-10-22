# Phase 5 — Dynamic Programming checkpoints

Owner MD.Khalid Hasan explicitly approved Phase 4 on 2026-10-22 (Asia/Dhaka), then selected **the eleven listed topics only**. Phase 5 is authorized; its human review remains pending. No commit, push, or publication is authorized.

## Catalog scope and discrepancy

A12 has 13 original memberships, not 11. Implement Fibonacci, 0/1 Knapsack, Coin Change, Rod Cutting, LCS, LIS, Edit Distance, Matrix Chain Multiplication, Subset Sum, Palindrome Partitioning, and Kadane at their existing canonical paths. Preserve Bellman-Ford and Floyd-Warshall at their graph canonical paths as planned, outside this phase. Completion of this scope must not be called completion of all 13 memberships.

## Contracts resolved before implementation

Coin Change retains both formulations named by the catalog: `minimum_coins` (null/None if unreachable) and `count_combinations` (unordered, unbounded usage, duplicate denominations collapsed). Palindrome Partitioning computes minimum cuts, not enumeration. Subset Sum accepts nonnegative integers and returns existence. LCS/LIS return lengths. Edit costs are one. Rod Cutting must exactly fill the rod; unavailable lengths are None/x and impossibility is None/null. Kadane returns sum/start/end-exclusive with earliest-start then earliest-end ties and None/null for empty input, consistent with the divide/conquer topic on their shared numeric domain.

Python and C++ share documented finite numeric/resource domains. Fibonacci is limited to F(92); counting raises on any signed-64 table overflow. C++ Unicode APIs decode strict UTF-8 to Unicode scalar values; Python rejects surrogates. No normalization or grapheme segmentation.

## Batch order

1. Fibonacci, 0/1 Knapsack, Coin Change, Rod Cutting.
2. LCS, LIS, Edit Distance.
3. Matrix Chain Multiplication, Subset Sum, Palindrome Partitioning.
4. Kadane and integration.

Finish documentation, both implementations, independent-oracle tests and Python/C++17/C++20 validation before advancing each batch. Actual evidence will be appended below. Resume: Batch 1 implementation and tests.

## Batch 1 — actual algorithm gate

- fibonacci: `7 passed in 3.08s`; includes Python, C++17 and C++20.
- zero-one-knapsack: `7 passed in 3.32s`; includes Python, C++17 and C++20.
- coin-change: `7 passed in 3.00s`; includes Python, C++17 and C++20.
- rod-cutting: `7 passed in 3.02s`; includes Python, C++17 and C++20.

Catalog and generated-document checks follow this gate. Resume: Batch 2 after configuration passes.

Batch 1 configuration passed: catalog/local links, generated documents, and 224 infrastructure tests (2.19s). Batch 2 may proceed.

## Batch 2 — actual algorithm gate

- longest-common-subsequence: `10 passed in 4.13s`; includes Python, C++17 and C++20.
- longest-increasing-subsequence: `7 passed in 2.86s`; includes Python, C++17 and C++20.
- edit-distance: `10 passed in 4.18s`; includes Python, C++17 and C++20.

Catalog and generated-document checks follow this gate. Resume: Batch 3 after configuration passes.

Batch 2 configuration passed: catalog/local links, generated documents, and 224 infrastructure tests. Batch 3 may proceed.

## Batch 3 — actual algorithm gate

- matrix-chain-multiplication: `7 passed in 3.12s`; includes Python, C++17 and C++20.
- subset-sum: `7 passed in 2.80s`; includes Python, C++17 and C++20.
- palindrome-partitioning: `10 passed in 4.05s`; includes Python, C++17 and C++20.

Catalog and generated-document checks follow this gate. Resume: Batch 4 after configuration passes.

Batch 3 configuration passed: catalog/local links, generated documents, and 224 infrastructure tests. Batch 4 may proceed.

## Batch 4 — actual algorithm gate

- kadane: `8 passed in 3.20s`; includes Python, C++17 and C++20.

Catalog and generated-document checks follow this gate. Resume: final regression, examples, preservation, report and packaging, then owner review.

## Final regression and examples

Final DP runs: 37 Python passed (50 C++ cases deselected), 25 C++17 passed (37 Python cases deselected), and 25 C++20 passed (37 Python cases deselected). All 22 documented Python/C++20 examples matched exact outputs. Full repository: **1344 passed in 167.87s**, no failures/skips/timeouts. Prior 174 files are byte-identical, all 13 A12 memberships and all canonical identities preserved. Sanitizers, final report/configuration/tracked export and archive checks follow.

## Final configuration and tracking

C++20 ASan+UBSan with recovery disabled: **25 passed, 37 deselected in 20.55s**. Final configuration passed catalog/local links, generated docs, and **224 infrastructure tests in 2.36s**. Whitespace validation passed. All seven completion/review reports are nonempty and tracked; no required report is ignored. A clean export of the actual staged Git index passed catalog/generated-document/preservation validation. Staging was authorized for these integrity checks; no commit, push or publication occurred.

Archive CRC, exact source-byte/required-artifact checks, SHA-256 and extracted checks are run by `scripts/package_dynamic_programming_review.py`. Actual package counts and outcomes are saved in the external `.zip.verification.json` sidecar after packaging, avoiding a self-hash dependency. After successful packaging, **STOP for explicit owner review**. Phase 5 is awaiting-review; do not develop another category or mark it human-approved.
