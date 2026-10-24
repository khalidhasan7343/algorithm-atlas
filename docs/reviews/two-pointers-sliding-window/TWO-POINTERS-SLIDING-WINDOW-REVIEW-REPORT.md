# Phase 12 — Two Pointers and Sliding Window review report

Owner and maintainer: **MD.Khalid Hasan**. Repository: [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). MIT License.
Date: 2026-10-24 (Asia/Dhaka). **Implementation complete; owner approval pending.**

## Authorization and independent checkpoint

The owner officially approved completed Phase 10 on 2026-10-24 and explicitly
authorized combined Phases 11/12 in normal roadmap sequence. This message
supersedes the attachment's stale prerequisite; no second approval was requested.
Phase 9 approval remains preserved. Historical reports, evidence and ZIP metadata
retain their original handoff statements and bytes. The prior Phase 10 archive's
SHA-256 and CRC were actually verified in [approval evidence](../../two-pointers-sliding-window-evidence/approval-verification.json).

This report covers Phase 12 only. Its [checkpoint](../../two-pointers-sliding-window-checkpoints.md),
`development.phase_records['12']`, report, evidence, ZIP, checksum and JSON
are independent. Both implementations are finished; neither is human-reviewed
or owner-approved. The owner may approve either or both. No Phase 13, unrelated
category, staging, commit, push or publication occurred or is authorized.

## Exact scope and completion

3 catalog canonicals in A10; all implemented and tested. The
[pre-implementation locked scope](../../number-theory-window-scope.md) records
original status, canonical paths and related references. No new syllabus item,
category membership or duplicate canonical was added. Each canonical contains
its exact 25-section lesson, Python/C++ solution and executable language tests.

| Algorithm | Canonical ID | Canonical path | Status |
| --- | --- | --- | --- |
| Two Sum in Sorted Array | `two-sum-sorted-array` | [`dsa/two-pointers-and-sliding-window/two-sum-sorted-array`](../../../dsa/two-pointers-and-sliding-window/two-sum-sorted-array/README.md) | Implemented / Python and C++ tested |
| Sliding Window Maximum | `sliding-window-maximum` | [`dsa/two-pointers-and-sliding-window/sliding-window-maximum`](../../../dsa/two-pointers-and-sliding-window/sliding-window-maximum/README.md) | Implemented / Python and C++ tested |
| Longest Substring Without Repeating Characters | `longest-substring-without-repeating-characters` | [`dsa/two-pointers-and-sliding-window/longest-substring-without-repeating-characters`](../../../dsa/two-pointers-and-sliding-window/longest-substring-without-repeating-characters/README.md) | Implemented / Python and C++ tested |

## Executed validation

Internal stages: C (10 Two Sum tests) then D (all 30 category tests). Each stage completed its repository gate before
advancing; full Number Theory tests passed before Stage C. Stage logs and gate
JSON are retained in this category's evidence directory.

| Final selection | Actual result | Elapsed |
| --- | --- | --- |
| python | 12 passed, 18 deselected in 1.00s | 1.1s |
| cpp17 | 9 passed, 12 deselected in 3.36s | 3.48s |
| cpp20 | 9 passed, 12 deselected in 4.29s | 4.41s |
| full-suite | 1985 passed in 448.20s (0:07:28) | 448.38s |

The full-suite row is **one shared repository execution**, referenced by both
reports; it is not two independent runs. It includes all ten previously completed
categories, the two new categories and infrastructure tests, with required C++17
and C++20 compilation. [Final commands and logs](../../two-pointers-sliding-window-evidence/final-results.json)
record actual return codes, timeouts and durations. All final commands returned
zero; no failures, skips, missing compilers or timeouts occurred.

Catalog validation and relative Markdown links passed. Generated-document check
passed for all 180 generated pages. Infrastructure: 298 passed. See the
[configuration evidence](../../two-pointers-sliding-window-evidence/configuration-results.json).
Additional C++20 address/undefined-behavior sanitizers: **9 passed, 12 deselected in 7.59s**,
7.72s, using `g++ -fsanitize=address,undefined -fno-sanitize-recover=all`.
[Sanitizer record](../../two-pointers-sliding-window-evidence/sanitizer-results.json).
All lesson CLI examples executed in Python/C++17/C++20 and matched printed JSON:
3 lessons, 9 configurations. [Example results](../../two-pointers-sliding-window-evidence/examples-results.json).

## Independent oracle and randomized evidence

| Canonical | Valid oracle vectors per language configuration |
| --- | ---: |
| `two-sum-sorted-array` | 2436 |
| `sliding-window-maximum` | 1809 |
| `longest-substring-without-repeating-characters` | 1263 |

Fixed seeds: 12101, 12102, 12109. Vector counts are grouped
inside pytest tests; they are not additional pytest test counts. Invalid-input,
CLI, semantic consistency and maximum-boundary tests run separately.
[Inventory](../../two-pointers-sliding-window-evidence/oracle-inventory.json) and
[relationship matrix](../../two-pointers-sliding-window-evidence/oracle-matrix.json) record deterministic
coverage. Oracles contain no production imports. Production Python/C++ agreement
is checked in addition to independent mathematical/brute-force expectations.

Two Sum uses exhaustive original index-pair enumeration, including duplicates
and ties. Sliding maximum enumerates every complete window and every valid k
for small signed arrays. Longest distinct independently expands fresh seen sets
from each starting index and checks optimal interval/ties. Random tests supplement
exhaustive small alphabets. The relationship matrix adds 120 cases for each of
pair search, signed-window maxima and distinct byte intervals (seed 12109).

## Correctness and complexity audit

| Canonical | Time | Auxiliary space / invariant |
| --- | --- | --- |
| Two Sum | O(n), including sortedness validation | O(1); inward pointers safely eliminate impossible pairs |
| Sliding maximum | O(n) amortized, including validation | O(k) candidates plus O(n-k+1) output; increasing indices/decreasing values |
| Longest distinct substring | O(n) | O(256) last positions, constant-size interval output; valid half-open unique window |

Arrays and byte strings are limited to length 10000, array values to ±10^9 and
the Two Sum target to ±2*10^9. C++ addition uses int64; sums and JSON numeric
values remain within their documented domains. Python rejects bool/non-integer
operands. Inputs retain their order and are not mutated.

Two Sum validates nondecreasing order, returns zero-based indices or [], and
chooses the lexicographically earliest pair. Equality shrinks duplicate right
values to the first valid partner. Empty/single arrays return []. A brute-force
index-order oracle checks the complete tie rule, rather than only sum equality.

Sliding maximum accepts arbitrary signed values: no nonnegative-sum premise is
used. Each index enters and leaves the deque at most once; newer equal values
dominate older ones and expire later. Empty requires k=0; nonempty requires
1<=k<=n. Only complete windows are returned. Expiry arithmetic avoids unsigned
underflow and every candidate lies inside the current window.

Longest distinct substring uses Python bytes and C++ string treated as unsigned
bytes. It returns the earliest maximal [start,end) interval; empty is [0,0].
left=max(left,last[byte]+1) never moves backward, and strict improvement preserves
the earliest tie. All 256 byte values, NUL, repeats and UTF-8 encoded bytes are
tested. Offsets count bytes and can divide a multibyte character. Approved Phase 9
byte validation/hex transport is reused without changing its implementation.

## Repository preservation and integration

The inventory remains **35 categories / 256 memberships / 235 canonicals**.
There are now 97 completed, 137 planned and one blocked canonical. Dynamic Policy
Optimization remains blocked pending its intended reference; it was not renamed
or implemented. All out-of-scope algorithm catalog records are unchanged.
**1221 approved source/history files** matched their frozen SHA-256 baseline.
[Preservation record](../../two-pointers-sliding-window-evidence/preservation-results.json).
Historical review archives and sidecars remain intact in the workspace and are
intentionally omitted from new source ZIP payloads.

Both new reports exist, are nonempty/unignored and ready to track; all twelve
historical reports remain tracked. Both completion report pointers and independent
phase records are validated. No Git index mutation was made. See
[tracking results](../../two-pointers-sliding-window-evidence/tracking-results.json) and the complete
[changed-file manifest](../../two-pointers-sliding-window-evidence/changed-files.txt).
Changes are limited to the two category implementations, supporting validation,
current scope/approval navigation, generated documentation and review deliverables.
The primary completion pointer is Phase 11; `completion_reports` also identifies
Phase 12, with no combined report or third combined ZIP.

## Bugs fixed and limits

The initial Stage A infrastructure gate exposed 14 failures in a newly added
miniature catalog fixture because its docs directory was absent. Creating the
fixture directory fixed those failures. The original failed JSON/log are retained
in Number Theory evidence; no production algorithm failure was hidden and no
validator or test was weakened. Development boundary checks cover final-square
overflow, negative remainder normalization, duplicate pair ties and a left pointer
that must not move backward. Review-evidence generation also corrected an oracle
inventory lookup from a Number Theory-only helper to the actual window scope;
this did not change algorithms or test outcomes.

Contracts are bounded educational APIs, not arbitrary precision or unbounded
streaming services. The [shared conventions](../../two-pointers-sliding-window-conventions.md) state
exact ranges, invalid-input behavior, CLI grammar and language differences.
Local Python 3.14.2
on macOS/Apple clang is actual execution evidence. CI configuration remains
unchanged and local CI-equivalent gates passed. Hosted GitHub Actions and the
complete hosted Linux/Python-version matrix were **not triggered or verified**.
No unresolved blocker remains in this phase. Unrelated DPO clarification remains.

## Review package and reproduction

Deliverables live in [the package directory](../../../artifacts/review-packages/two-pointers-sliding-window/README.md):
`algorithm-atlas-two-pointers-sliding-window-review.zip`, `.zip.sha256` and `.json`.
The packager validates an exported source snapshot with catalog, generated docs,
preservation and infrastructure/category Python/C++17/C++20 tests before writing
the ZIP. It then verifies unique safe paths, exclusions, every file's bytes,
CRC and independently extracted catalog/docs/preservation/oracle relationships.
The external package JSON records the actual check outputs, SHA-256 and per-file
digests. It is outside the ZIP to avoid a circular checksum. No old archives or
other review ZIPs/sidecars are nested. Each archive is independently extractable.

From the repository root (or a fresh extracted root after creating a venv and
installing `requirements-dev.txt`), run:

```sh
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest dsa/two-pointers-and-sliding-window -m 'not cpp' -q
python -m pytest dsa/two-pointers-and-sliding-window -m cpp --cpp-standard=c++17 --require-cpp -q
python -m pytest dsa/two-pointers-and-sliding-window -m cpp --cpp-standard=c++20 --require-cpp -q
python scripts/verify_number_window_oracles.py --category two-pointers-sliding-window --check-only
python scripts/verify_number_window_scope.py --check-only --source-only
python -m pytest --require-cpp
```

From `artifacts/review-packages/two-pointers-sliding-window/` verify:

```sh
shasum -a 256 -c algorithm-atlas-two-pointers-sliding-window-review.zip.sha256
unzip -t algorithm-atlas-two-pointers-sliding-window-review.zip
```

`--source-only` skips exactly the omitted historical package files while verifying
all protected source bytes. Full workspace preservation uses the same script
without that flag. Reproduction commands do not grant further implementation or
publication authority. **STOP: Phase 12 owner approval is pending independently.**
