# Algorithm Atlas

From Fundamental Algorithms to Advanced Artificial Intelligence — Learn, Implement, and Understand.

## Introduction

Algorithm Atlas is an educational, open-source project maintained by **MD.Khalid Hasan**. Its goal is to explain algorithms from first principles through clear documentation, Python and modern C++ implementations, meaningful tests, complexity analysis, and practical applications.

**Current state: Phase 9 fully completed and explicitly owner-approved; all four Phase 10 Bit Manipulation topics implemented and locally tested; owner review pending.** Follow [Bit checkpoints](docs/bit-manipulation-checkpoints.md), [fixed-width conventions](docs/bit-conventions.md) and [progress](docs/progress.md). Phase 8 remains completed and owner-approved; Phase 10 review is pending.

## Project Overview

A comprehensive collection of Data Structures, Algorithms, Machine Learning, and Artificial Intelligence concepts, explained from scratch with Python and C++ implementations, complexity analysis, and real-world applications.

The project serves CS students, DSA learners, competitive programmers, interview candidates, and developers studying ML and AI. The [catalog](catalog.yaml) is the source of truth for scope and status. Repeated syllabus topics point to one canonical folder; meaningful variants retain their own entries. Planning READMEs identify intended work and do not count as completed algorithm documentation.

The configured target repository is [khalidhasan7343/algorithm-atlas](https://github.com/khalidhasan7343/algorithm-atlas). Local setup does not establish that the repository has been published.

## Key Features

The foundation provides:

- A complete, categorized syllabus with canonical locations and explicit progress fields.
- A navigable [algorithm index](docs/algorithm-index.md) and eight-level [learning roadmap](docs/learning-roadmap.md).
- Documentation standards, pytest infrastructure, C++ compiler checks, and GitHub Actions configuration.
- Automated catalog, documentation-link, and implementation-status validation.

Sorting, Searching, Recursion & Backtracking, Divide & Conquer, the eleven Phase 5 Dynamic Programming topics, the four Phase 6 Greedy topics, all fifteen Phase 7 Graph topics, all fourteen Phase 8 Tree topics, all nine Phase 9 String topics, and four Phase 10 Bit Manipulation topics provide detailed explanations, dry runs, Python/C++ implementations, examples, and relevant edge-case tests. Other topics follow in separately approved phases. ML examples will distinguish educational implementations from library-based usage and document compute and dependency limits.

## Technologies Used

| Technology | Purpose |
| --- | --- |
| Python 3.11+ | Development tools, pytest, and completed DSA implementations |
| C++17 / C++20 | completed DSA implementations and compiler checks |
| pytest | Infrastructure tests and per-algorithm test discovery |
| PyYAML | Catalog parsing and validation |
| Markdown / YAML | Learning materials, catalog, and CI configuration |
| GitHub Actions | Lightweight validation and tests when run on GitHub |

No ML frameworks, models, or datasets are needed for Phase 0. Future topics will declare their own dependencies.

## Repository Structure

```text
algorithm-atlas/
├── README.md, LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md
├── catalog.yaml, requirements-dev.txt, pyproject.toml, conftest.py
├── .github/                # CI, issue forms, and pull request template
├── docs/                   # Index, roadmap, progress, guides, and reviews/<phase>/
├── artifacts/              # review-packages/<phase>/ ZIPs and integrity sidecars
├── scripts/                # Validation and generated-document checks
├── tests/                  # Infrastructure tests and syllabus baseline
├── dsa/                    # 12 syllabus categories
├── machine-learning/       # 13 syllabus categories, with supervised/unsupervised groups
└── artificial-intelligence/ # 10 syllabus categories
```

Review reports are indexed in [docs/reviews](docs/reviews/README.md); historical ZIPs and checksums are organized under [artifacts/review-packages](artifacts/review-packages/README.md). The [maintenance report](docs/maintenance/root-cleanup/REPORT.md) records moves and verification.

Each unique topic has one canonical folder. Completed Sorting, Searching, Recursion & Backtracking, Divide & Conquer, authorized Dynamic Programming, Greedy, Graph, Tree, String, and Bit Manipulation topics have a full lesson and `python/`, `cpp/`, and `tests/` content; planned topics retain honest scope READMEs. See the [development guide](docs/development.md) for the final per-algorithm structure and documentation standard.

## Data Structures and Algorithms

Explore [DSA](dsa/README.md): [sorting](dsa/sorting/README.md), [searching](dsa/searching/README.md), [recursion and backtracking](dsa/recursion-and-backtracking/README.md), [divide and conquer](dsa/divide-and-conquer/README.md), [graphs](dsa/graph-algorithms/README.md), [trees](dsa/tree-algorithms/README.md), [strings](dsa/string-algorithms/README.md), [bit manipulation](dsa/bit-manipulation/README.md), [number theory](dsa/number-theory/README.md), [two pointers and sliding windows](dsa/two-pointers-and-sliding-window/README.md), [greedy algorithms](dsa/greedy/README.md), and [dynamic programming](dsa/dynamic-programming/README.md).

## Machine Learning

Explore [machine learning](machine-learning/README.md): supervised [regression](machine-learning/supervised-learning/regression/README.md) and [classification](machine-learning/supervised-learning/classification/README.md), [ensembles](machine-learning/ensemble-methods/README.md), [clustering](machine-learning/unsupervised-learning/clustering/README.md), [dimensionality reduction](machine-learning/unsupervised-learning/dimensionality-reduction/README.md), [association rules](machine-learning/unsupervised-learning/association-rule-learning/README.md), [deep learning](machine-learning/deep-learning/README.md), [reinforcement learning](machine-learning/reinforcement-learning/README.md), [graph learning](machine-learning/graph-learning/README.md), [optimization](machine-learning/optimization/README.md), [time series](machine-learning/time-series/README.md), [anomaly detection](machine-learning/anomaly-detection/README.md), and [NLP](machine-learning/natural-language-processing/README.md).

## Artificial Intelligence

Explore [AI](artificial-intelligence/README.md): [uninformed search](artificial-intelligence/uninformed-search/README.md), [informed search](artificial-intelligence/informed-search/README.md), [local search](artificial-intelligence/local-search/README.md), [global optimization](artificial-intelligence/global-optimization/README.md), [adversarial search](artificial-intelligence/adversarial-search/README.md), [constraint satisfaction](artificial-intelligence/constraint-satisfaction/README.md), [multi-agent systems](artificial-intelligence/multi-agent-systems/README.md), [fuzzy logic](artificial-intelligence/fuzzy-logic/README.md), [swarm intelligence](artificial-intelligence/swarm-intelligence/README.md), and [computer vision](artificial-intelligence/computer-vision/README.md).

## Complete Algorithm Index

The [complete algorithm index](docs/algorithm-index.md) preserves every syllabus occurrence and links directly to canonical folders. [catalog.yaml](catalog.yaml) records difficulty, category, documentation/Python/C++/test statuses, related topics, and scope notes.

## Learning Roadmap

Follow the [eight-level roadmap](docs/learning-roadmap.md), from DSA foundations through advanced AI. Each level lists prerequisites and links to topic folders. Planned topics are destinations for future lessons, not currently runnable examples.

## How to Get Started

Read the [getting-started guide](docs/getting-started.md), browse the [index](docs/algorithm-index.md), and review [current progress](docs/progress.md). Start from your existing local checkout, or clone the target repository once it is available to you.

## Python Setup

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_catalog.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The development dependencies support the foundation tools; future algorithms may need additional explicitly documented packages.

## C++ Setup

Install a compiler supporting C++17 and C++20, such as GCC or Clang. Confirm the compiler with `g++ --version`; on macOS this command may invoke Apple Clang. Set `CXX=clang++` if you prefer a different compiler. The test fixtures compile temporary programs and do not require CMake.

## How to Run Examples

Use a completed topic in [Sorting](dsa/sorting/README.md); its README contains exact Python/C++ commands, inputs, outputs, and dependency instructions. For example, from the repository root:

```sh
printf '5 1 4 2 8\n' | python dsa/sorting/bubble-sort/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/bubble-sort/cpp/solution.cpp -o /tmp/atlas-bubble
printf '5 1 4 2 8\n' | /tmp/atlas-bubble
```

Both commands print `1 2 4 5 8`. Inputs contain values only, without a length prefix. Check each algorithm's input contract before using it.

For a Searching example, input starts with the target, followed by the sorted values:

```sh
printf '%s\n' '2 -5 0 2 2 9' | .venv/bin/python dsa/searching/binary-search/python/solution.py
```

This prints `2`, the first matching zero-based index. Sorted searches validate
order by default; see each [Searching lesson](dsa/searching/README.md) for its
contract and the extra validation cost.

For a Recursion & Backtracking example, print all row-to-column N-Queens
placements in deterministic order:

```sh
printf '4\n' | .venv/bin/python dsa/recursion-and-backtracking/n-queens/python/solution.py
```

This prints `[[1,3,0,2],[2,0,3,1]]`. Each lesson defines its own CLI grammar,
empty/impossible results, and duplicate/ordering semantics. Results can grow
exponentially; these eager recursive examples are intended for small inputs.

For the Divide & Conquer maximum-subarray example:

```sh
printf '%s\n' '-2 1 -3 4 -1 2 1 -5 4' | .venv/bin/python dsa/divide-and-conquer/maximum-subarray-divide-and-conquer/python/solution.py
```

This prints `["6",3,7]`: exact sum as a decimal string and the zero-based
half-open interval [3,7). Read each lesson's numeric, shape, tie, and CLI contract.

Repository checks can be run with:

```sh
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest
```

## Testing Instructions

Install [requirements-dev.txt](requirements-dev.txt), make a C++ compiler available, and run `python -m pytest` from the root. Infrastructure tests exercise catalog failures and compile/run small C++ toolchain checks. Per-algorithm tests exercise completed DSA implementations against independent expected values and reference oracles.

The [CI workflow](.github/workflows/ci.yml) checks documentation/catalog consistency and runs lightweight tests. Local test results and hosted CI results are separate: a workflow file does not imply a successful GitHub run. See [testing and contribution guidance](CONTRIBUTING.md) for future algorithm tests.

## Complexity Cheat Sheet

Use the [complexity cheat sheet](docs/complexity-cheatsheet.md) for asymptotic notation, common growth rates, space accounting, and assumptions. The [glossary](docs/glossary.md) defines terms used across DSA, ML, and AI.

## Project Progress

[Progress tracking](docs/progress.md) records catalog totals, completed and remaining algorithms, blockers, and the next proposed batch. The [Phase 0 review report](docs/phase-0-review.md) and [complete file inventory](docs/phase-0-files.md) document the foundation handoff. Phase 0 supplies the foundation only. The term **Dynamic Policy Optimization (DPO)** is retained from the syllabus and blocked pending clarification; it has not been replaced by Direct Preference Optimization.

Phase 9 received explicit owner approval on 2026-10-24 (Asia/Dhaka). Phase 10 covers the four Bit Manipulation canonicals in two sequential batches and ends with a verified review package and explicit owner checkpoint. Phase 11, commits, pushes and publication are not authorized.

## Contribution Guidelines

Read [CONTRIBUTING.md](CONTRIBUTING.md), the [development standards](docs/development.md), and the [Code of Conduct](CODE_OF_CONDUCT.md). Check the catalog before adding a topic, reuse canonical implementations across categories, and report actual test results. See the [security policy](SECURITY.md) for private vulnerability reports.

## Author and Maintainer

**Author:** MD.Khalid Hasan

**GitHub:** [khalidhasan7343](https://github.com/khalidhasan7343)

## Contact

**Public email:** [mdkhalidhasan7343@gmail.com](mailto:mdkhalidhasan7343@gmail.com)

Use the repository issue templates for reproducible bugs, documentation corrections, and algorithm proposals when GitHub hosting is available.

## License

**License:** [MIT License](LICENSE)

Copyright (c) 2026 MD.Khalid Hasan.
