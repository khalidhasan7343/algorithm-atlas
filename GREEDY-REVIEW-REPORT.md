# Phase 6 — Greedy Algorithms review report

**The four authorized Greedy-owned topics are implemented and locally tested. Phase 6 is awaiting owner review; it is not human-approved.**

Prepared for **MD.Khalid Hasan**, 2026-10-22 (Asia/Dhaka). The owner explicitly approved Phase 5 in this session. Its eleven topics were separately checked against the verified Phase 5 archive manifest; approval was not treated as test certification. MIT licensing and attribution are preserved. Historical reports remain unchanged as original handoff records; current approval is recorded in the [checkpoint](docs/greedy-checkpoints.md), [working instructions](AGENTS.md) and catalog.

## Complete category membership and classification

A11 retains **seven original memberships**: four Greedy implementations and three shared Graph topics. No prior complete Greedy implementation existed to reuse. Completing this authorized scope does not complete all seven memberships.

| Original membership | Canonical lesson | Phase 6 status | Python | C++17 | C++20 |
| --- | --- | --- | ---: | ---: | ---: |
| Activity Selection | [activity-selection](dsa/greedy/activity-selection/README.md) | New, complete/tested | 3 | 2 | 2 |
| Huffman Coding | [huffman-coding](dsa/greedy/huffman-coding/README.md) | New, complete/tested | 4 | 3 | 3 |
| Fractional Knapsack | [fractional-knapsack](dsa/greedy/fractional-knapsack/README.md) | New, complete/tested | 3 | 2 | 2 |
| Job Sequencing with Deadlines | [job-sequencing-with-deadlines](dsa/greedy/job-sequencing-with-deadlines/README.md) | New, complete/tested | 3 | 3 | 3 |
| Kruskal's Algorithm | [kruskal](dsa/graph-algorithms/kruskal/README.md) | Conceptual reference; planned | — | — | — |
| Prim's Algorithm | [prim](dsa/graph-algorithms/prim/README.md) | Conceptual reference; planned | — | — | — |
| Dijkstra's Algorithm | [dijkstra](dsa/graph-algorithms/dijkstra/README.md) | Conceptual reference; planned | — | — | — |
| **Authorized total** | **4 new lessons** | **33 collected tests** | **13** | **10** | **10** |

The [Greedy README](dsa/greedy/README.md) and [roadmap](docs/learning-roadmap.md) explicitly separate “Greedy algorithms implemented in Phase 6” from “Graph algorithms that also use the Greedy paradigm.” They explain Dijkstra's smallest tentative-distance choice under nonnegative weights, Prim's cheapest cut edge and Kruskal's cheapest cycle-free edge. Their Graph canonical paths and all four statuses remain unchanged and planned. No Graph implementation or duplicate folder was created; actual implementation requires an authorized Graph phase.

Catalog metadata uses only the existing `related_algorithms` field: Activity Selection gains these three conceptual references. No new tags/schema fields, identities, categories or memberships were added. Counts remain **256 syllabus entries, 235 canonical topics, 35 categories**.

## Implementation contracts and correctness/complexity audit

All four lessons have the exact 25 numbered sections, intuition, applications, prerequisites, greedy-choice/optimal-substructure proofs, pseudocode, detailed dry runs, numeric contracts, actual time/space bounds, runnable examples, limitations, comparisons, interview questions, exercises and primary references. The source implements each strategy directly. Sorting, priority queues and disjoint sets are supporting structures, not substitutes for the algorithm.

| Topic | Contract and proof | Complexity |
| --- | --- | --- |
| Activity Selection | Half-open positive-duration intervals; maximize count, return original indices; ties finish/start/index. Exchange the first optimum activity with the earliest-finishing feasible activity, then induct on the remainder. | O(n log(n+1)) worst including sorting, O(n) scan, O(n) indices/output |
| Fractional Knapsack | Divisible items; exact density cross products, rational total and per-item fractions; equal ratios prefer index; zero-value items omitted. Equal-weight exchange from lower to higher density proves optimality. | O(n log(n+1)) worst sorting plus O(n) scan/output under bounded arithmetic |
| Huffman Coding | Actual two-minimum heap tree, ties frequency/minimum subtree byte/creation index; left=0/right=1; encoding/decoding and weighted cost. Exchange minimum weights into deepest sibling leaves and collapse them to prove optimality; leaf paths prove prefix freedom. | Tree build O(k log(k+1)); materialized codewords add O(L), where L can be O(k²). Decode linear in bits/output; C++ encoding map lookup adds O(message length·log(k+1)). |
| Job Sequencing | Independent unit-duration jobs; descending profit/index, latest feasible slot; omit deadline zero/nonpositive profit. Nested deadline capacities form a matroid, so weighted exchange proves profit greedy; saturated-prefix reasoning proves safe rejection. | O(n log(n+1)) total; rank/path-compression slot operations O(q·α(H+1)) amortized; O(n+H) storage, H≤n |

Huffman L is total codeword length; it is not hidden inside the tree-build bound. Job disjoint sets keep the free boundary separately from the rank-selected representative. Lessons explain meaningful best cases and avoid assuming an average input distribution. These are code/proof audits supported by independent tests, not benchmark-based proofs of asymptotic bounds.

All APIs preserve caller inputs. Python native integer fields reject bool/floats; invalid data/resource bounds raise ValueError, or C++ invalid_argument. C++ library use defines `ALGORITHM_ATLAS_NO_MAIN` and namespace `atlas_greedy`. CLIs use exact ASCII-decimal token counts, print one JSON value on success, and return exit 2 with stderr/empty stdout on malformed or invalid input.

Numeric/resource contracts:

- Activity: n≤10000, times ±10^9, start<finish; touching allowed, duplicates positional, empty returns []. Zero-duration/reversed intervals rejected. Time values are compared without overflow-sensitive subtraction.
- Fractional: n≤10000, weights 1..10^6, values 0..10^6, capacity 0..10^9. Zero/negative weights and negative values rejected. Cross products≤10^12; full value≤10^10; rational numerator≤10^10·10^6+10^12 fits signed-64, denominator≤10^6. Python Fraction and reduced C++ pairs avoid floating point internally; external float conversion can round.
- Huffman: unique byte symbols 0..255, frequencies 1..10^9, messages/decoded output≤10000 bytes, streams≤1000000 bits. Empty alphabet accepts only empty data; singleton code is 0 and weighted cost is its frequency. Unknown symbols, duplicate CLI/C++ symbols, malformed/truncated streams and size violations are rejected. Subtree sums≤256·10^9 and conservative weighted cost≤256·10^9·255 fit signed-64. These are ordinary deterministic tree codes, not canonical Huffman codes.
- Jobs: n≤10000, deadlines 0..10^9, profits ±10^9. Negative deadlines rejected; zero unschedulable; nonpositive profit omitted. Fixed output horizon H=min(n,max deadline) represents unused slots as nulls. Clamp before allocation; total profit≤10^13 fits signed-64. No variable durations, release times, dependencies or multiple machines.

## Sequential batch evidence

Batch 1's complete lessons, Python/C++17/C++20 tests and repository gates passed before Batch 2 implementation began. No inter-batch approval was requested.

| Gate | Actual result |
| --- | --- |
| Batch 1: activity-selection | 7 passed in 3.90s |
| Batch 1: fractional-knapsack | 7 passed in 2.93s |
| Batch 2: huffman-coding | 10 passed in 5.45s |
| Batch 2: job-sequencing-with-deadlines | 9 passed in 4.40s |
| Batch 1 repository | Catalog/generated docs passed; 236 infrastructure passed in 2.28s |
| Batch 2 repository | Catalog/generated docs passed; 236 infrastructure passed in 2.46s |

Commands, limits and transcripts are in [execution evidence](docs/greedy-evidence/README.md) and the checkpoint. Batch-prefixed configuration records preserve both gates.

## Final actual results

Environment: Python 3.14.2, macOS arm64, Apple Clang 21.0.0 (the local g++ command invokes Clang). Only this local environment was executed. Child gates have 300-second limits; compilation 60 seconds, API execution 30 seconds, CLI execution 10 seconds. No job timed out.

| Run | Actual result |
| --- | --- |
| python | 13 passed, 20 deselected in 0.85s |
| cpp17 | 10 passed, 13 deselected in 5.43s |
| cpp20 | 10 passed, 13 deselected in 6.69s |
| full-suite | 1389 passed in 174.60s (0:02:54) |
| C++20 ASan+UBSan, recovery disabled | 10 passed, 13 deselected in 9.38s |
| Documented Python/C++20 examples | 8/8 exact expected outputs |
| Prior-file preservation | 263 files byte-identical |
| 25-section/artifact audit | All four lessons passed |
| Membership/classification audit | 256/235 counts, seven A11 memberships, three unchanged Graph topics |

The full suite is **1389 passed**: 556 Sorting + 316 Searching + 125 Recursion/Backtracking + 36 Divide/Conquer + 87 Dynamic Programming + 33 Greedy + 236 infrastructure. All five previously completed categories passed regression. There were no failures, errors or skips. Language-marker deselections are not passes. Sanitizers repeat ten C++20 cases using `-fsanitize=address,undefined -fno-sanitize-recover=all`, not ten additional unique tests.

See [final records](docs/greedy-evidence/final-results.json), [sanitizers](docs/greedy-evidence/sanitizer-results.json), [examples](docs/greedy-evidence/examples-results.json), [environment](docs/greedy-evidence/environment.json) and [configuration](docs/greedy-evidence/configuration-results.json). Final catalog/generated/infrastructure checks after report/metadata edits are recorded there rather than inferred.

## Independent randomized and brute-force tests

| Topic | Input-vector entries | Independent oracle/evidence |
| --- | ---: | --- |
| Activity Selection | 273 | Enumerate all compatible positional subsets; maximize count then specified witness order. Exhaustive four-interval-pool arrays through length 3, seed 6001, 10000-interval fixed schedule; check compatibility/mutation. |
| Fractional Knapsack | 148 | Enumerate all small LP vertices: zero/one choices except at most one partial item. Optimize exact value and allocation tie policy; seed 6002; 2/3, equal/near ratios, zero capacity/values and 10000-item fixed total; check feasibility. |
| Huffman Coding | 147 | Exhaustively try every pair at every merge with memoization, not greedy pair choice; seed 6003. Check weighted optimum, prefix freedom, round trips, equal-frequency determinism and cross-language codes. Full-byte and powers-of-two costs have analytic expectations. |
| Job Sequencing with Deadlines | 273 | Enumerate all subsets with sorted-deadline feasibility, independent of profit ordering/DSU. Exhaustive four-job-type arrays through length 3; seed 6004; verify unique jobs, deadlines, total profit, deterministic cross-language witnesses and large sparse deadlines. |

The [oracle inventory](docs/greedy-evidence/oracle-inventory.json) contains **841 input-vector entries**, reused across languages/standards; they are not all distinct inputs or collected pytest cases. Some witness/property checks repeat vectors. Invalid/resource/CLI assertions run additionally. Cross-language agreement supplements independent expected optimality rather than replacing it.

## Preservation, catalog and GitHub Actions readiness

Baseline: revision 20fd27321d46098358f862c81dec1b9ecf1ee40c plus the already-staged approved Phase 5 state. [Baseline hashes](docs/greedy-evidence/approved-baseline.json) and the original catalog snapshot preserve provenance. All 263 prior algorithm/report/license/ignore/workflow files remain byte-identical, including the five completed categories and Graph records. All out-of-scope catalog records remain equal. [Preservation audit](docs/greedy-evidence/preservation-results.json) works offline after ZIP extraction.

Completion increases from 41 to **45 topics**; 189 remain planned and one blocked (190 remaining). Dynamic Policy Optimization retains its unresolved-reference blocker. New documentation is implemented; Python/C++/tests are tested, never human-reviewed. Development is awaiting-review, completed_batches [1,2], active_batch null. Current guides, roadmap and generated progress/index/A11 pages describe the exact scope. Workflow, dependencies, frozen syllabus and strict validators remain intact. Twelve new infrastructure cases guard batch claims and Graph classification.

All eight review reports are existing, nonempty and tracked, verified with `git ls-files --error-unmatch`; `git check-ignore --no-index` confirms none is ignored. Catalog/local-link, generated-document and preservation checks passed from a clean export of the actual staged Git index. [Tracking evidence](docs/greedy-evidence/tracking-results.json) records these actual outcomes. `development.completion_report` points to this report. Phase 6 files are staged for these integrity checks; no commit was created. No hosted GitHub Actions run was triggered or verified; local checks are not hosted CI certification. No commit or push is authorized or performed.

## Bugs fixed and limitations

No confirmed defect in prior algorithms required changing their sources. Tests guard endpoint/tie semantics, exact fractional decisions, prefix/singleton/invalid Huffman streams, omission policies and deadline-safe unique schedules. No failing test was weakened or relabeled.

- Activity Selection is unweighted, one resource and half-open positive-duration intervals; weighted interval scheduling needs a different algorithm.
- Fractional Knapsack assumes divisible linear values and one capacity. Zero-weight/negative-value/real inputs are outside its API; retain rational pairs if external floating conversion loss is unacceptable.
- Huffman outputs string bits, not packed files; no framing/header, arbitrary-codebook import, adaptive mode, corruption detection or canonical-code serialization. Both ends need the same frequencies/tree. Symbols are bytes, not Unicode characters.
- Job Sequencing depends on independent unit durations with no release times or dependencies. Nonpositive profits are omitted and fixed-horizon idle slots are represented.
- Numeric/resource caps are intentional. Hosted CI matrix and other local environments remain unverified.
- Dijkstra, Prim and Kruskal remain planned Graph implementations; conceptual references do not authorize their development or complete their A11 memberships.

## Files added and modified

Four planning READMEs became full lessons; each canonical folder gained `python/solution.py`, `cpp/solution.cpp`, `tests/cases.py`, `tests/test_python.py` and `tests/test_cpp.py` (20 new per-topic modules). Added category conftest/common header, validation/example/scope/tracking/package scripts, checkpoints, actual evidence and this report. Updated metadata, guides, roadmap, generated documentation and validator/generator support with twelve regression cases.

The Phase 6-only [changed-file inventory](docs/greedy-evidence/changed-files.txt) is computed relative to the already-staged approved Phase 5 snapshot. Preexisting Phase 5 changes are preserved. The archive verification sidecar lists every payload file and its SHA-256.

## Exact reproduction commands

From the root with development dependencies and C++17/C++20 available:

```sh
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python scripts/run_greedy_validation.py --stage final
CXX='clang++ -fsanitize=address,undefined -fno-sanitize-recover=all' .venv/bin/python scripts/run_greedy_validation.py --stage sanitizer
.venv/bin/python scripts/verify_greedy_examples.py
.venv/bin/python scripts/verify_greedy_scope.py
.venv/bin/python scripts/verify_greedy_tracking.py
.venv/bin/python -m pytest --require-cpp
```

The runner supports batch1, batch2 and configuration stages; reruns overwrite their evidence logs. Direct pytest supports `--cpp-standard=c++17` or `--cpp-standard=c++20`. Tracking verification requires Git metadata and the complete proposed state in the actual Git index; staging is not a commit. Other checks work after extraction with dependencies supplied. Historical phase scope checkers apply to their historical snapshots; this phase uses the Greedy checker.

## Review archive and mandatory stop

Artifacts: `algorithm-atlas-greedy-review.zip`, `.zip.sha256` and an extra `.zip.verification.json`. The ZIP contains the entire updated repository source/documentation/configuration/evidence under `algorithm-atlas/`. Git internals, environments, caches, binaries, temporary/private/credential files, data/model weights, older archives and archive sidecars are excluded. Historical Markdown reports and genuine text/JSON evidence are preserved.

`python scripts/package_greedy_review.py` refuses to overwrite an existing artifact. It checks required files, exact source bytes, safe unique paths, directories, no symlinks, CRC and SHA-256. A temporary extracted copy runs catalog/local-link, generated-document and preservation checks. Actual counts/hash and extracted outputs are stored in the external verification sidecar to avoid a self-hash dependency.

```sh
shasum -a 256 -c algorithm-atlas-greedy-review.zip.sha256
```

**STOP for MD.Khalid Hasan's explicit Phase 6 review and approval. Do not mark Phase 6 human-approved, start Graph Algorithms or another category, commit, push or publish.**
