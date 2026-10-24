# Phase 10 — Bit Manipulation review report

Owner and maintainer: **MD.Khalid Hasan**. Repository:
[khalidhasan7343/algorithm-atlas](https://github.com/khalidhasan7343/algorithm-atlas).
[MIT License](../../../LICENSE). Review date: 2026-10-24 (Asia/Dhaka).

**All four A8 Bit Manipulation canonicals are implemented, documented and locally
tested. Phase 10 owner approval is pending.** This is normal roadmap Phase 10,
following the owner's explicit confirmation that Phase 9 is fully completed and
owner-approved. No additional Phase 9 approval was requested or inferred from tests.
Phase 8 remains completed and owner-approved. Current approval records are synchronized
in the catalog development state, current navigation, working instructions and
[Bit checkpoints](../../bit-manipulation-checkpoints.md). Historical Tree/String
handoff reports, execution evidence, ZIPs and metadata retain their original bytes.
No Phase 11, other category, commit, push or publication is authorized.

## Canonical deliverables

| Algorithm | Canonical path | Actual implementation |
| --- | --- | --- |
| XOR Tricks for Unique Elements | [dsa/bit-manipulation/xor-unique-elements/](../../../dsa/bit-manipulation/xor-unique-elements/README.md) | Unsigned-32 XOR accumulation and signed decode; checked solve plus explicit xor_candidate core. |
| Finding Two Non-Repeating Elements | [dsa/bit-manipulation/two-non-repeating-elements/](../../../dsa/bit-manipulation/two-non-repeating-elements/README.md) | Total XOR, differing-bit isolation, two group XORs and ascending signed pair; checked solve plus explicit partition_candidates. |
| Brian Kernighan Set Bit Counting | [dsa/bit-manipulation/brian-kernighan-set-bit-counting/](../../../dsa/bit-manipulation/brian-kernighan-set-bit-counting/README.md) | Genuine nonzero word AND (word-1) loop on a finite unsigned word. |
| Subset Generation using Bitmasking | [dsa/bit-manipulation/subset-generation-bitmasking/](../../../dsa/bit-manipulation/subset-generation-bitmasking/README.md) | Genuine unsigned mask enumeration with positional duplicates and guarded shifts. |

All four IDs/paths match the authoritative catalog exactly. Each directory has
the exact 25 numbered lesson sections, python/solution.py, cpp/solution.cpp,
tests/test_python.py and tests/test_cpp.py. Documentation status is implemented;
Python/C++/test status is tested. No per-topic reviewed or owner-approved flag is
claimed for Phase 10. No canonical duplication or syllabus expansion occurred.

## Numeric model and invalid-input behavior

[Shared contracts](../../bit-conventions.md) define signed inputs in
[-2147483648,2147483647]. Python accepts native int, excluding bool; C++ receives
int64_t then validates the same range. Bit operations use 32-bit unsigned words.
Python masks before work; C++ negative-to-unsigned conversion is modulo 2^32.
Words are decoded after widening: subtract 4294967296 when the high bit is set.
No implementation-defined unsigned-to-signed narrowing, signed INT_MIN negation,
negative signed shift or signed overflow is used. This supplies identical
mathematical two's-complement semantics without assuming C++17 signed storage.

Default XOR solve functions validate **exactly** one/two singleton counts and
otherwise exact pairs with a frequency map. They then compute the answer with
the named XOR core, not by returning frequency-map keys. Unsupported triples,
fourfold counts, too many singletons and no singletons are rejected. The explicit
candidate functions preserve O(n) time/O(1) auxiliary algorithm space under caller
pair assumptions; they do not pretend to prove those assumptions. Numeric, size,
minimum length/parity and zero-total checks are validated separately. Checked
wrappers add O(d) frequency memory and expected O(n) hashing work, worst O(n²).

Kernighan interprets -1 as 32 ones, INT32_MIN as one and INT32_MAX as 31. Zero
returns zero without entering the loop; masking prevents unbounded-negative
Python nontermination. Subsets use n≤16, increasing mask order, bit j for input
position j, and original order within each fresh row. Equal values retain equal
rows with full multiplicity. Empty input gives [[]]. All shift counts are below
32 and the loop limit is at most 65536. CLI tokens share a strict decimal grammar;
invalid input exits 2 with error: on stderr and no partial result.

## Sequential batch evidence

| Batch | Python/C++17/C++20 algorithm gate | Catalog/documentation/infrastructure gate |
| --- | --- | --- |
| 1 | 20 passed in 9.30s | passed |
| 2 | 20 passed in 9.94s | passed |

Batch 1 implements the two XOR topics; Batch 2 implements counting/subsets.
The first repository gate passed 280 infrastructure tests; the second passed
281, including the added oracle-matrix test. All lessons and both C++ standards
passed before advancing. [Checkpoints](../../bit-manipulation-checkpoints.md)
link exact commands/times and per-batch logs. No failures, skips or timeouts
occurred in these batch gates; no validator or test was weakened.

## Final observed tests and regressions

| Selection | Actual result |
| --- | --- |
| python | 16 passed, 24 deselected in 1.68s |
| cpp17 | 12 passed, 16 deselected in 5.42s |
| cpp20 | 12 passed, 16 deselected in 6.20s |
| full-suite | 1868 passed in 373.27s (0:06:13) |

[Final records](../../bit-manipulation-evidence/final-results.json) and
[full output](../../bit-manipulation-evidence/final-full-suite.txt) establish
execution. No failures, skips or timeouts occurred in the final runs. Tests
deselected by the language selections were deliberately outside those selections,
and ran in the full suite. C++ compilation alone is not counted as execution.

[ASan/UBSan C++20 run](../../bit-manipulation-evidence/sanitizer-results.json)
passed all 12 C++ tests, with 16 Python tests deselected and no diagnostics.
All four [lesson examples](../../bit-manipulation-evidence/examples-results.json)
passed in Python, C++17 and C++20: 12 executable configurations. Example commands
use a portable printf format that safely handles a negative first value.

The full repository suite included all previously completed categories:

| Prior category | Collected and executed test count |
| --- | ---: |
| divide-and-conquer | 36 |
| dynamic-programming | 87 |
| graph-algorithms | 151 |
| greedy | 33 |
| recursion-and-backtracking | 125 |
| searching | 316 |
| sorting | 556 |
| string-algorithms | 90 |
| tree-algorithms | 153 |

The [regression inventory](../../bit-manipulation-evidence/regression-inventory.json)
records collection separately from execution. Those prior categories plus 281
infrastructure and 40 Bit tests total 1868. No separate targeted regression run
is implied by collecting these counts. Tree and String implementations are
included in the successful full suite, with their code unchanged.

## Independent and randomized correctness evidence

[Oracle inventory](../../bit-manipulation-evidence/oracle-inventory.json) records
387 valid cases for each XOR topic: six explicit, 80 exhaustive combinations of
singleton/pair choices over a five-value signed alphabet, 300 deterministic random
cases, and one maximum-size valid array. Seeds are 10102 and 10103. Expected
answers come from independent frequency counting. Cases include a singleton zero,
negative and boundary values, zero-pair cancellation, high-bit-only partition and
9999/10000-value valid inputs. Default invalid multiplicities are separately tested.
Inputs are not mutated; tuple input and explicit candidate functions also run.

Kernighan uses 9268 values: exhaustive 12-bit words and their signed 32-bit
complements, all one-set and one-clear positions, boundary/alternating patterns,
and 1000 seed-10104 random signed values. Python expectations use binary-string
representation; a C++ test reference scans a fixed 32 positions using division
and remainder, independent of clearing the lowest set bit.

Subsets use 295 arrays: six explicit cases, all 127 binary-valued sequences through
length six, 160 seed-10105 random arrays and both distinct/all-equal maximum n=16
inputs. A separate positional recursive oracle generates all selections and
orders terminal selections by their IDs. It verifies exact mask ordering and
value rows, not just count. Duplicate and aliasing/input-mutation checks run.
The existing recursive Power Set canonical is compared as a multiset so duplicate
rows remain observable despite different generation order. Its code is preserved.

The [additional matrix](../../bit-manipulation-evidence/oracle-matrix.json) checks
every XOR corpus pair against frequency, plus 120 seed-10109 count and subset
comparisons with independent references and the existing Power Set. It also
checks all 32 possible isolated differing-bit positions. Every C++ corpus result
is compared both with independent expectations and with Python. Both standards
execute the same numeric contract. Malformed CLI, invalid types, over-wide signed
values, subset n=17/n=32 and resource boundaries receive explicit rejection tests.

## Complexity and resource audit

| Algorithm | Actual time | Actual auxiliary/output space |
| --- | --- | --- |
| XOR Unique candidate | O(n), fixed-width validation plus accumulation | O(1) auxiliary/scalar result |
| Two candidates | O(n), validation plus two word passes | O(1) auxiliary/two-value result |
| Checked XOR APIs | Expected O(n), generic hash worst O(n²), then the XOR core | O(d) map memory, d distinct values |
| Kernighan | O(k) clearing iterations, total O(k+1); k≤32 | O(1) |
| Bitmask subsets | Θ(n*2^n) for n≥1; empty input Θ(1) | O(n) working row beyond Θ(2^n+n*2^(n-1)) eager returned storage |

Array inputs for XOR are capped at 10000; all payloads are signed-32. At subset
n=16, exactly 65536 rows and 524288 selected value entries are materialized. The
exponential lower bound belongs to the requested eager output itself. Numeric
validation precedes shifts/enumeration; no unsupported shift is used to discover
an invalid input. No hardware popcount or recursive helper replaces production
bit algorithms. These bounds follow the code and representation, not a timing
benchmark claim.

## Catalog, approval preservation, reports and CI readiness

Catalog counts remain **35 categories / 256 original memberships / 235 canonicals**.
There are 87 completed canonicals, 147 planned and one blocked. Out-of-scope
algorithm records, including the nine tested String records, remain identical to
the frozen baseline. DPO stays blocked pending its intended reference. Current
phase approval is separate from the historical implementation-time notes.
[Approval verification](../../bit-manipulation-evidence/approval-verification.json)
records A6/A7 completion, prior String archive CRC/checksum, explicit owner Phase 9
approval and normal Phase 10 sequencing. It does not rewrite historical pending
handoff metadata to imply approval occurred earlier.

[Preservation audit](../../bit-manipulation-evidence/preservation-results.json)
verifies 1167 protected prior source, lesson, test, checkpoint, report, execution,
license, workflow and historical package files byte for byte. Four current
navigation pages are named exceptions; no prior implementation or historical
report finding was changed. The latest catalog development approval and current
README/progress/roadmap/category navigation reflect genuine Phase 9 approval.

[Configuration results](../../bit-manipulation-evidence/configuration-results.json)
record actual catalog/local-link validation, generated-document drift checks and
281 infrastructure tests. All 25-section headings are validated. The current
completion_report resolves to this nonempty file. [Tracking checks](../../bit-manipulation-evidence/tracking-results.json)
verify all twelve historical/current reports are nonempty, unignored and available
to Git. Eleven historical reports are tracked; the new report/source are ready to
track. The index was not changed and no commit was created. A clean tracked-file
checkout was not run because current new files are uncommitted; clean source
export and independent ZIP extraction are validated by the packager instead.

The unchanged workflow still requires catalog/generation checks and the full
C++17/C++20 pytest suite. Local tools are Python 3.14.2/macOS arm64 and Apple clang
21.0.0 under g++. [Environment evidence](../../bit-manipulation-evidence/environment.json)
records the actual versions. **Hosted GitHub Actions was not triggered or
verified**; its Linux/Python matrix and other compiler platforms were not run.

## Limitations, corrections and remaining risks

No confirmed algorithm defect or failing gate was observed in this phase's
recorded test runs. No tests/validators were disabled or weakened. These bounded
educational APIs are not arbitrary-precision, streaming, concurrent or persistent
services. Default XOR validation deliberately spends additional map memory;
candidate cores require the documented occurrence promise. Positional subsets
are eager and exponential, and duplicate rows are intentional. Allocation
failure, concurrent mutation and machine-independent timing guarantees are outside
the contract. Finite tests and sanitizer results are evidence, not a proof for
every compiler, machine or possible input.

## Changed files and exact reproduction

[Changed-file manifest](../../bit-manipulation-evidence/changed-files.txt) lists
source, documentation, current metadata and the three review artifacts. Additions
include four canonical Python/C++ implementations and tests, shared signed-32
validation/serialization, independent oracles, evidence/checkpoint/contracts,
verification/runners, this report and package generation. Existing modifications
update current approval/navigation, A8 catalog statuses and phase-aware
validator/generator checks. Prior implementation files are unchanged.

From the repository root:

```sh
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python -m pytest --require-cpp
.venv/bin/python scripts/verify_bit_manipulation_scope.py --check-only
.venv/bin/python scripts/verify_bit_oracles.py --check-only
.venv/bin/python scripts/verify_bit_examples.py
CXX='g++ -fsanitize=address,undefined -fno-sanitize-recover=all' .venv/bin/python -m pytest dsa/bit-manipulation -m cpp --cpp-standard=c++20 --require-cpp
.venv/bin/python scripts/verify_bit_tracking.py
.venv/bin/python scripts/package_bit_manipulation_review.py
```

The runner accepts --stage batch1, batch2, configuration or final. Evidence writers
replace only current-phase outputs. Package creation refuses to overwrite an
existing ZIP.

## Package and mandatory owner checkpoint

[Package guide](../../../artifacts/review-packages/bit-manipulation/README.md)
identifies algorithm-atlas-bit-manipulation-review.zip, its .zip.sha256 and
algorithm-atlas-bit-manipulation-review.json. Source payload includes the complete
updated repository source, catalog, documentation, tests and historical reports,
with current evidence. It excludes .git, environments, caches, binaries, secrets
and nested review ZIPs/unnecessary package sidecars including its own artifacts.
Historical package bytes remain intact locally.

The external JSON records actual language/full-suite results, Phase 10/category/
counts/timestamp, pending owner approval, source hashes, required paths, safe ZIP
entries, CRC, SHA-256, source-export tests and extracted checks. Archive checks run
after finalizing this report; external metadata is the observed record and avoids
a circular archive hash.

**STOP for MD.Khalid Hasan's explicit Phase 10 review and approval.** No Phase 11,
other category, commit, push or publication was performed or authorized.
