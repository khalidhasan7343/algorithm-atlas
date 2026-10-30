# Phase review packages

Six existing ZIPs and twelve checksum/verification sidecars were relocated without changing their bytes (6,919,849 ZIP bytes total). Five package sets were already tracked. The Graph set was local and untracked; cleanup preserves that status. None was ignored. Availability below describes the working checkout at maintenance time, not a guarantee that local untracked files exist in a fresh clone.

| Phase | Availability at cleanup | ZIP bytes |
| --- | --- | ---: |
| [sorting](sorting/README.md) | no package found | — |
| [searching](searching/README.md) | tracked before cleanup | 810606 |
| [recursion-backtracking](recursion-backtracking/README.md) | tracked before cleanup | 948887 |
| [divide-conquer](divide-conquer/README.md) | tracked before cleanup | 1053768 |
| [dynamic-programming](dynamic-programming/README.md) | tracked before cleanup | 1225605 |
| [greedy](greedy/README.md) | tracked before cleanup | 1338178 |
| [graph-algorithms](graph-algorithms/README.md) | local, untracked before cleanup | 1542805 |

Checksums contain archive basenames, so run shasum from the corresponding phase folder. The verifier also resolves them correctly from the repository root. ZIP metadata describes the unchanged original archived snapshot; historical internal paths should not be rewritten. See [review reports](../../docs/reviews/README.md) and the [maintenance report](../../docs/maintenance/root-cleanup/REPORT.md).

Future ZIPs, SHA-256 sidecars and package JSON belong in artifacts/review-packages/<phase-name>/. Package scripts create their output directory, retain no-overwrite protection, and exclude nested ZIPs and sidecars from source payloads. Markdown reports must remain tracked and unignored. Existing owner-review gates remain mandatory.

The later [Tree Algorithms package](tree-algorithms/README.md) follows Phase 8 conventions and records its pending owner approval separately from the maintenance-time inventory above.

The [String Algorithms package](string-algorithms/README.md) records Phase 9 execution and pending owner approval. The later explicit approval of Phase 8 is recorded in [String checkpoints](../../docs/string-algorithms-checkpoints.md); historical Tree sidecars retain their handoff-time approval status.

The [Bit Manipulation package](bit-manipulation/README.md) covers normal roadmap Phase 10 and records pending owner approval. The owner explicitly approved completed Phase 9 on 2026-10-24, as recorded in [Bit checkpoints](../../docs/bit-manipulation-checkpoints.md); historical String package metadata retains its original handoff-time pending status.

The owner officially approved Phase 10 on 2026-10-24 (Asia/Dhaka); the original
Bit package remains unchanged. The [Number Theory package](number-theory/README.md)
and [Two Pointers & Sliding Window package](two-pointers-sliding-window/README.md)
cover jointly authorized Phases 11/12 with independent pending owner checkpoints.
There is no third combined ZIP.

The later [DSA final audit package](dsa-final-audit/README.md) is a separately
authorized verification snapshot covering all DSA canonicals. It preserves the
independent Phase 11/12 approval checkpoints and excludes historical review ZIPs.

The [Regression package](regression/README.md) covers authorized Phase 13 ML
foundation and the seven B1 canonicals. It preserves DSA source/history, requires
Python/numerical tests for ML with optional C++, and awaits explicit owner approval.

The owner subsequently satisfied Phase 13's checkpoint on 2026-10-28, authorizing
the [Classification package](classification/README.md) for Phase 14's eleven B2
canonicals. Its owner review remains pending; original B1 package bytes/metadata
remain unchanged historical records.

The owner subsequently approved all previous work and authorized only the
[Phase 13 B1 Regression completion audit](regression/README.md). Its current
review approval remains pending. The approved prior Regression package set is
preserved under the Regression history folder; Classification and all earlier
package bytes remain unchanged. The active Regression ZIP/checksum/JSON contain
the revised audit deliverables and actual extraction verification results.

After accepting the latest B1 completion audit and all earlier work, the owner
authorized [Phase 15 Ensemble Methods](ensemble-methods/README.md). Its new review
approval remains pending. All prior Regression/Classification/DSA report/evidence/
package bytes are preserved; their generation-time statuses remain historical.

The owner subsequently approved the latest Ensemble Methods review and authorized
[Phase 16 Clustering](clustering/README.md), whose new owner review remains pending.
All previous package/report/evidence bytes are preserved; generation-time pending
statuses remain historical rather than rewritten after approval.
