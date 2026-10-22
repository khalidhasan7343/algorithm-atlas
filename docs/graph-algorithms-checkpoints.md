# Phase 7 — Graph Algorithms checkpoints

MD.Khalid Hasan explicitly approved Phase 6 on 2026-10-23 (Asia/Dhaka) and authorized all fifteen A5 canonical topics. The four Greedy implementations match the verified Phase 6 review manifest; owner approval is separate from test certification. Preserve prior implementations and historical reports. No commit, push or publication is authorized. Stop after the Phase 7 report, full review ZIP and SHA-256 for explicit owner review.

## Exact scope and batch order

1. BFS, DFS, Union-Find, Topological Sorting.
2. Dijkstra, Bellman-Ford, Floyd-Warshall.
3. Kruskal and Prim.
4. Tarjan SCC, Kosaraju SCC, Bridges Detection, Articulation Points.
5. A* and Johnson; final cross-algorithm matrix and regression.

A5 has exactly fifteen original memberships at existing canonical paths; do not change 35/256/235 totals. Complete documentation, Python/C++17/C++20 tests and catalog/generated checks before each next batch. Continue automatically between these batches.

## Shared conventions established before Batch 1

See [graph conventions](graph-conventions.md). Zero-based vertices; each input edge has its original-position identity. Unweighted edge pairs and weighted edge triples; adjacency preserves input order. Undirected graphs add reverse arcs with the same identity. Parallel edges and self-loops are supported where meaningful. Empty graphs are valid; source-based empty graphs require None/null (-1 in CLI). Invalid dimensions/references/flags/types are rejected. Traversals are deterministic; unreachable distances are None/null, negative-cycle-affected paths are the string -inf. Sources/paths and algorithm-specific bounds are explicit.

General cap: V<=1000, E<=10000. Floyd/Johnson cap V<=100. Weighted bounds are +/-10^6 except Dijkstra, which supports 0..10^12 to accept Johnson reweighting. Bellman-Ford in-place intermediates fit signed-64 under V*E*10^6. Floyd clamps internal negative values at -10^12, below any finite simple-path bound, then labels every affected pair -inf. A* requires nonnegative weights and nonnegative heuristic values with h(goal)=0; admissibility is a caller guarantee for optimal early goal termination, not silently assumed for arbitrary heuristics. Reopening is supported.

Canonical Graph implementations serve Greedy Dijkstra/Prim/Kruskal and DP Bellman-Ford/Floyd references; category navigation/status prose will update while historical Phase 5/6 approval scope stays separate.

Initial checkpoint before implementation: Batch 1 pending. The completed gates are recorded below.

## Batch 1 algorithm gate

- `breadth-first-search`: 10 passed in 5.56s.
- `depth-first-search`: 10 passed in 4.16s.
- `union-find`: 10 passed in 4.46s.
- `topological-sorting`: 10 passed in 4.15s.

Actual commands and outputs: [batch 1 results](graph-algorithms-evidence/batch1-results.json). Repository gates are recorded below; no next category is authorized after Batch 5.

Batch 1 repository gate: catalog and generated docs passed; 244 infrastructure tests passed. Initial failures were catalog status-update quoting and a missing seven-membership phrase; corrected without weakening checks. Failure logs are retained. Batch 2 began after this gate.

## Batch 2 algorithm gate

- `dijkstra`: 10 passed in 4.31s.
- `bellman-ford`: 10 passed in 4.41s.
- `floyd-warshall`: 10 passed in 4.65s.

Actual commands and outputs: [batch 2 results](graph-algorithms-evidence/batch2-results.json). Repository gates are recorded below; no next category is authorized after Batch 5.

Batch 2 repository gate: catalog/generated checks and 244 infrastructure tests passed. The three shortest-path cross comparisons each passed 60 seed-70909 cases with independent path-enumeration expectations. Batch 3 began after this gate.

## Batch 3 algorithm gate

- `kruskal`: 10 passed in 5.15s.
- `prim`: 10 passed in 4.91s.

Actual commands and outputs: [batch 3 results](graph-algorithms-evidence/batch3-results.json). Repository gates are recorded below; no next category is authorized after Batch 5.

Batch 3 repository gate: catalog/generated checks and 244 infrastructure tests passed. Prim/Kruskal and brute-force forest expectations agreed on 60 seed-70909 graphs, including negative weights and disconnected components. Batch 4 began after this gate.

## Batch 4 algorithm gate

- `tarjan-strongly-connected-components`: 10 passed in 4.63s.
- `kosaraju-strongly-connected-components`: 10 passed in 4.49s.
- `bridges-detection`: 10 passed in 4.60s.
- `articulation-points`: 10 passed in 4.31s.

Actual commands and outputs: [batch 4 results](graph-algorithms-evidence/batch4-results.json). Repository gates are recorded below; no next category is authorized after Batch 5.

Batch 4 repository gate: catalog/generated checks and 244 infrastructure tests passed. SCC normalization and independent removal oracles each passed 60 seed-70909 comparisons. All four structural implementations also passed 208 independent vectors per language configuration and 1000-vertex iterative boundaries. Batch 5 began after this gate.

## Batch 5 algorithm gate

- `a-star-search`: 10 passed in 4.64s.
- `johnson`: 10 passed in 4.85s.

Actual commands and outputs: [batch 5 results](graph-algorithms-evidence/batch5-results.json). Repository gates are recorded below; no next category is authorized after Batch 5.


## Final regression and review checkpoint

All fifteen Graph topics and five batches are complete/tested locally. Phase 7 is awaiting independent owner review, not human-approved. `.venv/bin/python scripts/run_graph_algorithms_validation.py --stage final` recorded:

- `python`: 61 passed, 90 deselected in 1.27s.
- `cpp17`: 45 passed, 61 deselected in 27.83s.
- `cpp20`: 45 passed, 61 deselected in 32.43s.
- `full-suite`: 1548 passed in 227.75s (0:03:47).

The full suite includes Sorting, Searching, Recursion & Backtracking, Divide & Conquer, Dynamic Programming, Greedy and Graph, plus infrastructure tests. No skips, failures, missing compiler or timeout occurred. Final Graph suites also check exact Python/C++ deterministic outputs against the same independently expected vectors. Matrix seed 70909: nine comparisons × 60 cases, zero failures. Documented examples: 30/30 exact. C++20 ASan+UBSan with recovery disabled: 45 passed. Prior protected files: 273 byte-identical; 35/256/235 inventory unchanged.

Catalog/generated documentation and report tracking/export checks finish the review-package gate. See [review report](reviews/graph-algorithms/GRAPH-ALGORITHMS-REVIEW-REPORT.md), [execution results](graph-algorithms-evidence/final-results.json), [matrix](graph-algorithms-evidence/cross-matrix-batch5.json) and [tracking record](graph-algorithms-evidence/tracking-results.json).

**STOP: wait for MD.Khalid Hasan's explicit Phase 7 review approval. No subsequent category, commit, push or publication.**

Final repository gate passed: 35 categories / 256 memberships / 235 canonicals; 318 Markdown files and 3957 local links; 217 generated pages, zero drift; 244 infrastructure tests. All nine historical/current reports are nonempty, tracked and not ignored. Clean staged export passed catalog/generated/scope checks. Archive preflight passed with 963 files, byte equality, CRC and fresh-extraction validation. Final archive repeats these checks and records the observed digest in its sidecar. STOP for owner review.
