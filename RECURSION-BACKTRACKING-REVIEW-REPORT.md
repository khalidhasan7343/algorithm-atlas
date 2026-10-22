# Phase 3 — Recursion & Backtracking review report

**Implementation/testing complete; awaiting explicit owner review. Phase 3 is not human-approved.**

The owner approved Phase 2 and authorized only these nine catalog A3 topics.
All three sequential internal batch gates passed before the next batch began.
No A5 Graph Algorithms or other category implementation, commit, push, or
publication was performed. Maintainer: **MD.Khalid Hasan**; MIT attribution is
preserved.

## Completed deliverables

Each canonical folder contains an authored README with all 25 required numbered
sections; standalone Python and C++17/C++20 implementations; and executed Python
and C++ API/CLI tests. Lessons include exact contracts, pseudocode, invariants,
worked traces, reproducible examples, applications, complexity, comparisons,
limitations, questions, exercises, references, and attribution.

| Algorithm / canonical folder | Python cases | C++17 cases | C++20 cases | Total |
| --- | ---: | ---: | ---: | ---: |
| [Permutations](dsa/recursion-and-backtracking/permutations/README.md) | 20 | 2 | 2 | 24 |
| [Combinations](dsa/recursion-and-backtracking/combinations/README.md) | 24 | 2 | 2 | 28 |
| [Power Set Generation](dsa/recursion-and-backtracking/power-set-generation/README.md) | 20 | 2 | 2 | 24 |
| [N-Queens](dsa/recursion-and-backtracking/n-queens/README.md) | 4 | 2 | 2 | 8 |
| [Sudoku Solver](dsa/recursion-and-backtracking/sudoku-solver/README.md) | 5 | 3 | 3 | 11 |
| [Rat in a Maze](dsa/recursion-and-backtracking/rat-in-a-maze/README.md) | 3 | 2 | 2 | 7 |
| [Graph Coloring](dsa/recursion-and-backtracking/graph-coloring/README.md) | 4 | 2 | 2 | 8 |
| [Hamiltonian Path](dsa/recursion-and-backtracking/hamiltonian-path/README.md) | 3 | 2 | 2 | 7 |
| [Subset Sum using Backtracking](dsa/recursion-and-backtracking/subset-sum-backtracking/README.md) | 4 | 2 | 2 | 8 |
| **Category total** | **87** | **19** | **19** | **125** |

Counts are collected pytest cases. Several cases internally execute hundreds or
thousands of exhaustive/seeded vectors, so these counts are not input-vector
counts. Per-algorithm logs are retained in the evidence directory. C++ tests
compile and run API drivers and standalone programs; compilation alone is not
counted as behavioral validation.

## Defined behavior and correctness coverage

- **Permutations:** ascending original-index DFS; positional identity; n! rows,
  including repeated value rows when input values repeat; empty input `[[]]`.
- **Combinations:** exactly k increasing input indices, lexicographic index-tuple
  order; repeated value rows remain distinct positional choices; k=0 `[[]]`,
  k>n `[]`, negative k invalid.
- **Power Set Generation:** exclude before include; lexicographic binary-choice
  vectors; input-order rows; duplicates preserve positional multiplicity;
  empty input `[[]]`.
- **N-Queens:** all row-to-column vectors, columns tried ascending; separate
  reflected/rotated placements; n=0 `[[]]`, n=1 `[[0]]`, n=2/3 `[]`.
- **Sudoku Solver:** standard 9×9 only, 0 blank; validate shape/range and row,
  column, box contradictions before search. Return the first row-major,
  digit-ascending completion; consistent impossible boards return null.
  Contradictory givens are invalid, not an unsatisfiable search result.
- **Rat in a Maze:** all simple top-left to bottom-right routes in rectangular
  binary grids; D/L/R/U DFS; no cell revisits; empty grid no route; open singleton
  one zero-move route. Bounds checked before C++ index subtraction.
- **Graph Coloring:** square symmetric binary undirected matrix; first
  lexicographic fixed-palette coloring. Disconnected components reuse colors;
  self-loops are valid but unsatisfiable. Empty graph has empty coloring.
- **Hamiltonian Path:** directed or symmetric undirected binary matrix; first
  lexicographic vertex-once path over all starts. No closing edge is required;
  self-loops do not help; empty graph has the vacuous path.
- **Subset Sum using Backtracking:** first include-before-exclude index subset,
  checking the current sum before branching. Target 0 returns the empty subset.
  Signed/zero/repeated values supported; no invalid positive-only pruning.
  C++ separates exact positive/negative two-word unsigned magnitudes, avoiding
  signed prefix overflow and signed negation of LLONG_MIN.

Every algorithm keeps working state local, owns its output, and leaves caller
inputs unchanged. Successful search branches undo trial state before returning.
Python integer fields require native int (bool/subclasses excluded); C++ APIs
use typed containers and long long payloads. Invalid domain inputs raise
ValueError/invalid_argument, Python invalid field types raise TypeError, and CLI
errors produce nonzero exit/stderr with no result. Resource exhaustion is never
reported as an impossible-problem answer.

Independent expectations include itertools positional enumeration, bit-vector
subsets, permutation-filtered N-Queens and Hamiltonian paths, Cartesian-product
colorings, a Sudoku MRV/set solver and known completions, nonrecursive move-string
maze enumeration, and ranked index subsets with arbitrary-precision sums.
Regressions cover duplicate inputs, empty/singleton/impossible/multiple solutions,
repeated calls, mutable result independence, malformed CLI/shape/range data,
directed starts away from vertex 0, Sudoku contradictions, and signed/unsigned
word-boundary cancellation in subset sums.

## Actual local validation results

Environment: macOS 27.0.1 arm64; Python 3.14.2; pytest 9.1.1; Apple Clang 21.0.0
(the local g++ command invokes Apple Clang). Exact version output is saved in
[environment evidence](docs/recursion-backtracking-evidence/environment.json).
Each child command was bounded by 180 seconds; API execution tests additionally
use 30-second limits and compiler calls use 60-second limits.

| Gate | Actual result |
| --- | --- |
| Batch 1 individual suites | 24 + 28 + 24 = 76 passed |
| Batch 1 full repository | 1,148 passed in 86.37s |
| Batch 2 individual suites | 8 + 11 + 7 = 26 passed |
| Batch 2 full repository | 1,174 passed in 94.27s |
| Batch 3 individual suites | 8 + 7 + 8 = 23 passed |
| Final backtracking-python | 87 passed, 38 deselected in 2.25s |
| Final backtracking-cpp17 | 19 passed, 87 deselected in 12.34s |
| Final backtracking-cpp20 | 19 passed, 87 deselected in 13.61s |
| Final infrastructure | 200 passed in 2.07s |
| Final full-suite | 1197 passed in 100.12s (0:01:40) |
| C++20 AddressSanitizer + UndefinedBehaviorSanitizer | 19 passed, 87 deselected in 16.78s |
| README example execution | 18/18 Python and C++20 executions matched exact JSON |
| Catalog / local documentation links | Passed; all 235 canonical records and 35 categories validated |
| Generated-document drift check | Passed |
| Approved-file / catalog preservation | 87 approved files byte-identical; all identities and out-of-scope catalog records unchanged |

No failed, skipped, errored, or timed-out test cases occurred in the successful
batch/final runs. Marker deselection in language-specific runs selects the
intended language; it does not claim the deselected cases ran there. Sanitizers
cover the Phase 3 C++ tests; they are additional executions of those cases,
not additional unique tests. The full result is **1,197 passed in 100.12s**:
556 Sorting + 316 Searching + 125 Recursion/Backtracking + 200 infrastructure.

See [batch checkpoints](docs/recursion-backtracking-checkpoints.md),
[final command records](docs/recursion-backtracking-evidence/revalidation/final-results.json),
[sanitizer records](docs/recursion-backtracking-evidence/revalidation/sanitizer-results.json),
and [evidence instructions](docs/recursion-backtracking-evidence/README.md).
Configuration/link checks are rerun after this report and the final documentation
edits; their exact transcripts are in `revalidation/configuration-results.json` and matching
text files. Original batch/final evidence remains in the parent directory. No hosted GitHub Actions run was triggered or verified. Local testing
does not establish passes on Ubuntu/GCC or all four configured Python versions.

The renewed implementation/requirements audit is recorded in
[requirements-audit.md](docs/recursion-backtracking-evidence/revalidation/requirements-audit.md).
It verified the nine source contracts, all 25 README headings per topic, required
source/test files, and the critical edge-case coverage. No new algorithm defect
was identified; the changes since the initial handoff restore historical report
links and make the review package complete. The three recovered originals and
recovery hashes are included. Phase 3 remains awaiting the owner's review.

## Files changed and structure

All nine existing canonical lesson files were replaced with complete lessons;
18 implementation files and 18 test modules were added. Six `tests/cases.py`
files hold independent oracles/fixtures for Batches 2/3. A category conftest
provides import-safe loading and temporary C++ API/CLI drivers.

```text
dsa/recursion-and-backtracking/
├── README.md                         # generated category navigation
├── conftest.py                       # shared test-only fixtures
└── <each of the nine catalog IDs>/
    ├── README.md                     # all 25 sections
    ├── python/solution.py
    ├── cpp/solution.cpp
    └── tests/
        ├── test_python.py
        ├── test_cpp.py
        └── cases.py                  # six Batch 2/3 topics
```

Shared updates include catalog statuses/notes and development metadata,
`docs/progress.md`, the algorithm index and category index; README,
AGENTS, CONTRIBUTING, development/getting-started guides; batch checkpoint;
validator/generator Phase 3 support and 13 meaningful metadata/progress regression
cases. New scripts run bounded gates, verify scope and examples, and build/verify
the review snapshot. Existing CI, root pytest fixtures, dependency configuration,
license, and approved Sorting/Searching algorithms/tests/individual lessons are
preserved. Five historical report links in four documentation files were restored to the recovered originals.

The complete changed-file inventory is
`docs/recursion-backtracking-evidence/changed-files.txt` (repository-relative
source/evidence files, excluding the ZIP and its sidecars). The archive's
verification JSON lists every included file and its SHA-256.

## Defects fixed and known limitations

The first catalog gate found **five broken links to three historical reports**
absent from the clean starting checkout. All three originals have since been
restored: [Sorting review](SORTING-REVIEW-REPORT.md),
[Sorting final audit](SORTING-FINAL-AUDIT-REPORT.md), and
[Searching review](SEARCHING-REVIEW-REPORT.md). The two Sorting reports were
recovered byte-for-byte from Git revision `902167999dd002558e33f2fb7009e2fb8e15b87c`;
the Searching report was recovered from its recorded original creation and
updates in the local project session history. No historical results were invented.
The five documentation links now point to the restored originals. The initial
failed transcript remains `initial-missing-historical-reports.txt` as historical
evidence. The refreshed Phase 3 archive includes all three reports.

No algorithm test failure required changes to approved implementations. New
Phase 3 regression coverage explicitly protects restoration, input preservation,
invalid-given validation, positional duplicate behavior, directed boundaries,
and overflow/cancellation cases.

- Exhaustive enumeration is factorial/exponential, eager, and intended for small
  inputs. Large cases can exhaust runtime, memory, Python recursion depth, or
  C++ stack resources. No deadline/cancellation or streaming contract is supplied.
- Positional selection APIs deliberately retain repeated value rows; unique
  multiset results would require a separately specified variant.
- Sudoku returns one completion, without uniqueness certification; fixed
  row-major search can be slow on hard puzzles. Only standard 9×9 is supported.
- Coloring finds one fixed-palette assignment, not the chromatic number;
  Hamiltonian Path finds one path, without cost minimization or cycle closure.
- Subset Sum returns the first DFS witness, not a minimum-cardinality witness.
  C++ requires 64-bit long long and at most 64-bit size_t for its documented exact
  magnitude bound (compile-time checked); Python integers are unbounded.
- Remote CI and other operating systems/compiler/interpreter versions remain
  unverified locally. No known incomplete Phase 3 implementation requirement is
  being marked complete.
- The preexisting Dynamic Policy Optimization terminology blocker remains
  unchanged and outside this phase; the intended reference is an owner decision.

## Catalog and approval state

The catalog retains 256 syllabus memberships, 235 canonical topics, and 35
categories. Now **26 topics are complete**, 208 planned, and one blocked (209
remaining). All nine A3 documentation statuses are implemented; Python/C++/tests
are tested. Development is `awaiting-review`, completed_batches `[1,2,3]`, with no
active batch. No Phase 3 topic is marked human-reviewed or approved.

## Review package

Requested artifact: `algorithm-atlas-recursion-backtracking-review.zip`, with
`.zip.sha256` and `.zip.verification.json` sidecars. The ZIP contains the entire
current repository source/documentation/configuration/evidence snapshot under
`algorithm-atlas/`, including this report and preserved prior algorithms. It
excludes Git internals, environments, caches, binaries/build outputs, private
configuration/credential files, OS/editor metadata, and other archives/sidecars.
Known credential filename filters and high-confidence credential-pattern scans
are part of packaging.

`python scripts/package_backtracking_review.py` creates a new snapshot and refuses
to overwrite an existing artifact. It verifies required files, exact source
bytes, complete safe/unique relative paths, explicit directory entries, no
symlinks, ZIP CRC integrity, and SHA-256; it extracts a temporary copy and reruns
catalog/link validation plus the generated-document check. The sidecar records
actual archive byte/file/directory counts and extracted validation output after
packaging. It is external to the archive to avoid a self-hash dependency.

Verify the checksum from the repository root with:

```sh
shasum -a 256 -c algorithm-atlas-recursion-backtracking-review.zip.sha256
```

**STOP: please review Phase 3 and explicitly approve any further category work.
Passing tests does not authorize Graph Algorithms or another phase. No commit,
push, publication, or further-category implementation is authorized.**
