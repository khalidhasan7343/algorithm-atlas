# Phase 16 — Clustering checkpoints

[Scope lock](clustering-scope.md). Previous phases including the latest Phase 15
package are explicitly owner-approved. Current Phase 16 review is **pending**.

## Discovery and baseline

Clean main at HEAD 4869db2a868151f08c560603dc6ec3f7aa91c3a9; exact environment,
Git status/index and pre-existing hashes are in [baseline](clustering-evidence/baseline.json).
The owner advanced the repository after the previous handoff. No cleanup/reset,
identity change, dependency installation or rewrite of approved implementations.
All eight B4 records start planned. Current commands preserve numbered attempts,
including failures, under clustering-evidence rather than overwriting old evidence.

## Internal stages

1. K-Means / Agglomerative — **24 passed in 0.78s**, full lessons/examples passed.
2. DIANA / DBSCAN — **21 passed in 0.76s**, full lessons/examples passed.
3. HDBSCAN / Mean Shift — **24 passed in 0.75s**, full lessons/examples passed.
4. GMM / Spectral — **29 passed in 0.82s**, full lessons/examples passed.

## Final checkpoint

Full required-C++ suite, prior B1/B2/B3 gates, mathematical markers, negative
validator tests, generated docs, examples and actual ZIP extraction will be
recorded before handoff. Stop after the tracked completion report and verified
ZIP/checksum/JSON for explicit owner review. No Phase 17 or publication.

## Final local gates

Combined B4: **206 passed**. Overlapping selections: numerical **21 passed /
185 deselected**, oracle **22 passed / 184 deselected**, reference **23 passed /
183 deselected**. A separate ten-case HDBSCAN reference audit matched all partitions
and membership strengths within 2.6e-15; those cases are not pytest counts.
All eight examples/equivalent CLIs (16 executions) and eight invalid CLI checks pass.
The final required-C++ full run passed **3,141 tests**, zero failures/errors/skips:
B4 206, B1 281, B2 398, B3 253,
DSA 1,687 (Python/shared 1,149; C++17 269; C++20 269), infrastructure 316.
[Matrix](clustering-evidence/test-matrix.json) and [actual commands](clustering-evidence/final-results.json)
retain evidence. Every named negative-validation requirement is confirmed by JUnit.
Catalog/link, 146 generated pages and exact eight 25-section lessons pass. All
2,020 protected pre-existing files remain byte-identical. Initial tie-fixture failure
and the resolved sklearn copy-default warnings are retained, not hidden. No confirmed
solver defect required repair. Actual extracted-package checks are in the external
JSON after ZIP creation. Hosted CI/other platforms remain unverified. Stop for
owner review; Phase 16 approval remains **pending**.
