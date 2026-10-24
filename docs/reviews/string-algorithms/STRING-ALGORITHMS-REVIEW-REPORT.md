# Phase 9 — String Algorithms review report

Owner and maintainer: **MD.Khalid Hasan**. Repository:
[khalidhasan7343/algorithm-atlas](https://github.com/khalidhasan7343/algorithm-atlas).
[MIT License](../../../LICENSE). Review date: 2026-10-23 (Asia/Dhaka).

**All nine A7 String Algorithms are implemented, documented and locally tested.
Phase 9 owner approval remains pending.** The owner explicitly stated “I approved
phase 8” and supplied the Phase 9 instructions. That approval is recorded in
[String checkpoints](../../string-algorithms-checkpoints.md), the current catalog
and working instructions. Historical Phase 8 handoff statements remain unchanged.
No Phase 10, other category, commit, push or publication is authorized.

## Exact scope and implementation status

The authoritative catalog matches the supplied nine IDs and paths without any
syllabus discrepancy. Every row has the exact 25-section README, Python source,
C++ source and executable test files. Documentation status is implemented;
Python/C++/test statuses are tested, without a human-reviewed claim.

| Algorithm | Canonical path | Implemented behavior |
| --- | --- | --- |
| Naive Pattern Matching | [dsa/string-algorithms/naive-pattern-matching/](../../../dsa/string-algorithms/naive-pattern-matching/README.md) | Alignment comparisons; overlaps and all empty boundaries. |
| KMP | [dsa/string-algorithms/knuth-morris-pratt/](../../../dsa/string-algorithms/knuth-morris-pratt/README.md) | Prefix/LPS links and full-match fallback; independent border table oracle. |
| Rabin-Karp | [dsa/string-algorithms/rabin-karp/](../../../dsa/string-algorithms/rabin-karp/README.md) | Polynomial rolling hash; byte verification; deliberate weak-hash collisions. |
| Z-Algorithm | [dsa/string-algorithms/z-algorithm/](../../../dsa/string-algorithms/z-algorithm/README.md) | Linear Z-box reuse; Z[0]=0; integer separator 256. |
| Boyer-Moore | [dsa/string-algorithms/boyer-moore/](../../../dsa/string-algorithms/boyer-moore/README.md) | Bad-character and strong good-suffix shifts; proper full-match shifts. |
| Manacher | [dsa/string-algorithms/manacher/](../../../dsa/string-algorithms/manacher/README.md) | Separate odd/even radii; earliest longest half-open range. |
| Suffix Array | [dsa/string-algorithms/suffix-array/](../../../dsa/string-algorithms/suffix-array/README.md) | Rank-pair prefix doubling, Kasai LCP and binary-bound search. |
| Suffix Tree | [dsa/string-algorithms/suffix-tree/](../../../dsa/string-algorithms/suffix-tree/README.md) | Genuine compressed edges, range splitting, explicit suffix leaves and terminal 256. |
| Aho-Corasick | [dsa/string-algorithms/aho-corasick/](../../../dsa/string-algorithms/aho-corasick/README.md) | Dense byte trie transitions, BFS failures and uncopied terminal output links. |

[Shared contracts](../../string-conventions.md) define exact unsigned-byte
semantics. Python accepts bytes; Unicode callers encode UTF-8 explicitly. C++
std::string indexes bytes. All positions therefore agree across languages and
are byte offsets, including Unicode examples. Empty pattern matches all n+1
boundaries; all overlaps are included. Inputs are case sensitive. Sentinels
cannot collide with any byte. Aho duplicates retain distinct list IDs and its
triple order is end, decreasing pattern length, then identity. Manacher returns
earliest longest range with both parity radii.

## Sequential batch records

| Batch | Algorithm gate | Repository gate |
| --- | --- | --- |
| 1 | 30 passed in 13.43s | catalog/links, generation, infrastructure passed |
| 2 | 30 passed in 9.25s | catalog/links, generation, infrastructure passed |
| 3 | 30 passed in 10.62s | catalog/links, generation, infrastructure passed |

Batch 1: Naive/KMP/Rabin-Karp. Batch 2: Z/Boyer-Moore/Manacher.
Batch 3: Suffix Array/Suffix Tree/Aho-Corasick. Each batch's lessons and both C++
standards passed before implementation of the next batch. The repository gates
ran 271, 271 and 272 infrastructure tests respectively. Later final tests also
strengthened C++ KMP border and Rabin-Karp weak-hash checking over the complete
679-vector corpus. No algorithm was substituted with a placeholder.

Observed batch commands, elapsed times and logs are linked from
[checkpoints](../../string-algorithms-checkpoints.md). Original development-run
logs remain in the evidence directory; final evidence controls the handoff.

## Final observed validation

| Selection | Actual pytest result |
| --- | --- |
| python | 36 passed, 54 deselected in 2.99s |
| cpp17 | 27 passed, 36 deselected in 17.61s |
| cpp20 | 27 passed, 36 deselected in 20.25s |
| full-suite | 1819 passed in 367.24s (0:06:07) |

No failures, skips or timeouts occurred in these final runs. Deselected tests in
the language-specific runs were deliberately outside that selection; they ran in
the full suite. The C++ fixture default tests both C++17 and C++20 and requires an
available compiler. [Final command records](../../string-algorithms-evidence/final-results.json)
and [full-suite output](../../string-algorithms-evidence/final-full-suite.txt)
record actual execution, rather than configured intentions.

[ASan/UBSan evidence](../../string-algorithms-evidence/sanitizer-results.json):
27 C++20 tests passed, 36 deselected, with no sanitizer diagnostics.
All [nine lesson examples](../../string-algorithms-evidence/examples-results.json)
were executed in Python, C++17 and C++20: 27 configurations passed.

The full repository run included these previously completed categories:

| Prior category | Collected and executed tests |
| --- | ---: |
| divide-and-conquer | 36 |
| dynamic-programming | 87 |
| graph-algorithms | 151 |
| greedy | 33 |
| recursion-and-backtracking | 125 |
| searching | 316 |
| sorting | 556 |
| tree-algorithms | 153 |

These counts come from the [regression inventory](../../string-algorithms-evidence/regression-inventory.json),
with execution established by the successful full suite. Infrastructure adds 272
tests and String adds 90, totaling 1819. No separately executed regression run is
implied by collection.

## Independent oracles and cross-algorithm verification

[Oracle inventory](../../string-algorithms-evidence/oracle-inventory.json) records
seed 90901 and 679 matching vectors per matching/indexing algorithm: 465 bounded
exhaustive binary pairs, 160 randomized pairs, 40 repetitive pairs and 14 explicit
empty/minimal/Unicode/NUL/all-byte/special cases. The independent occurrence oracle
uses byte slicing, not the production alignment/failure/hash code. KMP LPS is
checked by exhaustive proper-border enumeration; Z values by direct expansion;
Boyer-Moore good-suffix shifts by independently enumerating compatible shifts.
Rabin-Karp is tested with base=1/modulus=2 over every corpus pair, including an
explicit unequal collision, in both languages.

Manacher uses 233 distinct texts, comparing every odd/even radius with independent
center expansion and the earliest longest range with exhaustive substring checks.
Suffix Array order is compared with direct suffix-string sorting only in the
small oracle, and adjacent LCP with pairwise comparison. Aho uses 167 pattern sets,
including 160 randomized seed-90904 sets, with independent repeated matching.
C++ outputs are compared with these expectations and with the Python API.

The [cross matrix](../../string-algorithms-evidence/cross-matrix-batch3.json)
executes 120 seed-90909 cases for each of nine relationships: Naive versus KMP,
Rabin-Karp, Z and Boyer-Moore; Manacher versus exhaustive/expansion; Suffix Array
order/LCP versus direct suffixes; both suffix indexes versus Naive; Aho versus
repeated Naive. All 1080 relationship checks passed. Repetitive and binary-byte
inputs are included. A discovered infrastructure test keeps the complete matrix
in future CI runs.

## Advanced structural invariants

External checks consume snapshots rather than constructor helper results.
Suffix Tree verifies unique reachable nodes, nonempty in-range edge ranges,
child-key/edge-first-symbol equality, unique incoming parents, at least two
children for every nonroot internal node, one terminal per leaf, exactly one
leaf per suffix including the empty suffix, and exact root-to-leaf suffix spelling.
Every distinct corpus text and a 2048-byte repeated-string tree pass these checks
in Python/C++17/C++20. The node-count bound is linear. Queries ending inside an
edge and repeated queries preserve the structure.

Aho structure checks reconstruct trie prefixes from the original patterns and
independently derive longest proper suffix failures, all 256 completed transitions,
local pattern identities and nearest nonroot terminal output links. Failure depth
strictly decreases. Every corpus pattern set passes in all language configurations.
Tests exercise 4096 aggregate pattern bytes, 256 empty pattern identities,
10000-byte text, copied input ownership, duplicates, shared suffixes and repeated
queries. Invalid counts, byte types, lengths, malformed hex and extra/missing
CLI tokens are rejected. C++ type constraints have no runtime Python-str analogue.

## Performance and complexity audit

[Code-path audit and measurements](../../string-algorithms-evidence/complexity-results.json)
separate asymptotic reasoning from one bounded Python observation per algorithm.
No wall-clock threshold is used as a correctness test or proof of complexity.
Maximum-size repeated-byte correctness cases also run in both C++ standards.

| Algorithm | Actual bound and reason |
| --- | --- |
| Naive | O(nm) worst-case comparisons; constant scan state plus output. |
| KMP | O(m) border preprocessing and O(n+r) amortized scan/output. |
| Rabin-Karp | O(m+n+c*m+r), c candidate windows; O(nm) worst case, even for dense genuine matches. Fixed parameters give no adversarial expected-time guarantee. |
| Z | O(n+m+r), with explicit combined symbols and linear rightmost-box extension. |
| Boyer-Moore | O(m+256) table construction; O(nm) worst-case all-occurrences scanning without Galil optimization. |
| Manacher | O(n) for both parity passes and longest-range selection; O(n) returned radii. |
| Suffix Array | Comparison-sort doubling O(n log² n), Kasai O(n); query O(m log n+r log r) including numeric output sorting. |
| Suffix Tree | Genuine compressed direct insertion O(n²) comparisons, O(n) nodes; contains O(m), find O(m+r log r) for the fixed alphabet. C++ child maps add log sigma, sigma≤257. |
| Aho-Corasick | O(P+k+256V) construction, O(n+z) scanning; O(256V+P+k+z) space including eager results. Output lists are not inherited/copied. |

Rabin-Karp uses byte+1, base 257, modulus 1000000007 by default and verifies every
hash candidate. Parameter bounds and modular normalization keep C++ int64_t
products below overflow; the lesson gives the arithmetic bound. No probabilistic
correctness claim or cryptographic hash claim is made. No optimized full-suffix
string sort is hidden inside construction. The Suffix Tree explicitly does not
claim Ukkonen construction.

## Catalog, documentation, preservation and Git readiness

Catalog/link validation and generated-document checks passed at every gate.
The final catalog still contains **35 categories, 256 original memberships and
235 canonicals**. There are 83 implemented canonicals, 151 planned and one blocked.
Out-of-scope algorithm records are identical to the frozen baseline; Dynamic
Policy Optimization remains blocked pending its intended reference. Generated
index/progress/category pages have no drift. The roadmap and current navigation
record Phase 8 approval and the Phase 9 boundary.

[Preservation evidence](../../string-algorithms-evidence/preservation-results.json)
checks 1068 protected prior source, lesson, test, report, checkpoint,
execution-evidence, workflow, license and historical package files byte for byte.
Three current navigation pages are named exceptions so they can record the later
explicit approval; no historical report finding or package digest was rewritten.
[Tracking checks](../../string-algorithms-evidence/tracking-results.json) verify all
eleven required reports exist, are nonempty and unignored, and the catalog's
completion_report points here. Ten historical reports are tracked; this report
and new source are ready to track. The Git index was not modified. A clean tracked
checkout was not run because current new files are uncommitted; clean source export
and ZIP extraction checks provide independent configuration/source validation.

The existing workflow remains unchanged and runs the required catalog/generation
and C++17/C++20 suite. Local environment is Python 3.14.2 on macOS arm64, with g++
resolving to Apple clang 21.0.0. **Hosted GitHub Actions was not triggered or verified.**
The hosted Linux/Python matrix and other compilers were not run locally.

## Corrections and remaining limitations

Initial test-scaffold quoting was corrected before the first successful pytest
run. The first documentation integration gate exposed missing development-state
context in the category renderer; it now receives that context explicitly. A new
progress test also initially imported the wrong renderer name and was corrected.
The failed [generation log](../../string-algorithms-evidence/batch1-initial-generated-docs.txt)
and [infrastructure log](../../string-algorithms-evidence/batch1-initial-infrastructure.txt)
are retained. These were integration/test-scaffold errors; no core algorithm defect
was observed in the final deterministic tests. No validators or tests were weakened.

These are bounded in-memory educational APIs. Byte semantics provide no Unicode
normalization or grapheme interpretation. Default strings are at most 10000 bytes;
the direct quadratic tree constructor accepts at most 2048 text bytes. Aho limits
are 256 patterns/4096 aggregate bytes, but eager output can still approach
(n+1)k triples and consume substantial memory. Index inspection arrays must not be
mutated. Static indexes must be rebuilt after changing text/patterns. Streaming,
concurrency, persistence, allocation-failure atomicity and production service
behavior are outside scope. Finite deterministic tests and sanitizers are evidence,
not a proof for all inputs or machine configurations.

## Changed files and reproduction

The [changed-file manifest](../../string-algorithms-evidence/changed-files.txt)
lists source/documentation changes and the three review artifacts. Additions
include nine canonical source/test pairs, shared byte/transport support, independent
oracles, structural/cross checks, execution runners, evidence, this report and the
package generator. Modified infrastructure only adds Phase 9 state/generation
validation and tests. Approved implementation source is unchanged.

From the repository root, use the existing environment:

```sh
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python -m pytest --require-cpp
.venv/bin/python scripts/verify_string_algorithms_scope.py --check-only
.venv/bin/python scripts/verify_string_cross_algorithms.py --check-only
.venv/bin/python scripts/verify_string_examples.py
.venv/bin/python scripts/audit_string_complexity.py
CXX='g++ -fsanitize=address,undefined -fno-sanitize-recover=all' .venv/bin/python -m pytest dsa/string-algorithms -m cpp --cpp-standard=c++20 --require-cpp
.venv/bin/python scripts/verify_string_tracking.py
.venv/bin/python scripts/package_string_algorithms_review.py
```

The validation runner accepts --stage batch1, batch2, batch3, configuration or
final and writes actual commands/logs. Evidence writers replace only current-phase
results. Package creation refuses to overwrite an existing archive.

## Review package and mandatory owner checkpoint

[Package guide](../../../artifacts/review-packages/string-algorithms/README.md)
identifies algorithm-atlas-string-algorithms-review.zip, its .zip.sha256 checksum
and algorithm-atlas-string-algorithms-review.json metadata. The ZIP contains the
updated repository source, documentation, tests, catalog, current evidence and
historical reports. It excludes .git, environments, caches, binaries, secrets and
all nested review ZIPs/unnecessary package sidecars, including its own artifacts.
Historical packages remain byte-preserved locally. The external JSON is the actual
record of CRC, SHA-256, safe paths, per-file source hashes, required-file presence,
clean source-export tests and independent extracted configuration/scope/cross checks.
Those archive checks occur after this report is finalized, avoiding a circular hash.

**STOP for MD.Khalid Hasan's explicit Phase 9 review and approval.** Phase 9 is
not human-approved. No Phase 10, other category, commit, push or publication has
been performed or is authorized.
