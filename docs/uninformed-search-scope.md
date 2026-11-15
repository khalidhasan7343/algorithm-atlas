# Phase27 C1 Uninformed Search Scope

The owner **MD.Khalid Hasan** approved the previous work (Phase26 final ML audit, whose `CONDITIONAL PASS` verdict is preserved unchanged) and authorized **Phase27 — C1 Uninformed Search** on **2026-11-14 Asia/Dhaka**. Evidence: [approval record](uninformed-search-evidence/approval-evidence.json) and the [verbatim request](uninformed-search-evidence/phase27-request.md).

## Inventory lock

| # | Syllabus entry | Canonical ID | Owner | Phase27 work |
| - | --- | --- | --- | --- |
| 1 | Breadth-First Search (BFS) | `breadth-first-search` | A5 | Reuse, link, integration tests and example; no new implementation |
| 2 | Depth-First Search (DFS) | `depth-first-search` | A5 | Reuse, link, integration tests and example; no new implementation |
| 3 | Depth-Limited Search | `depth-limited-search` | C1 | New canonical |
| 4 | Iterative Deepening DFS (IDDFS) | `iterative-deepening-dfs` | C1 | New canonical |
| 5 | Uniform Cost Search (UCS) | `uniform-cost-search` | C1 | New canonical |
| 6 | Bidirectional Search | `bidirectional-search` | C1 | New canonical (bidirectional BFS, unit costs) |

Repository inventory stays 35 categories, 256 syllabus memberships and 235 canonical topics. No canonical ID, path or category membership changes.

## Language policy

The repository track policy ([`scripts/track_policy.py`](../scripts/track_policy.py)) requires Python **and** C++ for non-ML tracks. Phase27 keeps that rule for AI: every new canonical has a Python implementation and tests, and a genuine C++ implementation tested under C++17 and C++20. NumPy is not needed; only the standard libraries are used.

## Batches

1. Shared BFS/DFS integration.
2. Depth-Limited Search and IDDFS.
3. Uniform Cost Search.
4. Bidirectional Search.
5. Integration, regression and packaging.

## Boundaries

- Do not modify A5 BFS, DFS or Dijkstra semantics, ownership or files.
- Preserve every prior approval, report, evidence file and package byte-for-byte, the DPO identity, path, four blocked statuses and remain-blocked decision.
- Generator/validator/track-policy changes are limited to recognizing an active AI phase, keeping post-ML approval text, and preserving the authored C1 guide.
- Deliver the [review report](reviews/uninformed-search/UNINFORMED-SEARCH-REVIEW-REPORT.md) and verified ZIP/SHA-256/JSON under `artifacts/review-packages/uninformed-search/`, then stop. Phase27 owner approval is pending. No C2, commit, push, tag, release or publication.
