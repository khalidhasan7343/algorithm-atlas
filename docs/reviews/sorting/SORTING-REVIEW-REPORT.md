# Sorting Category — External Review Report

**Prepared:** 2026-10-21 (Asia/Dhaka)

**Project:** Algorithm Atlas

**Author and maintainer:** MD.Khalid Hasan

**Checkpoint:** all 11 Sorting algorithms complete and tested; **stopped for user review**.

Review archive: **`algorithm-atlas-sorting-review.zip`**, extracting into one `algorithm-atlas/` folder. The package includes the entire current source/documentation/configuration snapshot and this report. It excludes Git metadata, virtual environments, caches, builds, generated binaries, other ZIP artifacts, credentials, and recognized secrets. No Searching or other-category implementations were added, and no commit, push, or publication was performed while preparing this handoff.

## Completion summary

All three authorized internal batches are complete:

1. **Batch 1:** Bubble Sort, Selection Sort, Insertion Sort, Merge Sort.
2. **Batch 2:** Quick Sort, Heap Sort, Counting Sort, Radix Sort.
3. **Batch 3:** Bucket Sort, Shell Sort, Tim Sort.

Every algorithm has a dedicated canonical folder with a complete 25-section lesson, reusable runnable Python and C++ implementations, command-line examples, and comprehensive Python/C++ tests. The lessons cover motivation and real-world applications, prerequisites, correctness intuition, working steps, pseudocode, concrete dry runs, justified time/space analysis, limitations, comparisons, interview questions, practice exercises, references, and attribution.

| Algorithm and lesson | Batch | Python implementation | C++ implementation | Test files | Passing pytest cases |
| --- | ---: | --- | --- | --- | ---: |
| [Bubble Sort](../../../dsa/sorting/bubble-sort/README.md) | 1 | [Python](../../../dsa/sorting/bubble-sort/python/solution.py) | [C++](../../../dsa/sorting/bubble-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/bubble-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/bubble-sort/tests/test_cpp.py) | 36 |
| [Selection Sort](../../../dsa/sorting/selection-sort/README.md) | 1 | [Python](../../../dsa/sorting/selection-sort/python/solution.py) | [C++](../../../dsa/sorting/selection-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/selection-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/selection-sort/tests/test_cpp.py) | 36 |
| [Insertion Sort](../../../dsa/sorting/insertion-sort/README.md) | 1 | [Python](../../../dsa/sorting/insertion-sort/python/solution.py) | [C++](../../../dsa/sorting/insertion-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/insertion-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/insertion-sort/tests/test_cpp.py) | 34 |
| [Merge Sort](../../../dsa/sorting/merge-sort/README.md) | 1 | [Python](../../../dsa/sorting/merge-sort/python/solution.py) | [C++](../../../dsa/sorting/merge-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/merge-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/merge-sort/tests/test_cpp.py) | 20 |
| [Quick Sort](../../../dsa/sorting/quick-sort/README.md) | 2 | [Python](../../../dsa/sorting/quick-sort/python/solution.py) | [C++](../../../dsa/sorting/quick-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/quick-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/quick-sort/tests/test_cpp.py) | 34 |
| [Heap Sort](../../../dsa/sorting/heap-sort/README.md) | 2 | [Python](../../../dsa/sorting/heap-sort/python/solution.py) | [C++](../../../dsa/sorting/heap-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/heap-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/heap-sort/tests/test_cpp.py) | 22 |
| [Counting Sort](../../../dsa/sorting/counting-sort/README.md) | 2 | [Python](../../../dsa/sorting/counting-sort/python/solution.py) | [C++](../../../dsa/sorting/counting-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/counting-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/counting-sort/tests/test_cpp.py) | 52 |
| [Radix Sort](../../../dsa/sorting/radix-sort/README.md) | 2 | [Python](../../../dsa/sorting/radix-sort/python/solution.py) | [C++](../../../dsa/sorting/radix-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/radix-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/radix-sort/tests/test_cpp.py) | 44 |
| [Bucket Sort](../../../dsa/sorting/bucket-sort/README.md) | 3 | [Python](../../../dsa/sorting/bucket-sort/python/solution.py) | [C++](../../../dsa/sorting/bucket-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/bucket-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/bucket-sort/tests/test_cpp.py) | 110 |
| [Shell Sort](../../../dsa/sorting/shell-sort/README.md) | 3 | [Python](../../../dsa/sorting/shell-sort/python/solution.py) | [C++](../../../dsa/sorting/shell-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/shell-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/shell-sort/tests/test_cpp.py) | 23 |
| [Tim Sort](../../../dsa/sorting/tim-sort/README.md) | 3 | [Python](../../../dsa/sorting/tim-sort/python/solution.py) | [C++](../../../dsa/sorting/tim-sort/cpp/solution.cpp) | [Python tests](../../../dsa/sorting/tim-sort/tests/test_python.py), [C++ tests](../../../dsa/sorting/tim-sort/tests/test_cpp.py) | 69 |
| **Sorting total** | | **11** | **11** | **22** | **480** |

Each folder has this structure:

```text
<algorithm>/
├── README.md
├── python/solution.py
├── cpp/solution.cpp
└── tests/
    ├── test_python.py
    └── test_cpp.py
```

The implementations perform the named algorithms themselves rather than delegating their sorting work to Python's built-in sort or `std::sort`. Independent reference sorting is used in tests as an oracle. Tim Sort includes natural runs, strict descending reversal, classic minrun computation, stable binary insertion, corrected four-run stack collapse, and actual exponential/binary galloping. It is not a fixed-block merge sort labeled as Tim Sort.

## Actual validation results

Fresh command executed from the repository root on 2026-10-21:

```text
.venv/bin/python -m pytest --require-cpp
655 passed in 37.54s
0 failures; 0 skips
```

This is **480 Sorting cases plus 175 infrastructure cases**. C++ API and CLI checks compile and execute under both **C++17 and C++20**: 44 Sorting C++ cases plus four compiler-harness cases, or 48 C++ pytest cases in the full suite. The remaining 607 cases exercise Python behavior and repository tooling. Many seeded or exhaustive inputs run inside each pytest case; those inputs are not inflated into the collected-test count.

Tests cover empty/singleton inputs, duplicates, sorted/reverse data, negatives and integer extremes where applicable, unchanged inputs, generic comparable records, promised stability or documented instability, malformed/overflowing CLI input, randomized independent oracles, algorithm-specific constraints, range guards, gap transitions, minrun boundaries, galloping behavior, and run-stack regressions. The infrastructure suite also rejects overstated checkpoints, malformed metadata, unsafe document paths, broken links, and inconsistent artifacts/statuses.

| Additional check | Observed result |
| --- | --- |
| Catalog, structure, statuses, and relative documentation links | **Passed:** 35 categories, 256 syllabus entries, 235 canonical topics, 294 Markdown files, 3,696 local links; zero errors. |
| Generated catalog/index/progress documents | **Passed:** 266 generated pages; zero drift. |
| Algorithm README format | **Passed:** all 11 contain the exact 25 required numbered sections in order. |
| Implementation and test artifacts | **Passed:** 11 Python sources, 11 C++ sources, and 22 per-algorithm test files. |
| Implementation scope | **Passed:** zero Python/C++ algorithm source files in Searching or any other category. |
| Earlier implementation sanitizer audit | **Passed:** 24 selected C++20 tests under AddressSanitizer and UndefinedBehaviorSanitizer, with no diagnostics; 513 nonselected cases were deselected in that earlier run. |
| Extracted-copy reproduction | **Passed:** all 655 tests passed in 37.09s, zero failures/skips; catalog/link and generated-document checks also passed without bundled `.git` or `.venv`. The installed local development interpreter supplied third-party test dependencies. |
| Archive integrity and completeness | **Passed:** 358 regular files and 316 explicit directory entries; no duplicate, unsafe, or symlink entries; CRC and byte-for-byte source comparisons passed. |
| Exclusions and credential-pattern inspection | **Passed:** prohibited local/private/generated paths excluded; no recognizable credential or secret patterns detected in exported files. |
| Configuration inspection | **Passed:** five GitHub YAML files and TOML parsed; all four pytest discovery roots present. |

The earlier sanitizer audit occurred before the additional checkpoint-validator cases were added; it is separate from the fresh 655-case full run. Independent implementation audits additionally checked exhaustive Quick Sort inputs and Tim Sort stability, gallop boundaries, and stack inequalities. These audit inputs are not included in the pytest totals.

**Local environment:** Python 3.14.2, pytest 9.1.1, PyYAML 6.0.3, macOS/arm64, Apple Clang 21.0.0 (the local `g++` command). Local success does not establish every compiler/platform combination or prove correctness for all possible inputs.

## Catalog and saved checkpoints

[catalog.yaml](../../../catalog.yaml) retains all **256 original syllabus occurrences**, **35 categories**, and **235 canonical topics**. **11 canonical topics are complete**, all in Sorting. The other **224** topics remain **223 planned plus one blocked**. Merge Sort and Quick Sort are also referenced from Divide and Conquer; these are canonical links, not duplicate implementations or additional-category work.

Sorting documentation is marked `implemented`; Python, C++, and test statuses are `tested`. No automatic human `reviewed` status has been assigned. The catalog development state records all three completed batches, no active batch, and `awaiting-review`.

[docs/progress.md](../../progress.md) is regenerated from the catalog. [docs/sorting-checkpoints.md](../../sorting-checkpoints.md) preserves the batch results and resume boundary:

| Saved gate | Actual full-suite result at that checkpoint |
| --- | --- |
| Batch 1 | 207 passed; catalog and generated documentation checks passed |
| Batch 2 | 359 passed; catalog and generated documentation checks passed |
| Batch 3 / final Sorting handoff | 655 passed; final catalog and generated documentation checks passed |

The earlier gate totals reflect the tests present at those times. The final infrastructure suite includes additional checkpoint-validation tests. **Resume action: wait for the user's review and explicit approval.**

## Testing and CI configuration

The archive includes [requirements-dev.txt](../../../requirements-dev.txt), [pyproject.toml](../../../pyproject.toml), the shared [C++ pytest fixtures](../../../conftest.py), all infrastructure tests, catalog/document generation scripts, and [.github/workflows/ci.yml](../../../.github/workflows/ci.yml).

The workflow is configured for Python **3.11, 3.12, 3.13, and 3.14** on Ubuntu with `g++`. It validates the catalog and documentation, checks generated pages, and runs lightweight pytest with a required C++ compiler; both C++ standards run by default. Repository permissions are read-only and checkout credential persistence is disabled.

**No hosted GitHub Actions result for this handoff is claimed.** No new push was performed to trigger remote CI. The full Python matrix and Linux/GCC environment were not executed locally.

After extraction, from `algorithm-atlas/`, reproduce with Python 3.11+ and a C++17/C++20 compiler:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
```

Windows activation and compiler options are documented in [getting started](../../getting-started.md). Third-party development packages must be installed; the archive does not bundle a virtual environment. Sorting implementations require no third-party runtime libraries or downloaded data.

## Known limitations and unresolved issues

- **No incomplete Sorting requirement or known failing test remains.** All 11 requested algorithms are represented and tested. Review is still pending; this is an educational collection, not a production-readiness claim.
- **Input preservation costs memory.** Public APIs return new containers. Constant-workspace algorithm cores still have O(n) returned-copy storage. Python copies references rather than deeply cloning elements; C++ copies values.
- **Comparison contracts:** generic comparison sorts require consistent `<` ordering and appropriate copy/assignment/swap behavior. They do not expose key/comparator/reverse options. NaNs or inconsistent comparators do not meet their ordering contracts.
- **CLI integer limits:** C++ integer CLIs use `long long`; Radix Sort explicitly requires the full signed 64-bit range. Python integer magnitude affects operation cost, and some CLIs retain the interpreter's default decimal conversion digit limit; each lesson states its behavior.
- **Counting Sort:** native integer-only API, negative-key offsets, default maximum of 1,000,000 count slots, and O(n + k) work/storage for key-span length `k`. Large spans are rejected before allocation; raising the limit does not guarantee available memory.
- **Radix Sort:** Python accepts native integers with bit-length-dependent arithmetic and variable byte passes. C++ performs eight stable byte passes with an order-preserving signed-key mapping. Neither implementation is a generic record sorter.
- **Bucket Sort:** finite values in the closed interval `[0, 1]`; Python accepts native int/float values and C++ uses `double`. Expected linear time requires suitable distribution assumptions; clustered descending values can produce quadratic work. Floating parsing rounds to represented values, explicit large bucket counts can exhaust memory, and C++ uses zero as its automatic-count sentinel while Python rejects explicit zero.
- **Quick Sort:** deterministic middle-position pivot, three-way partitioning, unstable ordering, quadratic worst-case time, logarithmically bounded recursion. It has no randomized or introspective fallback.
- **Shell Sort:** Knuth `3h+1` gaps; unstable, ordered-input Θ(n log n), worst-case O(n^(3/2)), and no universal tight average exponent claimed.
- **Tim Sort:** educational classic length-invariant merge policy, full forward buffers, and a fixed seven-win galloping trigger. It does not implement current CPython Powersort, adaptive galloping thresholds, smaller-run buffer selection, or every production optimization.
- **Stability:** Bubble, Insertion, Merge, Tim, and the documented numeric distribution variants preserve equal-key order. Selection, Quick, Heap, and Shell are explicitly unstable.
- **Outside this scope:** Dynamic Policy Optimization remains blocked pending the maintainer's intended reference. Searching and every other category remain unimplemented and require separate authorization.
- **Verification limits:** static checks cannot prove historical execution claims or guarantee external reference availability. Credential scanning uses filename rules and recognizable patterns; it is not a mathematical proof that arbitrary secret formats cannot exist.

## Files changed and included snapshot

The source/documentation changes below are compared with the Phase 0 Git checkpoint **`e82ff0b` (`Phase-0_Done`)**, through the current working snapshot. They include the already committed Sorting work, progress/validation updates, and this review handoff. Existing and newly created archive artifacts are excluded from the source change list and ZIP. No local changes were committed or pushed during packaging.

The main changes are the 55 algorithm lesson/source/test files, Sorting navigation and canonical cross-links, catalog/progress metadata, saved checkpoints, development approval instructions, and generator/validator regression coverage. Other categories' generated planning/navigation prose reflects the current approval boundary; their algorithms remain unimplemented.

| Included group | Regular files |
| --- | ---: |
| Root project files | 15 |
| .github | 6 |
| docs | 11 |
| scripts | 2 |
| tests | 5 |
| dsa | 154 |
| machine-learning | 116 |
| artificial-intelligence | 49 |
| **Total** | **358** |

The complete snapshot includes **358 regular files**, including this report and the historical Phase 0 documentation. It preserves `.github`, `.gitignore`, `.gitattributes`, and `.editorconfig`. The ZIP itself, Git history, environments, caches, and local generated outputs are excluded. The historical Phase 0 reports/inventory describe their earlier snapshot; the current catalog/progress and this report describe Sorting.

**338 added or modified included paths relative to the Phase 0 checkpoint:**

| Change | File |
| --- | --- |
| Modified | [.github/ISSUE_TEMPLATE/algorithm_proposal.yml](../../../.github/ISSUE_TEMPLATE/algorithm_proposal.yml) |
| Modified | [.github/pull_request_template.md](../../../.github/pull_request_template.md) |
| Modified | [AGENTS.md](../../../AGENTS.md) |
| Modified | [CONTRIBUTING.md](../../../CONTRIBUTING.md) |
| Modified | [README.md](../../../README.md) |
| Modified | [SECURITY.md](../../../SECURITY.md) |
| Added | [docs/reviews/sorting/SORTING-REVIEW-REPORT.md](SORTING-REVIEW-REPORT.md) |
| Modified | [artificial-intelligence/README.md](../../../artificial-intelligence/README.md) |
| Modified | [artificial-intelligence/adversarial-search/README.md](../../../artificial-intelligence/adversarial-search/README.md) |
| Modified | [artificial-intelligence/adversarial-search/alpha-beta-pruning/README.md](../../../artificial-intelligence/adversarial-search/alpha-beta-pruning/README.md) |
| Modified | [artificial-intelligence/adversarial-search/expectimax/README.md](../../../artificial-intelligence/adversarial-search/expectimax/README.md) |
| Modified | [artificial-intelligence/adversarial-search/minimax/README.md](../../../artificial-intelligence/adversarial-search/minimax/README.md) |
| Modified | [artificial-intelligence/computer-vision/README.md](../../../artificial-intelligence/computer-vision/README.md) |
| Modified | [artificial-intelligence/computer-vision/canny-edge-detection/README.md](../../../artificial-intelligence/computer-vision/canny-edge-detection/README.md) |
| Modified | [artificial-intelligence/computer-vision/r-cnn-object-detection/README.md](../../../artificial-intelligence/computer-vision/r-cnn-object-detection/README.md) |
| Modified | [artificial-intelligence/computer-vision/sift/README.md](../../../artificial-intelligence/computer-vision/sift/README.md) |
| Modified | [artificial-intelligence/computer-vision/sobel-edge-detection/README.md](../../../artificial-intelligence/computer-vision/sobel-edge-detection/README.md) |
| Modified | [artificial-intelligence/computer-vision/surf/README.md](../../../artificial-intelligence/computer-vision/surf/README.md) |
| Modified | [artificial-intelligence/computer-vision/viola-jones-face-detection/README.md](../../../artificial-intelligence/computer-vision/viola-jones-face-detection/README.md) |
| Modified | [artificial-intelligence/computer-vision/yolo-object-detection/README.md](../../../artificial-intelligence/computer-vision/yolo-object-detection/README.md) |
| Modified | [artificial-intelligence/constraint-satisfaction/README.md](../../../artificial-intelligence/constraint-satisfaction/README.md) |
| Modified | [artificial-intelligence/constraint-satisfaction/arc-consistency-ac-3/README.md](../../../artificial-intelligence/constraint-satisfaction/arc-consistency-ac-3/README.md) |
| Modified | [artificial-intelligence/constraint-satisfaction/backtracking-search/README.md](../../../artificial-intelligence/constraint-satisfaction/backtracking-search/README.md) |
| Modified | [artificial-intelligence/constraint-satisfaction/constraint-propagation/README.md](../../../artificial-intelligence/constraint-satisfaction/constraint-propagation/README.md) |
| Modified | [artificial-intelligence/constraint-satisfaction/forward-checking/README.md](../../../artificial-intelligence/constraint-satisfaction/forward-checking/README.md) |
| Modified | [artificial-intelligence/constraint-satisfaction/min-conflicts/README.md](../../../artificial-intelligence/constraint-satisfaction/min-conflicts/README.md) |
| Modified | [artificial-intelligence/fuzzy-logic/README.md](../../../artificial-intelligence/fuzzy-logic/README.md) |
| Modified | [artificial-intelligence/fuzzy-logic/mamdani-fuzzy-inference/README.md](../../../artificial-intelligence/fuzzy-logic/mamdani-fuzzy-inference/README.md) |
| Modified | [artificial-intelligence/fuzzy-logic/sugeno-fuzzy-inference/README.md](../../../artificial-intelligence/fuzzy-logic/sugeno-fuzzy-inference/README.md) |
| Modified | [artificial-intelligence/global-optimization/README.md](../../../artificial-intelligence/global-optimization/README.md) |
| Modified | [artificial-intelligence/global-optimization/ant-colony-optimization/README.md](../../../artificial-intelligence/global-optimization/ant-colony-optimization/README.md) |
| Modified | [artificial-intelligence/global-optimization/branch-and-bound/README.md](../../../artificial-intelligence/global-optimization/branch-and-bound/README.md) |
| Modified | [artificial-intelligence/global-optimization/exhaustive-search/README.md](../../../artificial-intelligence/global-optimization/exhaustive-search/README.md) |
| Modified | [artificial-intelligence/global-optimization/particle-swarm-optimization/README.md](../../../artificial-intelligence/global-optimization/particle-swarm-optimization/README.md) |
| Modified | [artificial-intelligence/informed-search/README.md](../../../artificial-intelligence/informed-search/README.md) |
| Modified | [artificial-intelligence/informed-search/beam-search/README.md](../../../artificial-intelligence/informed-search/beam-search/README.md) |
| Modified | [artificial-intelligence/informed-search/greedy-best-first-search/README.md](../../../artificial-intelligence/informed-search/greedy-best-first-search/README.md) |
| Modified | [artificial-intelligence/informed-search/iterative-deepening-a-star/README.md](../../../artificial-intelligence/informed-search/iterative-deepening-a-star/README.md) |
| Modified | [artificial-intelligence/informed-search/recursive-best-first-search/README.md](../../../artificial-intelligence/informed-search/recursive-best-first-search/README.md) |
| Modified | [artificial-intelligence/informed-search/simplified-memory-bounded-a-star/README.md](../../../artificial-intelligence/informed-search/simplified-memory-bounded-a-star/README.md) |
| Modified | [artificial-intelligence/local-search/README.md](../../../artificial-intelligence/local-search/README.md) |
| Modified | [artificial-intelligence/local-search/local-beam-search/README.md](../../../artificial-intelligence/local-search/local-beam-search/README.md) |
| Modified | [artificial-intelligence/local-search/random-restart-hill-climbing/README.md](../../../artificial-intelligence/local-search/random-restart-hill-climbing/README.md) |
| Modified | [artificial-intelligence/local-search/simple-hill-climbing/README.md](../../../artificial-intelligence/local-search/simple-hill-climbing/README.md) |
| Modified | [artificial-intelligence/local-search/steepest-ascent-hill-climbing/README.md](../../../artificial-intelligence/local-search/steepest-ascent-hill-climbing/README.md) |
| Modified | [artificial-intelligence/local-search/stochastic-hill-climbing/README.md](../../../artificial-intelligence/local-search/stochastic-hill-climbing/README.md) |
| Modified | [artificial-intelligence/local-search/tabu-search/README.md](../../../artificial-intelligence/local-search/tabu-search/README.md) |
| Modified | [artificial-intelligence/multi-agent-systems/README.md](../../../artificial-intelligence/multi-agent-systems/README.md) |
| Modified | [artificial-intelligence/multi-agent-systems/auction-algorithms/README.md](../../../artificial-intelligence/multi-agent-systems/auction-algorithms/README.md) |
| Modified | [artificial-intelligence/multi-agent-systems/nash-equilibrium-computation/README.md](../../../artificial-intelligence/multi-agent-systems/nash-equilibrium-computation/README.md) |
| Modified | [artificial-intelligence/swarm-intelligence/README.md](../../../artificial-intelligence/swarm-intelligence/README.md) |
| Modified | [artificial-intelligence/uninformed-search/README.md](../../../artificial-intelligence/uninformed-search/README.md) |
| Modified | [artificial-intelligence/uninformed-search/bidirectional-search/README.md](../../../artificial-intelligence/uninformed-search/bidirectional-search/README.md) |
| Modified | [artificial-intelligence/uninformed-search/depth-limited-search/README.md](../../../artificial-intelligence/uninformed-search/depth-limited-search/README.md) |
| Modified | [artificial-intelligence/uninformed-search/iterative-deepening-dfs/README.md](../../../artificial-intelligence/uninformed-search/iterative-deepening-dfs/README.md) |
| Modified | [artificial-intelligence/uninformed-search/uniform-cost-search/README.md](../../../artificial-intelligence/uninformed-search/uniform-cost-search/README.md) |
| Modified | [catalog.yaml](../../../catalog.yaml) |
| Modified | [docs/algorithm-index.md](../../algorithm-index.md) |
| Modified | [docs/development.md](../../development.md) |
| Modified | [docs/getting-started.md](../../getting-started.md) |
| Modified | [docs/glossary.md](../../glossary.md) |
| Modified | [docs/learning-roadmap.md](../../learning-roadmap.md) |
| Modified | [docs/progress.md](../../progress.md) |
| Added | [docs/sorting-checkpoints.md](../../sorting-checkpoints.md) |
| Modified | [dsa/README.md](../../../dsa/README.md) |
| Modified | [dsa/bit-manipulation/README.md](../../../dsa/bit-manipulation/README.md) |
| Modified | [dsa/bit-manipulation/brian-kernighan-set-bit-counting/README.md](../../../dsa/bit-manipulation/brian-kernighan-set-bit-counting/README.md) |
| Modified | [dsa/bit-manipulation/subset-generation-bitmasking/README.md](../../../dsa/bit-manipulation/subset-generation-bitmasking/README.md) |
| Modified | [dsa/bit-manipulation/two-non-repeating-elements/README.md](../../../dsa/bit-manipulation/two-non-repeating-elements/README.md) |
| Modified | [dsa/bit-manipulation/xor-unique-elements/README.md](../../../dsa/bit-manipulation/xor-unique-elements/README.md) |
| Modified | [dsa/divide-and-conquer/README.md](../../../dsa/divide-and-conquer/README.md) |
| Modified | [dsa/divide-and-conquer/closest-pair-of-points/README.md](../../../dsa/divide-and-conquer/closest-pair-of-points/README.md) |
| Modified | [dsa/divide-and-conquer/karatsuba-multiplication/README.md](../../../dsa/divide-and-conquer/karatsuba-multiplication/README.md) |
| Modified | [dsa/divide-and-conquer/maximum-subarray-divide-and-conquer/README.md](../../../dsa/divide-and-conquer/maximum-subarray-divide-and-conquer/README.md) |
| Modified | [dsa/divide-and-conquer/strassen-matrix-multiplication/README.md](../../../dsa/divide-and-conquer/strassen-matrix-multiplication/README.md) |
| Modified | [dsa/dynamic-programming/README.md](../../../dsa/dynamic-programming/README.md) |
| Modified | [dsa/dynamic-programming/coin-change/README.md](../../../dsa/dynamic-programming/coin-change/README.md) |
| Modified | [dsa/dynamic-programming/edit-distance/README.md](../../../dsa/dynamic-programming/edit-distance/README.md) |
| Modified | [dsa/dynamic-programming/fibonacci/README.md](../../../dsa/dynamic-programming/fibonacci/README.md) |
| Modified | [dsa/dynamic-programming/kadane/README.md](../../../dsa/dynamic-programming/kadane/README.md) |
| Modified | [dsa/dynamic-programming/longest-common-subsequence/README.md](../../../dsa/dynamic-programming/longest-common-subsequence/README.md) |
| Modified | [dsa/dynamic-programming/longest-increasing-subsequence/README.md](../../../dsa/dynamic-programming/longest-increasing-subsequence/README.md) |
| Modified | [dsa/dynamic-programming/matrix-chain-multiplication/README.md](../../../dsa/dynamic-programming/matrix-chain-multiplication/README.md) |
| Modified | [dsa/dynamic-programming/palindrome-partitioning/README.md](../../../dsa/dynamic-programming/palindrome-partitioning/README.md) |
| Modified | [dsa/dynamic-programming/rod-cutting/README.md](../../../dsa/dynamic-programming/rod-cutting/README.md) |
| Modified | [dsa/dynamic-programming/subset-sum/README.md](../../../dsa/dynamic-programming/subset-sum/README.md) |
| Modified | [dsa/dynamic-programming/zero-one-knapsack/README.md](../../../dsa/dynamic-programming/zero-one-knapsack/README.md) |
| Modified | [dsa/graph-algorithms/README.md](../../../dsa/graph-algorithms/README.md) |
| Modified | [dsa/graph-algorithms/a-star-search/README.md](../../../dsa/graph-algorithms/a-star-search/README.md) |
| Modified | [dsa/graph-algorithms/articulation-points/README.md](../../../dsa/graph-algorithms/articulation-points/README.md) |
| Modified | [dsa/graph-algorithms/bellman-ford/README.md](../../../dsa/graph-algorithms/bellman-ford/README.md) |
| Modified | [dsa/graph-algorithms/breadth-first-search/README.md](../../../dsa/graph-algorithms/breadth-first-search/README.md) |
| Modified | [dsa/graph-algorithms/bridges-detection/README.md](../../../dsa/graph-algorithms/bridges-detection/README.md) |
| Modified | [dsa/graph-algorithms/depth-first-search/README.md](../../../dsa/graph-algorithms/depth-first-search/README.md) |
| Modified | [dsa/graph-algorithms/dijkstra/README.md](../../../dsa/graph-algorithms/dijkstra/README.md) |
| Modified | [dsa/graph-algorithms/floyd-warshall/README.md](../../../dsa/graph-algorithms/floyd-warshall/README.md) |
| Modified | [dsa/graph-algorithms/johnson/README.md](../../../dsa/graph-algorithms/johnson/README.md) |
| Modified | [dsa/graph-algorithms/kosaraju-strongly-connected-components/README.md](../../../dsa/graph-algorithms/kosaraju-strongly-connected-components/README.md) |
| Modified | [dsa/graph-algorithms/kruskal/README.md](../../../dsa/graph-algorithms/kruskal/README.md) |
| Modified | [dsa/graph-algorithms/prim/README.md](../../../dsa/graph-algorithms/prim/README.md) |
| Modified | [dsa/graph-algorithms/tarjan-strongly-connected-components/README.md](../../../dsa/graph-algorithms/tarjan-strongly-connected-components/README.md) |
| Modified | [dsa/graph-algorithms/topological-sorting/README.md](../../../dsa/graph-algorithms/topological-sorting/README.md) |
| Modified | [dsa/graph-algorithms/union-find/README.md](../../../dsa/graph-algorithms/union-find/README.md) |
| Modified | [dsa/greedy/README.md](../../../dsa/greedy/README.md) |
| Modified | [dsa/greedy/activity-selection/README.md](../../../dsa/greedy/activity-selection/README.md) |
| Modified | [dsa/greedy/fractional-knapsack/README.md](../../../dsa/greedy/fractional-knapsack/README.md) |
| Modified | [dsa/greedy/huffman-coding/README.md](../../../dsa/greedy/huffman-coding/README.md) |
| Modified | [dsa/greedy/job-sequencing-with-deadlines/README.md](../../../dsa/greedy/job-sequencing-with-deadlines/README.md) |
| Modified | [dsa/number-theory/README.md](../../../dsa/number-theory/README.md) |
| Modified | [dsa/number-theory/euclidean-algorithm/README.md](../../../dsa/number-theory/euclidean-algorithm/README.md) |
| Modified | [dsa/number-theory/extended-euclidean-algorithm/README.md](../../../dsa/number-theory/extended-euclidean-algorithm/README.md) |
| Modified | [dsa/number-theory/fast-exponentiation/README.md](../../../dsa/number-theory/fast-exponentiation/README.md) |
| Modified | [dsa/number-theory/least-common-multiple/README.md](../../../dsa/number-theory/least-common-multiple/README.md) |
| Modified | [dsa/number-theory/modular-exponentiation/README.md](../../../dsa/number-theory/modular-exponentiation/README.md) |
| Modified | [dsa/number-theory/prime-factorization/README.md](../../../dsa/number-theory/prime-factorization/README.md) |
| Modified | [dsa/number-theory/sieve-of-eratosthenes/README.md](../../../dsa/number-theory/sieve-of-eratosthenes/README.md) |
| Modified | [dsa/recursion-and-backtracking/README.md](../../../dsa/recursion-and-backtracking/README.md) |
| Modified | [dsa/recursion-and-backtracking/combinations/README.md](../../../dsa/recursion-and-backtracking/combinations/README.md) |
| Modified | [dsa/recursion-and-backtracking/graph-coloring/README.md](../../../dsa/recursion-and-backtracking/graph-coloring/README.md) |
| Modified | [dsa/recursion-and-backtracking/hamiltonian-path/README.md](../../../dsa/recursion-and-backtracking/hamiltonian-path/README.md) |
| Modified | [dsa/recursion-and-backtracking/n-queens/README.md](../../../dsa/recursion-and-backtracking/n-queens/README.md) |
| Modified | [dsa/recursion-and-backtracking/permutations/README.md](../../../dsa/recursion-and-backtracking/permutations/README.md) |
| Modified | [dsa/recursion-and-backtracking/power-set-generation/README.md](../../../dsa/recursion-and-backtracking/power-set-generation/README.md) |
| Modified | [dsa/recursion-and-backtracking/rat-in-a-maze/README.md](../../../dsa/recursion-and-backtracking/rat-in-a-maze/README.md) |
| Modified | [dsa/recursion-and-backtracking/subset-sum-backtracking/README.md](../../../dsa/recursion-and-backtracking/subset-sum-backtracking/README.md) |
| Modified | [dsa/recursion-and-backtracking/sudoku-solver/README.md](../../../dsa/recursion-and-backtracking/sudoku-solver/README.md) |
| Modified | [dsa/searching/README.md](../../../dsa/searching/README.md) |
| Modified | [dsa/searching/binary-search/README.md](../../../dsa/searching/binary-search/README.md) |
| Modified | [dsa/searching/exponential-search/README.md](../../../dsa/searching/exponential-search/README.md) |
| Modified | [dsa/searching/interpolation-search/README.md](../../../dsa/searching/interpolation-search/README.md) |
| Modified | [dsa/searching/jump-search/README.md](../../../dsa/searching/jump-search/README.md) |
| Modified | [dsa/searching/linear-search/README.md](../../../dsa/searching/linear-search/README.md) |
| Modified | [dsa/searching/ternary-search/README.md](../../../dsa/searching/ternary-search/README.md) |
| Modified | [dsa/sorting/README.md](../../../dsa/sorting/README.md) |
| Modified | [dsa/sorting/bubble-sort/README.md](../../../dsa/sorting/bubble-sort/README.md) |
| Added | [dsa/sorting/bubble-sort/cpp/solution.cpp](../../../dsa/sorting/bubble-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/bubble-sort/python/solution.py](../../../dsa/sorting/bubble-sort/python/solution.py) |
| Added | [dsa/sorting/bubble-sort/tests/test_cpp.py](../../../dsa/sorting/bubble-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/bubble-sort/tests/test_python.py](../../../dsa/sorting/bubble-sort/tests/test_python.py) |
| Modified | [dsa/sorting/bucket-sort/README.md](../../../dsa/sorting/bucket-sort/README.md) |
| Added | [dsa/sorting/bucket-sort/cpp/solution.cpp](../../../dsa/sorting/bucket-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/bucket-sort/python/solution.py](../../../dsa/sorting/bucket-sort/python/solution.py) |
| Added | [dsa/sorting/bucket-sort/tests/test_cpp.py](../../../dsa/sorting/bucket-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/bucket-sort/tests/test_python.py](../../../dsa/sorting/bucket-sort/tests/test_python.py) |
| Modified | [dsa/sorting/counting-sort/README.md](../../../dsa/sorting/counting-sort/README.md) |
| Added | [dsa/sorting/counting-sort/cpp/solution.cpp](../../../dsa/sorting/counting-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/counting-sort/python/solution.py](../../../dsa/sorting/counting-sort/python/solution.py) |
| Added | [dsa/sorting/counting-sort/tests/test_cpp.py](../../../dsa/sorting/counting-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/counting-sort/tests/test_python.py](../../../dsa/sorting/counting-sort/tests/test_python.py) |
| Modified | [dsa/sorting/heap-sort/README.md](../../../dsa/sorting/heap-sort/README.md) |
| Added | [dsa/sorting/heap-sort/cpp/solution.cpp](../../../dsa/sorting/heap-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/heap-sort/python/solution.py](../../../dsa/sorting/heap-sort/python/solution.py) |
| Added | [dsa/sorting/heap-sort/tests/test_cpp.py](../../../dsa/sorting/heap-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/heap-sort/tests/test_python.py](../../../dsa/sorting/heap-sort/tests/test_python.py) |
| Modified | [dsa/sorting/insertion-sort/README.md](../../../dsa/sorting/insertion-sort/README.md) |
| Added | [dsa/sorting/insertion-sort/cpp/solution.cpp](../../../dsa/sorting/insertion-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/insertion-sort/python/solution.py](../../../dsa/sorting/insertion-sort/python/solution.py) |
| Added | [dsa/sorting/insertion-sort/tests/test_cpp.py](../../../dsa/sorting/insertion-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/insertion-sort/tests/test_python.py](../../../dsa/sorting/insertion-sort/tests/test_python.py) |
| Modified | [dsa/sorting/merge-sort/README.md](../../../dsa/sorting/merge-sort/README.md) |
| Added | [dsa/sorting/merge-sort/cpp/solution.cpp](../../../dsa/sorting/merge-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/merge-sort/python/solution.py](../../../dsa/sorting/merge-sort/python/solution.py) |
| Added | [dsa/sorting/merge-sort/tests/test_cpp.py](../../../dsa/sorting/merge-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/merge-sort/tests/test_python.py](../../../dsa/sorting/merge-sort/tests/test_python.py) |
| Modified | [dsa/sorting/quick-sort/README.md](../../../dsa/sorting/quick-sort/README.md) |
| Added | [dsa/sorting/quick-sort/cpp/solution.cpp](../../../dsa/sorting/quick-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/quick-sort/python/solution.py](../../../dsa/sorting/quick-sort/python/solution.py) |
| Added | [dsa/sorting/quick-sort/tests/test_cpp.py](../../../dsa/sorting/quick-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/quick-sort/tests/test_python.py](../../../dsa/sorting/quick-sort/tests/test_python.py) |
| Modified | [dsa/sorting/radix-sort/README.md](../../../dsa/sorting/radix-sort/README.md) |
| Added | [dsa/sorting/radix-sort/cpp/solution.cpp](../../../dsa/sorting/radix-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/radix-sort/python/solution.py](../../../dsa/sorting/radix-sort/python/solution.py) |
| Added | [dsa/sorting/radix-sort/tests/test_cpp.py](../../../dsa/sorting/radix-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/radix-sort/tests/test_python.py](../../../dsa/sorting/radix-sort/tests/test_python.py) |
| Modified | [dsa/sorting/selection-sort/README.md](../../../dsa/sorting/selection-sort/README.md) |
| Added | [dsa/sorting/selection-sort/cpp/solution.cpp](../../../dsa/sorting/selection-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/selection-sort/python/solution.py](../../../dsa/sorting/selection-sort/python/solution.py) |
| Added | [dsa/sorting/selection-sort/tests/test_cpp.py](../../../dsa/sorting/selection-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/selection-sort/tests/test_python.py](../../../dsa/sorting/selection-sort/tests/test_python.py) |
| Modified | [dsa/sorting/shell-sort/README.md](../../../dsa/sorting/shell-sort/README.md) |
| Added | [dsa/sorting/shell-sort/cpp/solution.cpp](../../../dsa/sorting/shell-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/shell-sort/python/solution.py](../../../dsa/sorting/shell-sort/python/solution.py) |
| Added | [dsa/sorting/shell-sort/tests/test_cpp.py](../../../dsa/sorting/shell-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/shell-sort/tests/test_python.py](../../../dsa/sorting/shell-sort/tests/test_python.py) |
| Modified | [dsa/sorting/tim-sort/README.md](../../../dsa/sorting/tim-sort/README.md) |
| Added | [dsa/sorting/tim-sort/cpp/solution.cpp](../../../dsa/sorting/tim-sort/cpp/solution.cpp) |
| Added | [dsa/sorting/tim-sort/python/solution.py](../../../dsa/sorting/tim-sort/python/solution.py) |
| Added | [dsa/sorting/tim-sort/tests/test_cpp.py](../../../dsa/sorting/tim-sort/tests/test_cpp.py) |
| Added | [dsa/sorting/tim-sort/tests/test_python.py](../../../dsa/sorting/tim-sort/tests/test_python.py) |
| Modified | [dsa/string-algorithms/README.md](../../../dsa/string-algorithms/README.md) |
| Modified | [dsa/string-algorithms/aho-corasick/README.md](../../../dsa/string-algorithms/aho-corasick/README.md) |
| Modified | [dsa/string-algorithms/boyer-moore/README.md](../../../dsa/string-algorithms/boyer-moore/README.md) |
| Modified | [dsa/string-algorithms/knuth-morris-pratt/README.md](../../../dsa/string-algorithms/knuth-morris-pratt/README.md) |
| Modified | [dsa/string-algorithms/manacher/README.md](../../../dsa/string-algorithms/manacher/README.md) |
| Modified | [dsa/string-algorithms/naive-pattern-matching/README.md](../../../dsa/string-algorithms/naive-pattern-matching/README.md) |
| Modified | [dsa/string-algorithms/rabin-karp/README.md](../../../dsa/string-algorithms/rabin-karp/README.md) |
| Modified | [dsa/string-algorithms/suffix-array/README.md](../../../dsa/string-algorithms/suffix-array/README.md) |
| Modified | [dsa/string-algorithms/suffix-tree/README.md](../../../dsa/string-algorithms/suffix-tree/README.md) |
| Modified | [dsa/string-algorithms/z-algorithm/README.md](../../../dsa/string-algorithms/z-algorithm/README.md) |
| Modified | [dsa/tree-algorithms/README.md](../../../dsa/tree-algorithms/README.md) |
| Modified | [dsa/tree-algorithms/avl-tree-rotations/README.md](../../../dsa/tree-algorithms/avl-tree-rotations/README.md) |
| Modified | [dsa/tree-algorithms/b-plus-tree-operations/README.md](../../../dsa/tree-algorithms/b-plus-tree-operations/README.md) |
| Modified | [dsa/tree-algorithms/b-tree-operations/README.md](../../../dsa/tree-algorithms/b-tree-operations/README.md) |
| Modified | [dsa/tree-algorithms/binary-lifting/README.md](../../../dsa/tree-algorithms/binary-lifting/README.md) |
| Modified | [dsa/tree-algorithms/euler-tour/README.md](../../../dsa/tree-algorithms/euler-tour/README.md) |
| Modified | [dsa/tree-algorithms/fenwick-tree/README.md](../../../dsa/tree-algorithms/fenwick-tree/README.md) |
| Modified | [dsa/tree-algorithms/inorder-traversal/README.md](../../../dsa/tree-algorithms/inorder-traversal/README.md) |
| Modified | [dsa/tree-algorithms/level-order-traversal/README.md](../../../dsa/tree-algorithms/level-order-traversal/README.md) |
| Modified | [dsa/tree-algorithms/lowest-common-ancestor/README.md](../../../dsa/tree-algorithms/lowest-common-ancestor/README.md) |
| Modified | [dsa/tree-algorithms/postorder-traversal/README.md](../../../dsa/tree-algorithms/postorder-traversal/README.md) |
| Modified | [dsa/tree-algorithms/preorder-traversal/README.md](../../../dsa/tree-algorithms/preorder-traversal/README.md) |
| Modified | [dsa/tree-algorithms/red-black-tree-operations/README.md](../../../dsa/tree-algorithms/red-black-tree-operations/README.md) |
| Modified | [dsa/tree-algorithms/segment-tree/README.md](../../../dsa/tree-algorithms/segment-tree/README.md) |
| Modified | [dsa/tree-algorithms/trie/README.md](../../../dsa/tree-algorithms/trie/README.md) |
| Modified | [dsa/two-pointers-and-sliding-window/README.md](../../../dsa/two-pointers-and-sliding-window/README.md) |
| Modified | [dsa/two-pointers-and-sliding-window/longest-substring-without-repeating-characters/README.md](../../../dsa/two-pointers-and-sliding-window/longest-substring-without-repeating-characters/README.md) |
| Modified | [dsa/two-pointers-and-sliding-window/sliding-window-maximum/README.md](../../../dsa/two-pointers-and-sliding-window/sliding-window-maximum/README.md) |
| Modified | [dsa/two-pointers-and-sliding-window/two-sum-sorted-array/README.md](../../../dsa/two-pointers-and-sliding-window/two-sum-sorted-array/README.md) |
| Modified | [machine-learning/README.md](../../../machine-learning/README.md) |
| Modified | [machine-learning/anomaly-detection/README.md](../../../machine-learning/anomaly-detection/README.md) |
| Modified | [machine-learning/anomaly-detection/isolation-forest/README.md](../../../machine-learning/anomaly-detection/isolation-forest/README.md) |
| Modified | [machine-learning/anomaly-detection/local-outlier-factor/README.md](../../../machine-learning/anomaly-detection/local-outlier-factor/README.md) |
| Modified | [machine-learning/anomaly-detection/one-class-svm/README.md](../../../machine-learning/anomaly-detection/one-class-svm/README.md) |
| Modified | [machine-learning/deep-learning/README.md](../../../machine-learning/deep-learning/README.md) |
| Modified | [machine-learning/deep-learning/convolutional-neural-networks/README.md](../../../machine-learning/deep-learning/convolutional-neural-networks/README.md) |
| Modified | [machine-learning/deep-learning/denoising-autoencoders/README.md](../../../machine-learning/deep-learning/denoising-autoencoders/README.md) |
| Modified | [machine-learning/deep-learning/diffusion-models/README.md](../../../machine-learning/deep-learning/diffusion-models/README.md) |
| Modified | [machine-learning/deep-learning/gated-recurrent-units/README.md](../../../machine-learning/deep-learning/gated-recurrent-units/README.md) |
| Modified | [machine-learning/deep-learning/generative-adversarial-networks/README.md](../../../machine-learning/deep-learning/generative-adversarial-networks/README.md) |
| Modified | [machine-learning/deep-learning/graph-neural-networks/README.md](../../../machine-learning/deep-learning/graph-neural-networks/README.md) |
| Modified | [machine-learning/deep-learning/long-short-term-memory/README.md](../../../machine-learning/deep-learning/long-short-term-memory/README.md) |
| Modified | [machine-learning/deep-learning/multilayer-perceptron/README.md](../../../machine-learning/deep-learning/multilayer-perceptron/README.md) |
| Modified | [machine-learning/deep-learning/recurrent-neural-networks/README.md](../../../machine-learning/deep-learning/recurrent-neural-networks/README.md) |
| Modified | [machine-learning/deep-learning/residual-networks/README.md](../../../machine-learning/deep-learning/residual-networks/README.md) |
| Modified | [machine-learning/deep-learning/sparse-autoencoders/README.md](../../../machine-learning/deep-learning/sparse-autoencoders/README.md) |
| Modified | [machine-learning/deep-learning/transformers/README.md](../../../machine-learning/deep-learning/transformers/README.md) |
| Modified | [machine-learning/deep-learning/vanilla-autoencoders/README.md](../../../machine-learning/deep-learning/vanilla-autoencoders/README.md) |
| Modified | [machine-learning/deep-learning/variational-autoencoders/README.md](../../../machine-learning/deep-learning/variational-autoencoders/README.md) |
| Modified | [machine-learning/ensemble-methods/README.md](../../../machine-learning/ensemble-methods/README.md) |
| Modified | [machine-learning/ensemble-methods/adaboost/README.md](../../../machine-learning/ensemble-methods/adaboost/README.md) |
| Modified | [machine-learning/ensemble-methods/bagging/README.md](../../../machine-learning/ensemble-methods/bagging/README.md) |
| Modified | [machine-learning/ensemble-methods/catboost/README.md](../../../machine-learning/ensemble-methods/catboost/README.md) |
| Modified | [machine-learning/ensemble-methods/gradient-boosting-machine/README.md](../../../machine-learning/ensemble-methods/gradient-boosting-machine/README.md) |
| Modified | [machine-learning/ensemble-methods/random-forest/README.md](../../../machine-learning/ensemble-methods/random-forest/README.md) |
| Modified | [machine-learning/ensemble-methods/stacking/README.md](../../../machine-learning/ensemble-methods/stacking/README.md) |
| Modified | [machine-learning/ensemble-methods/voting-classifiers/README.md](../../../machine-learning/ensemble-methods/voting-classifiers/README.md) |
| Modified | [machine-learning/ensemble-methods/xgboost/README.md](../../../machine-learning/ensemble-methods/xgboost/README.md) |
| Modified | [machine-learning/graph-learning/README.md](../../../machine-learning/graph-learning/README.md) |
| Modified | [machine-learning/graph-learning/graph-convolutional-networks/README.md](../../../machine-learning/graph-learning/graph-convolutional-networks/README.md) |
| Modified | [machine-learning/graph-learning/node2vec/README.md](../../../machine-learning/graph-learning/node2vec/README.md) |
| Modified | [machine-learning/graph-learning/pagerank/README.md](../../../machine-learning/graph-learning/pagerank/README.md) |
| Modified | [machine-learning/natural-language-processing/README.md](../../../machine-learning/natural-language-processing/README.md) |
| Modified | [machine-learning/natural-language-processing/bag-of-words/README.md](../../../machine-learning/natural-language-processing/bag-of-words/README.md) |
| Modified | [machine-learning/natural-language-processing/bert/README.md](../../../machine-learning/natural-language-processing/bert/README.md) |
| Modified | [machine-learning/natural-language-processing/conditional-random-fields/README.md](../../../machine-learning/natural-language-processing/conditional-random-fields/README.md) |
| Modified | [machine-learning/natural-language-processing/cyk-parsing/README.md](../../../machine-learning/natural-language-processing/cyk-parsing/README.md) |
| Modified | [machine-learning/natural-language-processing/glove/README.md](../../../machine-learning/natural-language-processing/glove/README.md) |
| Modified | [machine-learning/natural-language-processing/gpt/README.md](../../../machine-learning/natural-language-processing/gpt/README.md) |
| Modified | [machine-learning/natural-language-processing/hidden-markov-models-pos-tagging/README.md](../../../machine-learning/natural-language-processing/hidden-markov-models-pos-tagging/README.md) |
| Modified | [machine-learning/natural-language-processing/n-gram-language-models/README.md](../../../machine-learning/natural-language-processing/n-gram-language-models/README.md) |
| Modified | [machine-learning/natural-language-processing/named-entity-recognition/README.md](../../../machine-learning/natural-language-processing/named-entity-recognition/README.md) |
| Modified | [machine-learning/natural-language-processing/tf-idf/README.md](../../../machine-learning/natural-language-processing/tf-idf/README.md) |
| Modified | [machine-learning/natural-language-processing/word2vec/README.md](../../../machine-learning/natural-language-processing/word2vec/README.md) |
| Modified | [machine-learning/optimization/README.md](../../../machine-learning/optimization/README.md) |
| Modified | [machine-learning/optimization/adam/README.md](../../../machine-learning/optimization/adam/README.md) |
| Modified | [machine-learning/optimization/adamw/README.md](../../../machine-learning/optimization/adamw/README.md) |
| Modified | [machine-learning/optimization/batch-gradient-descent/README.md](../../../machine-learning/optimization/batch-gradient-descent/README.md) |
| Modified | [machine-learning/optimization/genetic-algorithms/README.md](../../../machine-learning/optimization/genetic-algorithms/README.md) |
| Modified | [machine-learning/optimization/l-bfgs/README.md](../../../machine-learning/optimization/l-bfgs/README.md) |
| Modified | [machine-learning/optimization/mini-batch-gradient-descent/README.md](../../../machine-learning/optimization/mini-batch-gradient-descent/README.md) |
| Modified | [machine-learning/optimization/momentum/README.md](../../../machine-learning/optimization/momentum/README.md) |
| Modified | [machine-learning/optimization/rmsprop/README.md](../../../machine-learning/optimization/rmsprop/README.md) |
| Modified | [machine-learning/optimization/simulated-annealing/README.md](../../../machine-learning/optimization/simulated-annealing/README.md) |
| Modified | [machine-learning/optimization/stochastic-gradient-descent/README.md](../../../machine-learning/optimization/stochastic-gradient-descent/README.md) |
| Modified | [machine-learning/reinforcement-learning/README.md](../../../machine-learning/reinforcement-learning/README.md) |
| Modified | [machine-learning/reinforcement-learning/advantage-actor-critic/README.md](../../../machine-learning/reinforcement-learning/advantage-actor-critic/README.md) |
| Modified | [machine-learning/reinforcement-learning/asynchronous-advantage-actor-critic/README.md](../../../machine-learning/reinforcement-learning/asynchronous-advantage-actor-critic/README.md) |
| Modified | [machine-learning/reinforcement-learning/deep-deterministic-policy-gradient/README.md](../../../machine-learning/reinforcement-learning/deep-deterministic-policy-gradient/README.md) |
| Modified | [machine-learning/reinforcement-learning/deep-q-networks/README.md](../../../machine-learning/reinforcement-learning/deep-q-networks/README.md) |
| Modified | [machine-learning/reinforcement-learning/dynamic-policy-optimization/README.md](../../../machine-learning/reinforcement-learning/dynamic-policy-optimization/README.md) |
| Modified | [machine-learning/reinforcement-learning/monte-carlo-tree-search/README.md](../../../machine-learning/reinforcement-learning/monte-carlo-tree-search/README.md) |
| Modified | [machine-learning/reinforcement-learning/proximal-policy-optimization/README.md](../../../machine-learning/reinforcement-learning/proximal-policy-optimization/README.md) |
| Modified | [machine-learning/reinforcement-learning/q-learning/README.md](../../../machine-learning/reinforcement-learning/q-learning/README.md) |
| Modified | [machine-learning/reinforcement-learning/reinforce-policy-gradient/README.md](../../../machine-learning/reinforcement-learning/reinforce-policy-gradient/README.md) |
| Modified | [machine-learning/reinforcement-learning/sarsa/README.md](../../../machine-learning/reinforcement-learning/sarsa/README.md) |
| Modified | [machine-learning/supervised-learning/README.md](../../../machine-learning/supervised-learning/README.md) |
| Modified | [machine-learning/supervised-learning/classification/README.md](../../../machine-learning/supervised-learning/classification/README.md) |
| Modified | [machine-learning/supervised-learning/classification/bernoulli-naive-bayes/README.md](../../../machine-learning/supervised-learning/classification/bernoulli-naive-bayes/README.md) |
| Modified | [machine-learning/supervised-learning/classification/c4-5-decision-trees/README.md](../../../machine-learning/supervised-learning/classification/c4-5-decision-trees/README.md) |
| Modified | [machine-learning/supervised-learning/classification/cart-decision-trees/README.md](../../../machine-learning/supervised-learning/classification/cart-decision-trees/README.md) |
| Modified | [machine-learning/supervised-learning/classification/gaussian-naive-bayes/README.md](../../../machine-learning/supervised-learning/classification/gaussian-naive-bayes/README.md) |
| Modified | [machine-learning/supervised-learning/classification/id3-decision-trees/README.md](../../../machine-learning/supervised-learning/classification/id3-decision-trees/README.md) |
| Modified | [machine-learning/supervised-learning/classification/k-nearest-neighbors/README.md](../../../machine-learning/supervised-learning/classification/k-nearest-neighbors/README.md) |
| Modified | [machine-learning/supervised-learning/classification/linear-discriminant-analysis/README.md](../../../machine-learning/supervised-learning/classification/linear-discriminant-analysis/README.md) |
| Modified | [machine-learning/supervised-learning/classification/logistic-regression/README.md](../../../machine-learning/supervised-learning/classification/logistic-regression/README.md) |
| Modified | [machine-learning/supervised-learning/classification/multinomial-naive-bayes/README.md](../../../machine-learning/supervised-learning/classification/multinomial-naive-bayes/README.md) |
| Modified | [machine-learning/supervised-learning/classification/quadratic-discriminant-analysis/README.md](../../../machine-learning/supervised-learning/classification/quadratic-discriminant-analysis/README.md) |
| Modified | [machine-learning/supervised-learning/classification/support-vector-machines/README.md](../../../machine-learning/supervised-learning/classification/support-vector-machines/README.md) |
| Modified | [machine-learning/supervised-learning/regression/README.md](../../../machine-learning/supervised-learning/regression/README.md) |
| Modified | [machine-learning/supervised-learning/regression/decision-tree-regression/README.md](../../../machine-learning/supervised-learning/regression/decision-tree-regression/README.md) |
| Modified | [machine-learning/supervised-learning/regression/elastic-net/README.md](../../../machine-learning/supervised-learning/regression/elastic-net/README.md) |
| Modified | [machine-learning/supervised-learning/regression/lasso-regression/README.md](../../../machine-learning/supervised-learning/regression/lasso-regression/README.md) |
| Modified | [machine-learning/supervised-learning/regression/linear-regression/README.md](../../../machine-learning/supervised-learning/regression/linear-regression/README.md) |
| Modified | [machine-learning/supervised-learning/regression/polynomial-regression/README.md](../../../machine-learning/supervised-learning/regression/polynomial-regression/README.md) |
| Modified | [machine-learning/supervised-learning/regression/ridge-regression/README.md](../../../machine-learning/supervised-learning/regression/ridge-regression/README.md) |
| Modified | [machine-learning/supervised-learning/regression/support-vector-regression/README.md](../../../machine-learning/supervised-learning/regression/support-vector-regression/README.md) |
| Modified | [machine-learning/time-series/README.md](../../../machine-learning/time-series/README.md) |
| Modified | [machine-learning/time-series/arima/README.md](../../../machine-learning/time-series/arima/README.md) |
| Modified | [machine-learning/time-series/exponential-smoothing/README.md](../../../machine-learning/time-series/exponential-smoothing/README.md) |
| Modified | [machine-learning/time-series/hidden-markov-models/README.md](../../../machine-learning/time-series/hidden-markov-models/README.md) |
| Modified | [machine-learning/time-series/holt-winters/README.md](../../../machine-learning/time-series/holt-winters/README.md) |
| Modified | [machine-learning/time-series/prophet/README.md](../../../machine-learning/time-series/prophet/README.md) |
| Modified | [machine-learning/time-series/sarima/README.md](../../../machine-learning/time-series/sarima/README.md) |
| Modified | [machine-learning/unsupervised-learning/README.md](../../../machine-learning/unsupervised-learning/README.md) |
| Modified | [machine-learning/unsupervised-learning/association-rule-learning/README.md](../../../machine-learning/unsupervised-learning/association-rule-learning/README.md) |
| Modified | [machine-learning/unsupervised-learning/association-rule-learning/apriori/README.md](../../../machine-learning/unsupervised-learning/association-rule-learning/apriori/README.md) |
| Modified | [machine-learning/unsupervised-learning/association-rule-learning/eclat/README.md](../../../machine-learning/unsupervised-learning/association-rule-learning/eclat/README.md) |
| Modified | [machine-learning/unsupervised-learning/association-rule-learning/fp-growth/README.md](../../../machine-learning/unsupervised-learning/association-rule-learning/fp-growth/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/README.md](../../../machine-learning/unsupervised-learning/clustering/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/agglomerative-hierarchical-clustering/README.md](../../../machine-learning/unsupervised-learning/clustering/agglomerative-hierarchical-clustering/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/dbscan/README.md](../../../machine-learning/unsupervised-learning/clustering/dbscan/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/divisive-hierarchical-clustering/README.md](../../../machine-learning/unsupervised-learning/clustering/divisive-hierarchical-clustering/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/gaussian-mixture-models/README.md](../../../machine-learning/unsupervised-learning/clustering/gaussian-mixture-models/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/hdbscan/README.md](../../../machine-learning/unsupervised-learning/clustering/hdbscan/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/k-means/README.md](../../../machine-learning/unsupervised-learning/clustering/k-means/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/mean-shift/README.md](../../../machine-learning/unsupervised-learning/clustering/mean-shift/README.md) |
| Modified | [machine-learning/unsupervised-learning/clustering/spectral-clustering/README.md](../../../machine-learning/unsupervised-learning/clustering/spectral-clustering/README.md) |
| Modified | [machine-learning/unsupervised-learning/dimensionality-reduction/README.md](../../../machine-learning/unsupervised-learning/dimensionality-reduction/README.md) |
| Modified | [machine-learning/unsupervised-learning/dimensionality-reduction/independent-component-analysis/README.md](../../../machine-learning/unsupervised-learning/dimensionality-reduction/independent-component-analysis/README.md) |
| Modified | [machine-learning/unsupervised-learning/dimensionality-reduction/linear-discriminant-analysis-projection/README.md](../../../machine-learning/unsupervised-learning/dimensionality-reduction/linear-discriminant-analysis-projection/README.md) |
| Modified | [machine-learning/unsupervised-learning/dimensionality-reduction/principal-component-analysis/README.md](../../../machine-learning/unsupervised-learning/dimensionality-reduction/principal-component-analysis/README.md) |
| Modified | [machine-learning/unsupervised-learning/dimensionality-reduction/singular-value-decomposition/README.md](../../../machine-learning/unsupervised-learning/dimensionality-reduction/singular-value-decomposition/README.md) |
| Modified | [machine-learning/unsupervised-learning/dimensionality-reduction/t-sne/README.md](../../../machine-learning/unsupervised-learning/dimensionality-reduction/t-sne/README.md) |
| Modified | [machine-learning/unsupervised-learning/dimensionality-reduction/umap/README.md](../../../machine-learning/unsupervised-learning/dimensionality-reduction/umap/README.md) |
| Modified | [scripts/generate_catalog_docs.py](../../../scripts/generate_catalog_docs.py) |
| Modified | [scripts/validate_catalog.py](../../../scripts/validate_catalog.py) |
| Modified | [tests/test_generate_catalog_docs.py](../../../tests/test_generate_catalog_docs.py) |
| Modified | [tests/test_validate_catalog.py](../../../tests/test_validate_catalog.py) |

## Mandatory review checkpoint

**STOP: Sorting is complete and awaiting the user's review.** Do not implement Searching or any other category, expand scope, commit, publish, or push without the user's explicit authorization. Preparing or validating this ZIP does not grant that approval.
