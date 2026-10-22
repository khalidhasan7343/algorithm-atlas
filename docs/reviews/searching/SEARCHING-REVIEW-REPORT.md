# Phase 2 — Searching Review Report

**Author and maintainer: MD.Khalid Hasan** · MIT licensed · 2026-10-21

## Completion and approval boundary

**All six Searching algorithms are implemented, documented, and tested.** Phase
1 (Sorting) was reviewed and approved by the owner in the instruction authorizing
this phase. Phase 2 is **awaiting human review**, not automatically approved.
No other-category algorithm was implemented. No commit, push, or publication
was performed.

Batch 1 completed its algorithm, catalog/documentation, and full-suite gate
before Batch 2 implementation began. Actual evidence is retained under
[docs/searching-evidence](../../searching-evidence/README.md); the durable resume
record is [Searching checkpoints](../../searching-checkpoints.md).

## Completed algorithms and original individual runs

Every algorithm has its own 25-section lesson, standalone Python and C++ CLI,
reusable API, independent expected-result tests, and executed C++17/C++20 tests.

| Batch | Algorithm | Individual suite result | Distinctive behavior verified |
| --- | --- | --- | --- |
| 1 | [Linear Search](../../../dsa/searching/linear-search/README.md) | 43 passed in 3.65s | Unordered data, equality-only records, first match and early return |
| 1 | [Binary Search](../../../dsa/searching/binary-search/README.md) | 52 passed in 3.42s | First-match lower bound, safe half-open midpoint, comparison budget |
| 1 | [Jump Search](../../../dsa/searching/jump-search/README.md) | 53 passed in 3.53s | Square-root blocks, capped final block, duplicates across blocks |
| 2 | [Interpolation Search](../../../dsa/searching/interpolation-search/README.md) | 62 passed in 3.59s | Equal endpoints, native integer contract, exact full-width arithmetic, skew and plateaus |
| 2 | [Exponential Search](../../../dsa/searching/exponential-search/README.md) | 53 passed in 3.45s | Expansion around powers of two, safe saturation, first duplicate within bracket |
| 2 | [Ternary Search](../../../dsa/searching/ternary-search/README.md) | 53 passed in 3.33s | Two-pivot sorted lookup, tiny intervals, earliest duplicate across pivots |

The six suites total **316 pytest cases**. Each test may check many generated
inputs internally; those inputs are not counted as extra pytest cases.

Each folder follows:

```text
dsa/searching/<algorithm-id>/
├── README.md                 # all 25 required numbered sections
├── python/solution.py
├── cpp/solution.cpp
└── tests/
    ├── test_python.py
    └── test_cpp.py
```

## Input, output, and duplicate contracts

All searches return the **first matching zero-based index**. Python returns -1
for absence. C++ returns `std::optional<std::size_t>` with `std::nullopt` for
absence, avoiding signed narrowing of a potentially large index. Both CLIs print
the index or -1, followed by one newline. Index zero is a valid match.

The CLI format is **target first, followed by zero or more values**, with no
length prefix. Input `7` searches an empty sequence and prints -1; empty stdin
is an error because the target is missing. Signed ASCII decimal integers are
accepted. Parsing and order validation finish before any result is printed.
Malformed tokens and C++ out-of-range integers produce nonzero exit, stderr,
and no partial result. Python CLIs support large decimal integers within resources.

Linear Search uses equality and accepts unordered input. Binary, Jump,
Exponential, and Ternary use equivalence under a consistent strict `<` ordering
and support generic compatible records. Their input must be nondecreasing and
support constant-cost random access for the stated search bounds.

Interpolation accepts integer keys only: exact native Python ints (excluding
bool/subclasses), or full signed 64-bit C++ long long. Its Python target type is
checked in every mode, including empty/unchecked calls.

All five sorted APIs validate adjacent order by default. Python uses keyword
`validate=False`, C++ third argument `false`, to skip the full scan **only for
already-validated input**. Python requires a genuine bool switch. Skipping the
scan transfers responsibility for order, type, and comparator preconditions to
the caller; it is not support for unordered data. No algorithm sorts or mutates
the supplied collection.

## Actual grouped and full-suite results

| Run | Observed result |
| --- | --- |
| Searching Python | **290 passed**, 26 C++ cases deselected, 3.03s |
| Searching C++17 | **13 passed**, 290 Python cases deselected, 7.04s |
| Searching C++20 | **13 passed**, 290 Python cases deselected, 8.03s |
| Infrastructure | **187 passed** in 2.04s |
| Full repository | **1,059 passed** in 72.63s; zero failures or skips |
| Batch 1 full gate | **891 passed** in 64.85s before Batch 2 began |

The final total is **556 existing Sorting + 316 Searching + 187 infrastructure**.
It contains **961 Python cases and 98 compiled/executed C++ cases** across both
standards. The 12 new infrastructure cases protect Searching checkpoint claims
and generated progress. Deselection in a language group is intentional selection,
not a skip or an extra pass. Every recorded command completed within its
180-second timeout; no timed-out run is reported as passing.

The 13 C++ cases per standard comprise two API/CLI cases for each algorithm plus
Interpolation's independent full-width ratio test. Compilation alone is never
counted as execution. API drivers and CLIs run with explicit subprocess limits.

Environment: Python **3.14.2**, pytest **9.1.1**, PyYAML **6.0.3**, Darwin 27.0.0
arm64, **Apple Clang 21.0.0**. On this host `g++` is Apple Clang; no separate GNU
GCC pass is claimed. See [environment.json](../../searching-evidence/environment.json).
Hosted GitHub Actions was not triggered or observed. The existing workflow
automatically discovers Searching tests and configures Python 3.11–3.14 with
GNU g++ on Ubuntu; those remote environments remain unexecuted in this task.

## Sanitizer results

Sanitizer evidence is recorded in
[sanitizer-results.json](../../searching-evidence/sanitizer-results.json) and its
adjacent transcript. The command instruments **all Searching C++20 tests** with
AddressSanitizer and UndefinedBehaviorSanitizer, with recovery disabled so a
finding fails execution:

```sh
CXX='clang++ -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all' .venv/bin/python scripts/run_searching_validation.py --stage sanitizer
```

Actual outcome: **13 passed, 290 deselected in 12.04s**, exit zero, no diagnostics
or timeout. All six APIs/CLIs and the independent ratio-helper executable ran.
This does not claim instrumentation of unselected Python/C++17 tests or other
compiler/platform combinations.

## Correctness and independent test coverage

- Every algorithm is implemented directly. Linear's scan, Binary's lower-bound
  loop, Jump's blocks/local scan, Interpolation's arithmetic probes,
  Exponential's doubling/binary narrowing, and Ternary's two pivots are visible
  in their own solutions. Built-in searches or sorting do not replace them.
- Empty/singleton, sorted/reversed where applicable, negative, zero, duplicates,
  missing values inside gaps and outside endpoints, and first/last positions are
  tested. Default sorted validation rejects disorder even after a possible early hit.
- Exhaustive tests generate all lengths 0–7 over `{-2,0,2}` and seven targets
  `-3..3`: 22,960 generated array/target combinations per algorithm per runtime.
  Sorted algorithms normalize the generated arrays first, so some normalized
  inputs repeat; the count is not a count of unique sorted arrays. Checked and
  unchecked paths are compared with an independent left-to-right oracle.
- Deterministic seed **20261022** covers lengths around powers of two, up to
  **65,537 items**. Python APIs also search keys up to **16,385 bits** in magnitude.
  Generic comparison APIs are exercised on less-than-only records with distinct
  identities and no default C++ constructor. Linear additionally accepts
  equality-only objects without ordering.
- All CLIs exercise missing target, signed tokens, whitespace, invalid syntax,
  embedded NULs, Unicode digits, and no partial output. C++ tests reject target
  and value overflows beyond signed bounds. Python CLIs execute 5,000-digit keys.
- Binary/Jump/Ternary comparison budgets protect their unchecked search behavior.
  Generic sorted tests confirm that checked mode adds exactly n-1 ordering
  comparisons to the same core, preventing hidden validation costs in the docs.
- Every documented shell example was actually compiled and executed: both
  Python and C++ produce the exact documented output. See
  [readme-examples.json](../../searching-evidence/readme-examples.json).

### Interpolation arithmetic and equal endpoints

Equal endpoints return the earliest possible match before division; outside-range
targets fail the guard. A successful probe saves its index and keeps searching
earlier positions, retaining first-match behavior. Skewed outliers and duplicate
plateaus exercise the linear worst case.

C++ distances are computed by defined unsigned subtraction after checking the
target is within the numeric range. The full LLONG_MIN..LLONG_MAX distance is
representable in uint64_t without evaluating overflowing signed subtraction.
The helper computes floor(a*b/d) without forming that product: quotient/remainder
updates process width bits and compare against d-r or d-a before addition.
The quotient never exceeds the processed width prefix. No floating conversion,
unsafe cast, or nonstandard 128-bit integer is used. The resulting offset is
bounded by the current interval length minus one.

**2,567 full-width/small-denominator helper cases per C++ standard** are checked
against Python's exact arbitrary-precision multiplication/division. Tests include
maximum size_t widths, maximum uint64_t distances, zero/full ratios, and 2,000
seeded random ratios. Public API tests additionally cover 100 random signed
64-bit tables, signed extrema, highly nonuniform gaps, and plateau duplicates.

### Exponential expansion and Ternary assumptions

Expansion checks `bound >= n-bound` before doubling, saturating at n without
overflow. Endpoints are read only while in range. Tests exercise lengths and
duplicate positions around powers of two, arithmetic near size_t maximum without
giant allocation, and a Python virtual range over **2^40 positions** with fewer
than 200 reads. This finite-length API does not claim an unbounded/infinite accessor.

Ternary is **sorted-sequence exact lookup**, not unimodal optimization. Tiny
intervals may have coincident pivots; branches still shrink safely and preserve
the first not-smaller boundary. Lengths around powers of three and duplicate
plateaus spanning both pivots are tested. A numerical optimizer would require
a separate unimodality/tolerance contract and was not added.

## Complexity and storage

Assume constant-time element comparisons and random access. The core bounds
exclude optional O(n) validation; checked default sorted APIs are Θ(n) on
accepted data for n>=2. CLI parsing/buffering has separate text and memory costs.

| Algorithm | Unchecked core best | Average / expected assumption | Core worst | API auxiliary slots |
| --- | --- | --- | --- | --- |
| Linear | Θ(1) | Θ(n), uniformly random unique successful rank | Θ(n) | O(1) |
| Binary | Θ(log(n+1)) for growing n | Same lower-bound narrowing | Θ(log(n+1)) | O(1) |
| Jump | Θ(1) | Θ(sqrt(n)), uniformly random unique successful rank | Θ(sqrt(n)) | O(1) |
| Interpolation | Θ(1) | O(log log n) probes under ideal uniform distinct keys | O(n), attainable with skew/duplicates | O(1) integer slots |
| Exponential | Θ(1) | Θ(log(n+1)), uniform unique successful rank | Θ(log(n+1)); position-sensitive O(1+log(p+1)) | O(1) |
| Ternary | Θ(log(n+1)) for growing n | Same two-pivot lower-bound narrowing | Θ(log(n+1)) | O(1) |

Here p is the first not-smaller insertion position, 0<=p<=n. Empty and singleton
inputs have constant work. Binary/Ternary deliberately continue past equality
to find a boundary, so the any-match O(1) midpoint-hit best case does not apply.
Python big-integer arithmetic/comparisons add bit-length costs; Interpolation
temporaries can occupy O(B+log n) bits for B-bit keys. Its C++ helper takes O(w)
operations per probe for size_t width w, a fixed constant on the tested platform.
All APIs avoid recursion and input copies; CLIs buffer O(n) value slots and text.

## Defects, regression protection, and limitations

No confirmed algorithm defect remains, and no failing test was suppressed or
marked complete. The new implementations passed their recorded gates; no
fictional defect/fix claim is made. Newly added edge tests protect against
off-by-one, first-duplicate, unsigned arithmetic, zero-denominator, and phase
metadata regressions. The generator's former Sorting-only authorization text was
updated to reflect the actual phase and generic planning boundaries.

Known limitations:

- Default validation makes sorted API calls linear. Callers can validate immutable
  data once and explicitly skip the scan for later queries; unchecked invalid
  input has no correctness guarantee.
- NaNs and inconsistent/side-effecting comparators violate the generic ordered
  contract; adjacent checking cannot establish a comparator's mathematical laws.
- Interpolation is integer-only, distribution-sensitive, and may degrade linearly.
  C++ requires full signed 64-bit long long; Python arbitrary precision is not
  constant-cost. No floating-key interpolation API is claimed.
- Exponential accepts finite known-length sequences. Ternary accepts sorted
  lookup data and provides no function optimizer. Jump is educational and does
  not promise to outperform Binary Search or implement a disk/block index.
- Verification is bounded exhaustive/random testing plus source analysis, not a
  formal proof of all inputs. Only the stated local compiler/interpreter/platform
  ran; remote CI and other environments are not claimed.
- The unrelated Dynamic Policy Optimization topic remains blocked pending its
  defining reference. No Searching requirement is left incomplete.
- The older Sorting final-review ZIP is absent in the working tree. This task
  did not delete or restore it; older archives are excluded from this review
  package. Prior Sorting reports remain historical evidence.

## Catalog, documentation, and preservation

Catalog completion is **6/6 Searching, 17/235 canonical topics overall**; 217
remain planned and one is blocked, for 218 remaining. Original membership counts
remain 256 entries in 35 categories. Binary Search's other syllabus memberships
reuse its canonical Searching implementation.

Each Searching lesson has all 25 sections, including applications, pseudocode,
dry runs, comparisons, exercises, references, and attribution. Generator checks
pass for **260 managed pages**. The final configuration gate passed with
**299 Markdown files and 3,761 local links**, zero validation errors, and
**187 infrastructure tests passed in 2.38s**. Exact outcomes are in
`docs/searching-evidence/configuration-results.json` and its transcripts.

All **57 tracked Sorting per-algorithm lesson/source/test files** match the
starting commit byte for byte, including the independent Sorting audit tests.
The Sorting category navigation page only receives the generator's generic
authorization wording. No Sorting algorithm was modified. See
[inventory.json](../../searching-evidence/inventory.json) for file hashes and
Searching's required-file/section inventory. The MIT license and maintainer
attribution are preserved.

## Files changed

The complete path list is [files-changed.txt](../../searching-evidence/files-changed.txt).
The substantive changes are:

- Six authored Searching READMEs and **24 new Python/C++ implementation/test files**.
- `catalog.yaml`: Phase 2 scope, two batches, accurate six-topic statuses/notes,
  checkpoint and completion-report path. No automatic Phase 2 reviewed status.
- `docs/progress.md`, `docs/algorithm-index.md`, Searching/category indexes and
  other managed planning READMEs regenerated. The broad generated-doc diff
  replaces obsolete hardcoded Sorting-only authorization wording with a pointer
  to current progress; it adds no other-category implementation.
- `AGENTS.md`, `CONTRIBUTING.md`, root README, `docs/development.md`, and
  `docs/getting-started.md`: owner Sorting approval and current Searching boundary.
- `scripts/generate_catalog_docs.py` and `scripts/validate_catalog.py`: Searching
  progress and truthful two-batch validation; existing Sorting checks preserved.
- Two infrastructure test files: **12 new tests** for checkpoint and generator
  behavior. Existing Sorting tests remain unchanged.
- `scripts/run_searching_validation.py`, `docs/searching-checkpoints.md`, this
  report, and `docs/searching-evidence/`: bounded reproducible gates and actual logs.
- `artifacts/review-packages/searching/algorithm-atlas-searching-review.zip` plus external SHA-256 and verification
  sidecars: final review artifacts, not recursively included in the ZIP.

## Reproduce the checks

From the root, use the existing `.venv`, or install `requirements-dev.txt` in
a Python 3.11+ environment with an available C++17/C++20 compiler:

```sh
.venv/bin/python scripts/run_searching_validation.py --stage batch1
.venv/bin/python scripts/run_searching_validation.py --stage batch2
.venv/bin/python scripts/run_searching_validation.py --stage final
CXX='clang++ -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all' .venv/bin/python scripts/run_searching_validation.py --stage sanitizer
.venv/bin/python scripts/run_searching_validation.py --stage configuration

# Direct required checks:
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python -m pytest --require-cpp
git diff --check

# Final archive integrity, from the directory containing the deliverables:
(cd artifacts/review-packages/searching && shasum -a 256 -c algorithm-atlas-searching-review.zip.sha256)
.venv/bin/python -m zipfile -t artifacts/review-packages/searching/algorithm-atlas-searching-review.zip
```

The runner records expanded child commands, exit codes, elapsed times, explicit
180-second timeouts, compiler flags, and stdout/stderr. Batch 1 also runs the
full suite; Batch 2 runs its three suites and catalog/generated checks; final
runs Python/C++17/C++20, infrastructure, full suite, and both validation scripts.
Re-running commands replaces their corresponding logs. C++ compilation has a
60-second timeout, API execution 30 seconds, CLI/helper subprocesses 10 seconds.

## Review package and mandatory stop

`artifacts/review-packages/searching/algorithm-atlas-searching-review.zip` contains the updated repository, all
Sorting and Searching source/tests, catalog, docs, infrastructure, CI files,
this report, and test evidence under an `algorithm-atlas/` directory.
Git metadata, virtual environments, caches, binaries, build outputs, temporary
files, credentials/private keys, and older ZIPs/sidecars are excluded.

Packaging verification checks CRC, duplicate/path-traversal entries, symlinks,
required files, exact archive/source bytes, and high-confidence credential
patterns. An extracted copy runs catalog and generated-doc checks. The external
verification JSON includes the complete archive file-hash inventory and check
outputs. The separate SHA-256 covers the finished ZIP, avoiding a circular
checksum inside this report. Pattern scanning is not a proof that every arbitrary
secret string is detectable.

**READY FOR HUMAN REVIEW. STOP after this handoff.** Wait for the owner's explicit
review and approval. No other category, commit, push, or publication is authorized.
