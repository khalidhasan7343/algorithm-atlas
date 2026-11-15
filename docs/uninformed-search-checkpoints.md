# Phase27 C1 Uninformed Search Checkpoints

Authorization: owner approval of previous work and Phase27 C1 authorization on 2026-11-14 Asia/Dhaka ([evidence](uninformed-search-evidence/approval-evidence.json)). The Phase26 `CONDITIONAL PASS` verdict is preserved. Phase27 owner approval is **pending**. Scope: [scope lock](uninformed-search-scope.md); contract: [conventions](uninformed-search-conventions.md).

## Starting state

| Item | Value |
| --- | --- |
| Branch / HEAD | `main` / `bd457cd8665c8e6357300749b9ce16205136a832` |
| Working tree | clean before Phase27 |
| Environment | Python 3.14.2 (`.venv`), pytest 9.1.1, PyYAML 6.0.3, NumPy 2.5.4, Apple clang 21.0.0 via `g++` (C++17 and C++20 available), macOS arm64 |
| Inventory | 35 categories, 256 memberships, 235 canonicals; 3962 hashed source files ([baseline](uninformed-search-evidence/baseline.json), [catalog snapshot](uninformed-search-evidence/catalog-baseline.yaml)) |
| Baseline regression | `python -m pytest --require-cpp -q -p no:cacheprovider` → **5222 passed** in 441.1 s, 0 failed, 0 skipped ([record](uninformed-search-evidence/baseline-full-suite-01.json)) |
| AI language policy | `scripts/track_policy.py`: non-ML tracks require Python and C++; Phase27 keeps that rule for AI |

## Batch gates

All commands were run from the repository root through `scripts/run_uninformed_search_validation.py`, which stores the output (`.txt`), command/timing record (`.json`) and JUnit XML in [the evidence folder](uninformed-search-evidence/).

| Batch | Scope | Command (after `python -m pytest -p no:cacheprovider --require-cpp -q`) | Result |
| --- | --- | --- | --- |
| 1 | Shared BFS/DFS integration | `dsa/graph-algorithms/breadth-first-search dsa/graph-algorithms/depth-first-search dsa/graph-algorithms/dijkstra artificial-intelligence/uninformed-search/tests` | 37 passed ([record](uninformed-search-evidence/batch1-shared-01.json)) |
| 2 | DLS and IDDFS | `artificial-intelligence/uninformed-search/depth-limited-search artificial-intelligence/uninformed-search/iterative-deepening-dfs` | 52 passed ([record](uninformed-search-evidence/batch2-dls-iddfs-01.json)) |
| 3 | UCS | `artificial-intelligence/uninformed-search/uniform-cost-search` | 36 passed ([record](uninformed-search-evidence/batch3-ucs-01.json)) |
| 4 | Bidirectional search | `artificial-intelligence/uninformed-search/bidirectional-search` | 27 passed ([record](uninformed-search-evidence/batch4-bidirectional-01.json)) |
| 5 | Integration, regression, packaging | see the final section | passed |

## Development findings fixed before the gates

1. Dataclasses fail when a module is loaded by file path with postponed annotations (no `sys.modules` entry); `SearchResult` became a small explicit immutable class.
2. Bidirectional ties always chose forward, so a chain degenerated into one-sided BFS; ties now pick the shallower side, then forward.
3. A placeholder "first collision" test was replaced by a real counterexample found by exhaustive search (edges `0→1, 1→3, 0→3`), on which a node-alternating variant returns length 2; the canonical returns 1.
4. CLI tokens were limited to 18 digits and ASCII whitespace so Python and C++ accept exactly the same inputs.
5. Generator: switching the active track to AI hid the ML B9–B13 category overviews that were gated on the final-audit mode; a `post_ml` gate restores them byte-for-byte, and ML pages differ only in their current-checkpoint paragraph.
6. Generator: the first batch 5 infrastructure run failed `tests/test_generate_catalog_docs.py::test_combined_progress_displays_independent_reports_and_approvals` (1 failed, 316 passed; [record](uninformed-search-evidence/c1-policy-01.json)) because the new AI progress branch overrode legacy DSA scopes. The AI branch now excludes legacy scopes exactly as the ML branch does; rerun 317 passed ([record](uninformed-search-evidence/c1-policy-02.json)).

## Batch 5 final validation

| Label | Command | Result |
| --- | --- | --- |
| catalog | `python scripts/validate_catalog.py` | passed, 444 Markdown files, 5211 links |
| generated | `python scripts/generate_catalog_docs.py --check` | 77 pages, 0 changes |
| scope | `python scripts/verify_uninformed_search_scope.py` | passed; 3929 protected, 33 allowed changes; report tracked and unignored |
| examples | `python scripts/verify_uninformed_search_examples.py` | 6 deterministic examples match lessons |
| c1-targeted | `python -m pytest -p no:cacheprovider --require-cpp -q artificial-intelligence/uninformed-search dsa/graph-algorithms/{breadth-first-search,depth-first-search,dijkstra}` | 152 passed |
| c1-policy | `python -m pytest -p no:cacheprovider -q tests/test_c1_language_and_scope_policy.py tests/test_track_policy.py tests/test_generate_catalog_docs.py tests/test_validate_catalog.py` | 317 passed (run 02; run 01 had 1 failure, finding 6) |
| full-suite | `python -m pytest --require-cpp -q -p no:cacheprovider` | **5363 passed**, 0 failed, 0 skipped, 458.4 s |

**Packaging attempt 1 (2026-11-15 22:04 Asia/Dhaka) failed its final integrity check.** All extracted-copy checks passed (including 5363 passed from the extracted ZIP), but `artificial-intelligence/uninformed-search/bidirectional-search/cpp/solution.cpp` was reformatted in the working tree after the freeze (IDE format-on-save; formatting only, 27 tests still passed under C++17/C++20). On the owner's instruction the archived bytes were restored (hash matches the frozen manifest), the failed ZIP/SHA-256/JSON from that attempt were removed, and the package was rebuilt.

Records are in [the evidence folder](uninformed-search-evidence/); [final-results.json](uninformed-search-evidence/final-results.json) collects the latest record of each label. The package is produced by `python scripts/package_uninformed_search_review.py`, which also re-runs validation and the full suite from the extracted ZIP. Phase27 owner approval is pending; do not start C2.
