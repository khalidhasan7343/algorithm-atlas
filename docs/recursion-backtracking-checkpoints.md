# Recursion & Backtracking checkpoints

The owner explicitly approved Phase 2 (Searching) and authorized **Phase 3 —
Recursion & Backtracking only**. Sorting and Searching sources/tests/lessons
must remain unchanged. Names, IDs, paths, and membership come from catalog.yaml.

## Internal gates

1. Permutations; Combinations; Power Set Generation.
2. N-Queens; Sudoku Solver; Rat in a Maze.
3. Graph Coloring; Hamiltonian Path; Subset Sum using Backtracking.

Complete and test each batch before starting the next. Save actual results and
update the catalog/progress after each gate. Graph Coloring and Hamiltonian Path
are the A3 backtracking topics; no A5 Graph Algorithms work is authorized.

## Initial checkpoint

Batch 1 is in progress. No Phase 3 batch is yet marked complete. Positional
selection and deterministic DFS ordering are explicit contracts; repeated input
values can produce repeated output rows. Caller inputs are never intentionally
modified. Errors and empty/impossible outputs must be distinguished.

## Final stop

After all three gates, prepare docs/reviews/recursion-backtracking/RECURSION-BACKTRACKING-REVIEW-REPORT.md and
artifacts/review-packages/recursion-backtracking/algorithm-atlas-recursion-backtracking-review.zip with its SHA-256 checksum.
Verify integrity and completeness, then STOP for explicit owner review.
No Phase 3 human approval, other-category work, commit, push, or publication
is authorized by passing tests.

## Initial repository defect

The first catalog gate found five stale links to three absent historical reports: docs/reviews/sorting/SORTING-REVIEW-REPORT.md, docs/reviews/sorting/SORTING-FINAL-AUDIT-REPORT.md, SEARCHING-REVIEW-REPORT.md. Those files were absent from the clean starting checkout and were not recreated or represented as original reports. The initial handoff recorded that absence; the recovery checkpoint below supersedes it. Original failed transcript: `recursion-backtracking-evidence/initial-missing-historical-reports.txt`. Approved implementations, tests, and individual lessons remain unchanged.

## Batch 1: validated

- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/permutations/tests` — 24 passed in 2.22s; 2.368 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/combinations/tests` — 28 passed in 2.02s; 2.13 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/power-set-generation/tests` — 24 passed in 1.78s; 1.896 seconds.
- `python scripts/validate_catalog.py` — exit 0; 0.42 seconds.
- `python scripts/generate_catalog_docs.py --check` — exit 0; 0.171 seconds.
- `python -m pytest -q --require-cpp` — 1148 passed in 86.37s (0:01:26); 86.492 seconds.

Evidence: `recursion-backtracking-evidence/batch1-results.json` and matching transcripts.

Resume: Batch 2 only; earlier batches passed their gate.

## Batch 2: validated

- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/n-queens/tests` — 8 passed in 3.14s; 3.274 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/sudoku-solver/tests` — 11 passed in 3.98s; 4.09 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/rat-in-a-maze/tests` — 7 passed in 3.06s; 3.169 seconds.
- `python scripts/validate_catalog.py` — exit 0; 0.401 seconds.
- `python scripts/generate_catalog_docs.py --check` — exit 0; 0.167 seconds.
- `python -m pytest -q --require-cpp` — 1174 passed in 94.27s (0:01:34); 94.402 seconds.

Evidence: `recursion-backtracking-evidence/batch2-results.json` and matching transcripts.

Resume: Batch 3 only; earlier batches passed their gate.

## Batch 3: validated

- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/graph-coloring/tests` — 8 passed in 2.48s; 2.626 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/hamiltonian-path/tests` — 7 passed in 2.33s; 2.441 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking/subset-sum-backtracking/tests` — 8 passed in 2.18s; 2.293 seconds.
- `python scripts/validate_catalog.py` — exit 0; 0.398 seconds.
- `python scripts/generate_catalog_docs.py --check` — exit 0; 0.169 seconds.

Evidence: `recursion-backtracking-evidence/batch3-results.json` and matching transcripts.

Resume: final comprehensive checks, report, package, then STOP for owner review.

## Final implementation and test checkpoint

- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking -m 'not cpp'` — 87 passed, 38 deselected in 2.04s; 2.157 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking -m cpp --cpp-standard=c++17` — 19 passed, 87 deselected in 10.66s; 10.774 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking -m cpp --cpp-standard=c++20` — 19 passed, 87 deselected in 12.21s; 12.329 seconds.
- `python -m pytest -q --require-cpp tests` — 200 passed in 2.09s; 2.209 seconds.
- `python -m pytest -q --require-cpp` — 1197 passed in 100.19s (0:01:40); 100.327 seconds.
- `python scripts/validate_catalog.py` — exit 0; 0.421 seconds.
- `python scripts/generate_catalog_docs.py --check` — exit 0; 0.172 seconds.

Sanitizers: 19 passed, 87 deselected in 16.29s. All 18 documented Python/C++20 examples matched exact output. Scope verification preserves 87 approved files and all catalog identities/out-of-scope records.

All nine algorithms are implemented/tested; owner review is pending. See [review report](reviews/recursion-backtracking/RECURSION-BACKTRACKING-REVIEW-REPORT.md). Finish package integrity/checksum checks, then STOP; no next category, commit, push, or publication.

## Review handoff boundary

Final configuration gate: catalog and generated docs passed; 200 infrastructure cases passed in 2.73s. Working-tree whitespace validation passed. Implementation and tests are frozen for review. The package builder verifies CRC, required payload, exact bytes, extracted catalog/docs, and checksum; actual package results are recorded in the external verification sidecar. After that succeeds the only next action is owner review, not another category or a commit/push.

## Restored reports and renewed Phase 3 verification

The owner requested the missing reports, and all three originals were recovered.
The five original documentation links now resolve again. The refreshed Phase 3
report/archive includes these reports. No approved Sorting/Searching source,
test, or individual lesson was changed. The nine Phase 3 implementations remain
in their catalog paths; final revalidation evidence is retained under
`recursion-backtracking-evidence/revalidation/`. Phase 3 remains awaiting review.

## Renewed final gate — passed

- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking -m 'not cpp'` — 87 passed, 38 deselected in 2.25s; 2.432 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking -m cpp --cpp-standard=c++17` — 19 passed, 87 deselected in 12.34s; 12.453 seconds.
- `python -m pytest -q --require-cpp dsa/recursion-and-backtracking -m cpp --cpp-standard=c++20` — 19 passed, 87 deselected in 13.61s; 13.725 seconds.
- `python -m pytest -q --require-cpp tests` — 200 passed in 2.07s; 2.208 seconds.
- `python -m pytest -q --require-cpp` — 1197 passed in 100.12s (0:01:40); 100.244 seconds.
- `python scripts/validate_catalog.py` — exit 0; 0.414 seconds.
- `python scripts/generate_catalog_docs.py --check` — exit 0; 0.194 seconds.

Sanitizers: 19 passed, 87 deselected in 16.78s. All 18 documented examples matched output. All nine lessons/sources/test layouts passed the deliverable audit. No algorithm defect was found and no algorithm source was changed. All 87 approved Sorting/Searching files remain unchanged.

Report/package refresh includes the three recovered original reports. After verified packaging, STOP for owner review; no other category, commit, push, publication, or human-approval flag.

Renewed configuration gate passed: catalog/local links and generated docs, plus 200 passed in 2.04s. Implementation and test evidence is complete. Archive verification results are recorded in the refreshed ZIP verification sidecar; the only development handoff after successful packaging is owner review.
