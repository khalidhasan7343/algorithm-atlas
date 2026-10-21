# Sorting Final Independent Audit

Maintainer: **MD.Khalid Hasan** · Audit date: **2026-10-21** · MIT licensed.

## 1. Executive summary

**All 11 Sorting algorithms passed independent verification. The full repository
suite completed: 731 passed in 41.19 seconds, zero failures or skips.** Selected
C++20 AddressSanitizer and UndefinedBehaviorSanitizer tests also passed: 14 passed
in 13.48 seconds, no diagnostics. Every bounded command finished; none timed out.
Human approval remains pending.

This audit reviewed both sources and lessons for all 11 algorithms, ran their
original suites separately first, added independent exhaustive/randomized
oracles, then executed the required groups and full suite. It found one confirmed
documentation mismatch and no sorting correctness defect. All 22 implementation
files are unchanged from the baseline commit in the
[environment record](docs/audit-evidence/environment.json).

The repository is packaged as `algorithm-atlas-sorting-final-review.zip`, with
388 regular files, 319 explicit directory entries, and an `algorithm-atlas/`
top-level directory. The checksum is supplied alongside the
ZIP, avoiding a self-referential report checksum. No Searching or other-category
implementation, commit, push, publication, or human approval was performed.

## 2. Algorithm-by-algorithm audit results

The original suites ran **before adding independent tests**. Each command was
`python -m pytest -q --require-cpp dsa/sorting/<id>/tests`, using `.venv/bin/python`,
both C++ standards, and a 120-second outer timeout. All rows completed with no
failure, skip, or timeout. Timings are pytest's reported times; complete
[individual records](docs/audit-evidence/individual-results.json) and adjacent
`.txt` transcripts are included.

| Algorithm | Original suite | Source and lesson audit conclusion |
| --- | --- | --- |
| Bubble Sort | 36 passed, 3.42s | Strict adjacent swaps and early exit are correct; stable. Corrected the README's C++ parser description. |
| Selection Sort | 36 passed, 3.43s | Minimum suffix scan and optional swap are correct; quadratic comparisons and tagged instability agree with the lesson. |
| Insertion Sort | 34 passed, 3.46s | Saved item and strict shifts preserve ties; inversion-sensitive cost and tagged trace agree. |
| Merge Sort | 20 passed, 3.07s | Half-open ranges, exhaustion guards, shared buffer, and left-on-tie merge are correct; ordered data still merges. |
| Quick Sort | 34 passed, 3.09s | Three-way invariant, saved pivot, and smaller-side recursion are correct. Added a minimum-pivot adversary and actual Python call-depth measurement. |
| Heap Sort | 22 passed, 2.93s | Bottom-up max heap and iterative sift are correct; early-stopping all-equal best case is linear; unstable extraction is documented. |
| Counting Sort | 52 passed, 3.87s | Negative offsets, inclusive range guard, cumulative counts, and reverse stable scatter are correct; near-extreme and full-span arithmetic is safe. |
| Radix Sort | 44 passed, 2.95s | Stable byte passes and signed encodings are correct: Python minimum offset; C++ unsigned sign-bit flip, eight passes, no minimum-value negation. |
| Bucket Sort | 110 passed, 3.11s | Finite closed `[0,1]` domain, endpoint clamping, stable insertion, and collection are correct; identity/signed-zero order is preserved. |
| Shell Sort | 23 passed, 2.90s | Knuth gaps, guarded subtraction, and gap-one final pass are correct; no unsupported tight average exponent is claimed. |
| Tim Sort | 69 passed, 3.55s | Strict descending reversal, classic minrun, upper-bound insertion, corrected four-run lookback, stable merge, and actual galloping are correct. |

These original runs total **480 pytest cases**, not 480 input vectors. Existing
tests meaningfully exercise large inputs, invalid values, less-than-only records,
stability/instability, CLI errors, and compiled API drivers. Independent checks
below supplement those tests; original passes alone did not establish the audit.

Every lesson implements its named method directly. Python `sorted`/`list.sort`
and C++ `std::sort`/`std::stable_sort` occur only as testing oracles, not algorithm
replacements. Tim's `_TimSorter.sort()` is its own implementation method.

## 3. Python test results

```text
python -m pytest -q --require-cpp dsa/sorting -m 'not cpp'
488 passed, 68 deselected in 5.75s
```

This includes 436 original plus **52 new Python cases**. Deselected C++ tests
were executed separately. See the [Python transcript](docs/audit-evidence/sorting-python.txt).

## 4. C++17 test results

```text
python -m pytest -q --require-cpp dsa/sorting -m cpp --cpp-standard=c++17
34 passed, 488 deselected in 18.33s
```

All 11 APIs and standalone CLIs compiled and executed, plus the independent
combined driver and additional CLI contracts: 22 original + 12 new C++17 cases.
Compilation uses `-std=c++17 -Wall -Wextra -pedantic`, with assertions enabled.
See the [C++17 transcript](docs/audit-evidence/sorting-cpp17.txt).

## 5. C++20 test results

```text
python -m pytest -q --require-cpp dsa/sorting -m cpp --cpp-standard=c++20
34 passed, 488 deselected in 21.21s
```

The same coverage compiled and executed with `-std=c++20`. See the
[C++20 transcript](docs/audit-evidence/sorting-cpp20.txt). On this host `g++` is
**Apple Clang 21.0.0**; this does not claim a separate GNU GCC run.

## 6. Infrastructure and full-suite test results

```text
python -m pytest -q --require-cpp tests
175 passed in 2.03s

python -m pytest -q --require-cpp
731 passed in 41.19s
```

The full suite is **556 Sorting + 175 infrastructure cases**: 659 Python and
72 compiled/executed C++ cases, including both standards and four toolchain
cases. The prior total was 655; the difference is exactly **76 new audit cases**.
No failures, skips, or timeouts occurred. Transcripts:
[infrastructure](docs/audit-evidence/infrastructure.txt),
[full suite](docs/audit-evidence/full-suite.txt).

Environment: Python 3.14.2, pytest 9.1.1, PyYAML 6.0.3, Darwin 27.0.0 arm64.
Hosted GitHub Actions was **not triggered or observed**. The existing workflow
configures Ubuntu, GNU `g++`, Python 3.11–3.14, catalog/link checks, generated docs,
and the full suite under both standards. Local results do not establish success
in those unexecuted environments.

## 7. Additional randomized and exhaustive testing

The [Python audit tests](dsa/sorting/tests/test_independent_audit.py) and
[C++ audit driver](dsa/sorting/tests/fixtures/independent_audit.cpp) add:

- **Integer exhaustive oracle:** all lengths 0–8 over `{-2,0,2}`: 9,841 vectors
  for each of ten integer sorts, **98,410 sorts per runtime**. Checks include
  input preservation, independent output storage, and an independent oracle.
- **Bucket exhaustive oracle:** all lengths 0–7 over `{0,.25,.5,1}`: 21,845
  vectors, each with automatic count and counts 1, 3, 7: **87,380 sorts per runtime**.
- The matrices perform **557,370 exhaustive sorts** across Python, C++17, and
  C++20. These inner checks are separate from pytest counts. Sanitizers repeat
  the C++20 matrix separately.
- **Seed `20261021`**, independent of the original `7343`: sorted, reversed,
  all-equal, and duplicate-heavy random patterns across 0/1/2, 31/32,
  63/64/65, 127/128/129, 257, and larger sizes. New tests use 512 items for
  Bubble/Selection/Insertion and 8,193 for the other integer sorts; existing Tim
  tests also execute 100,003 items.
- **Integer boundaries:** signed 64-bit extrema; Python 512/1,024/4,096-bit
  values; dense five-key Counting ranges around positive/negative `2**16384`;
  exact accepted/rejected range boundaries; C++ near both signed extrema and
  full-span rejection before allocation.
- **Stability:** distinguishable less-than-only records for Bubble, Insertion,
  Merge, and Tim against stable oracles; native equal integer object identities
  for Python Counting/Radix; numeric identities and signed zero for Bucket.
  C++ uses non-default-constructible tagged records for generic stable APIs and
  signed-zero bits for Bucket. Its integer-only Counting/Radix APIs do not
  expose tagged keys; scatter stability is also verified from traversal order.
- **Quick:** construct a permutation whose middle pivot is always the remaining
  minimum. Both languages correctly sort 256 items while exceeding `n²/2`
  comparisons. Python profiling asserts actual helper depth at most
  `ceil(log2(n))+2`. Source inspection establishes the general smaller-side
  recursion bound and saved-pivot safety; this test is not itself a proof for
  all permutations.
- **Tim:** 65,450 lower/upper-bound checks per runtime against `bisect` or standard
  bound functions, varying both subrange endpoints, empty ranges, ties, and
  outside pivots. Another 20,000 random run pushes per runtime check every
  decreasing-pair and sum-of-three invariant and interval adjacency after
  collapse. Original tests additionally execute adversarial real run patterns,
  minrun boundaries, descending equal plateaus, both gallop directions,
  overlapping equal keys, documented merge intervals, and galloping comparison
  budgets. This verifies actual galloping, not a renamed scalar merge.
- **CLI:** execute all 11 Python CLIs and both C++ builds on additional valid
  and invalid tokens. Cases include embedded NULs, mixed/doubled signs, Unicode
  minus, unsupported integer exponent syntax, incomplete real exponents,
  non-finite/out-of-domain Bucket values, and C++ signed overflow. Invalid
  inputs return nonzero, stderr, and no partial output. Expected valid values
  are independently computed within each documented contract.
- **Documentation:** explicit tests check all 11 dry-run final results, including
  Tim's 128-item trace. Intermediate transitions, pseudocode, examples, and
  stability witnesses were also reviewed against source.

## 8. Sanitizer results

```sh
CXX='clang++ -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all' \
  python -m pytest -q --require-cpp dsa/sorting/tests \
  dsa/sorting/tim-sort/tests -m cpp --cpp-standard=c++20
```

Actual outcome: **14 passed, 117 deselected in 13.48s**, no AddressSanitizer or
UndefinedBehaviorSanitizer diagnostics, exit zero, no timeout. Recovery is disabled
so an undefined-behavior finding must fail execution. This selects the
all-algorithm exhaustive/boundary driver, all 11 new CLI checks, and Tim's
original API/CLI checks. It is selected C++20 coverage, not every test/platform.
See the [transcript](docs/audit-evidence/sanitizer.txt) and
[structured result](docs/audit-evidence/sanitizer-results.json).

## 9. Bugs discovered and fixes applied

**One documentation defect; no confirmed sorting implementation defect.**
Bubble Sort's C++ section incorrectly named `std::from_chars`. The code validates
signed decimal grammar, calls range-checked `std::stoll`, checks full consumption,
and catches conversion failures. Its
[README](dsa/sorting/bubble-sort/README.md#14-c-implementation) now accurately
describes that behavior. Both standards and sanitizer runs pass overflow and
malformed-input checks. No parser or sorting code modification was necessary.

README/working instructions, catalog completion-report pointer, generated progress,
and saved checkpoint now identify this audit while preserving pending human review.

## 10. New regression tests

No implementation regression is claimed for a nonexistent code bug. The
documentation correction was verified against source and executing CLI tests;
a test asserting exact README wording would not test parser behavior.

The **76 new protective audit cases** comprise 52 Python and 12 C++ cases under
each standard. They cover exhaustive oracles, independently seeded inputs,
boundaries, identity stability, dry runs, Quick adversarial behavior/recursion,
Tim gallops/stack invariants, and CLI contracts. Their standalone run completed:
**76 passed in 14.66s**. Existing regression tests, including Tim's deeper-triple
collapse case, remain unchanged and passed again.

## 11. Complexity and stability verification

Bounds assume constant-cost operations and accepted nonempty input; lessons
separately discuss trivial sizes and big-integer costs. Every API copies its
output, so even constant-workspace cores require O(n) new storage overall.

| Algorithm | Best | Average assumption / bound | Worst | Core workspace beyond result | Stable? |
| --- | --- | --- | --- | --- | --- |
| Bubble | Θ(n) | Random distinct permutation: Θ(n²) | Θ(n²) | O(1) | Yes |
| Selection | Θ(n²) | Θ(n²), order independent | Θ(n²) | O(1) | No |
| Insertion | Θ(n) | Random distinct permutation: Θ(n²) | Θ(n²); generally Θ(n+I) | O(1) | Yes |
| Merge | Θ(n log n) | Θ(n log n) | Θ(n log n) | O(n) buffer + O(log n) stack | Yes |
| Quick | Θ(n), all equal | Random distinct permutation: Θ(n log n) | Θ(n²) | O(log n) stack | No |
| Heap | Θ(n), all equal | Random distinct permutation: Θ(n log n) | Θ(n log n) | O(1), iterative | No |
| Counting | Θ(n+k) for fixed n,k | Θ(n+k) | Θ(n+k) | O(k); Python also copies input | Stable scatter; integer API |
| Radix | Θ(d(n+256)) | Θ(d(n+256)) | Θ(d(n+256)) | O(n+256), plus Python key payloads | Stable scatter; integer API |
| Bucket | Θ(n+k) | IID uniform continuous: Θ(n+k+n²/k) | Θ(n²+k) | O(n+k) | Yes |
| Shell | Θ(n log n) | No universal tight average claimed | O(n^(3/2)), Knuth gaps | O(1) | No |
| Tim | Θ(n), one natural run | Random distinct permutation: Θ(n log n) | O(n log n) | O(n) buffers + O(log n) pending stack | Yes |

`I` counts strict inversions; `k` is the inclusive Counting key span or Bucket
count; `d` is byte count (eight in C++, data-width dependent in Python). Bucket's
order-sensitive bound is Θ(n+k+I) for within-bucket inversions: equal-key
concentration alone does not force quadratic work. Python arithmetic on arbitrary
integers is not constant-time. Source invariants and analysis support these
bounds; observed timings are not used as asymptotic proofs.

Knuth's bound agrees with the
[authors' Shell source](https://raw.githubusercontent.com/kevin-wayne/algs4/master/src/main/java/edu/princeton/cs/algs4/Shell.java).
The classic corrected Tim merge policy has the documented O(n log n) bound;
see [Auger et al.](https://arxiv.org/abs/1805.08612). This lesson uses classic
minrun/run-stack policy, copies both forward-merge runs, and fixes the gallop
trigger at seven wins. Current
[CPython design notes](https://github.com/python/cpython/blob/main/Objects/listsort.txt)
describe Powersort, smaller-run buffering, and an adaptive gallop threshold.
The repository does not claim to reproduce those production optimizations.

## 12. Documentation and catalog validation

All 11 folders contain the required 25 numbered lesson sections, both solutions,
and both original test files. Pseudocode, traces, applications, comparisons,
complexities, stability, and invalid-input contracts were reviewed.
[Source inventory](docs/audit-evidence/source-audit.json) records sections and hashes.

The grouped catalog check passed: **35 categories, 256 syllabus occurrences,
235 canonical topics, 295 Markdown files, 3,697 local links** at that stage of
report preparation. Generated docs passed: **266 pages, zero drift**. After
completing the report/evidence links, final checks passed with **296 Markdown
files and 3,719 local links**, and **266 generated pages, zero drift**; see
`docs/audit-evidence/final-configuration-checks.txt`. Internal targets and heading anchors are validated.
External URL availability is outside that validator, and not every external
reference was rechecked in this audit.

Catalog completion remains **11/11 Sorting, 11/235 canonical topics**, with
223 planned and one blocked DPO topic. Development remains `awaiting-review`,
all three batches are complete, and no human `reviewed` status was assigned.
The completion-report pointer targets this report; the original report remains
historical evidence.

## 13. Known limitations

- Bounded exhaustive/random testing plus source review is not a formal proof
  over all inputs. Local execution covers Python 3.14.2 and Apple Clang 21 on
  arm64; the hosted CI matrix remains unexecuted.
- Simple quadratic sorts and adversarial quadratic Quick Sort are intentional
  educational implementations, with the documented performance limits.
- Counting defaults to a 1,000,000-key cap; larger allowed allocations can fail.
  C++ Radix requires the full signed 64-bit `long long` range.
- Bucket requires finite `[0,1]` values and a suitable distribution for its
  expected bound. Python rejects count zero; C++ uses zero for automatic count.
  Huge bucket requests can exhaust memory. Floating CLI rounding, subnormals,
  underflow to signed zero, and printed approximations are documented behavior.
- Generic comparison APIs require consistent ordering and copyable C++ records;
  NaNs or side-effecting/inconsistent comparators do not provide that contract.
  Counting/Radix expose integer APIs, not generic tagged-key interfaces.
- Merge/Heap/Shell Python CLIs retain the interpreter's decimal digit conversion
  limit, as documented; their reusable APIs support arbitrary-size integers.
  Other integer CLIs disable that cap. All remain resource limited.
- Sanitizers covered selected C++20 tests. System-wide allocation exhaustion
  and every possible I/O/device failure were not simulated.
- Package exclusions and high-confidence credential scans cannot establish the
  absence of every possible arbitrary secret string.
- DPO's unrelated terminology question remains blocked for a future authorized
  category. No Sorting requirement is incomplete; human review remains required.

## 14. Files modified

Changes made by **this final audit**:

| Path | Change |
| --- | --- |
| `dsa/sorting/bubble-sort/README.md` | Corrected parser description only. |
| `dsa/sorting/tests/test_independent_audit.py` | Added 52 Python and parametrized C++ audit cases. |
| `dsa/sorting/tests/fixtures/independent_audit.cpp` | Added combined C++ oracle/boundary driver. |
| `scripts/run_sorting_verification.py` | Added separately logged individual/group/sanitizer runner. |
| `SORTING-FINAL-AUDIT-REPORT.md` | Added this report. |
| `AGENTS.md`, `README.md` | Updated audit links and pending-review checkpoint. |
| `catalog.yaml` | Updated completion-report path only; no approval/status promotion. |
| `docs/progress.md` | Regenerated the report pointer. |
| `docs/sorting-checkpoints.md` | Saved final verification checkpoint. |
| `docs/audit-evidence/` | Added actual transcripts, results, environment/source inventory, and guide. |
| `algorithm-atlas-sorting-final-review.zip`, `.zip.sha256` | Final package and external checksum; not recursively included. |
| `algorithm-atlas-sorting-final-review.zip.verification.json` | File-hash inventory, exclusions/integrity results, and extracted-copy check outputs; supplied outside the ZIP. |

Evidence files: 11 `<algorithm-id>.txt` transcripts; `individual-results.json`;
`sorting-python.txt`, `sorting-cpp17.txt`, `sorting-cpp20.txt`, `infrastructure.txt`,
`full-suite.txt`, `catalog.txt`, `generated-docs.txt`; `groups-results.json`;
`sanitizer.txt`, `sanitizer-results.json`; `environment.json`, `source-audit.json`,
`README.md`; and `final-configuration-checks.txt`. All are included in the ZIP.

All implementation and original test files remain unchanged. Pre-existing
uncommitted README, instructions, catalog, progress, and checkpoint changes were
preserved while updating this handoff. The existing deletion of the Phase 0 ZIP
and original review report/ZIP were not reverted or overwritten. Older ZIPs are
excluded from the new archive to avoid nesting generated archives.

## 15. Exact commands used to reproduce results

Run from the root using a Python 3.11+ environment with `requirements-dev.txt`
installed and a C++17/C++20 compiler available:

```sh
# Original suites separately first, each subprocess bounded at 120 seconds.
.venv/bin/python scripts/run_sorting_verification.py --stage individual --output docs/audit-evidence --timeout 120

# Required groups, followed by catalog/link and generated-document checks.
.venv/bin/python scripts/run_sorting_verification.py --stage groups --output docs/audit-evidence --timeout 120

# Standalone new audit suite: observed 76 passed in 14.66s.
.venv/bin/python -m pytest -q --require-cpp dsa/sorting/tests

# Selected sanitizer run, with compiler flags recorded in the result.
CXX='clang++ -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all' .venv/bin/python scripts/run_sorting_verification.py --stage sanitizer --output docs/audit-evidence --timeout 120

# Direct required checks; group runner above also executes these with -q.
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python -m pytest --require-cpp
git diff --check

# Archive integrity from the directory containing the deliverables.
shasum -a 256 -c algorithm-atlas-sorting-final-review.zip.sha256
.venv/bin/python -m zipfile -t algorithm-atlas-sorting-final-review.zip
```

[Group results](docs/audit-evidence/groups-results.json) record exact expanded
child commands, exit codes, elapsed times, 120-second timeouts, `timed_out: false`,
summaries, and compiler overrides. Compilation has a separate 60-second limit;
new exhaustive C++ executables 60 seconds and new CLI processes 10 seconds.
Original executable limits remain 10–20 seconds. No incomplete/timed-out run is
reported as passed.

Packaging checks cover ZIP CRC, unique safe relative paths, no symlinks, exact
regular-file inventory, required paths, and byte-for-byte source comparison.
A temporary extracted copy is checked with the same catalog and generated-doc
commands. The archive excludes `.git`, environments, caches, build outputs,
binaries, credentials/private keys, temporary files, and earlier ZIPs. It includes
configuration dotfiles, `.github`, all lessons/tests, and planned-category docs.
The external SHA-256 covers the finished ZIP.

## 16. Final recommendation

**READY FOR HUMAN REVIEW.** Independent verification completed with no unresolved
Sorting implementation defect. The confirmed documentation error is corrected;
reproducible tests and execution evidence accompany the repository.

**STOPPED — awaiting explicit maintainer review and approval.** No Searching,
other-category development, commit, push, publication, or automatic approval is
authorized by this report.
