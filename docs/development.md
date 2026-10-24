# Development Guide

This guide defines how to turn a planned Algorithm Atlas topic into an explained, executable, tested educational contribution. The project is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343); read [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution and attribution requirements.

## Phase boundaries

The owner explicitly approved Phase 8 on 2026-10-23 (Asia/Dhaka) and authorized **Phase 9 — String Algorithms only**: all nine A7 canonicals in three sequential validated [batches](string-algorithms-checkpoints.md). Preserve prior approved categories, historical reports/evidence and the 35/256/235 inventory. Use [byte-string contracts](string-conventions.md), genuine algorithms, independent oracles and exact 25-section lessons.

Finish each batch’s Python/C++17/C++20 tests and repository gates before continuing automatically. Report: docs/reviews/string-algorithms/STRING-ALGORITHMS-REVIEW-REPORT.md; ZIP/checksum/JSON: artifacts/review-packages/string-algorithms/. After validation and package integrity checks, STOP for explicit owner review. Do not mark Phase 9 human-approved, start Phase 10, commit, push or publish. Never set Git identity from the public email.

## Canonical layout and catalog ownership

[catalog.yaml](../catalog.yaml) is the topic inventory. The [algorithm index](algorithm-index.md) retains the syllabus's category navigation while linking repeated subjects to one canonical folder. Before adding a folder, check related records and their notes: a repeated category label often describes an existing algorithm, while a meaningful variant may warrant a separate entry.

Use lowercase kebab-case for folders. Once implementation is authorized, a normal algorithm folder contains:

```text
<canonical-folder>/
├── README.md
├── python/
│   └── solution.py
├── cpp/
│   └── solution.cpp
└── tests/
    ├── test_python.py
    └── test_cpp.py
```

Add a dependency manifest, build file, small input fixture, or example driver when a topic actually needs it. Avoid empty files, duplicate implementations in different categories, generated binaries, virtual environments, large datasets, and model checkpoints. Keep all execution instructions relative to a stated working directory.

## Required algorithm README sections

Every completed algorithm README must contain these **25 numbered sections with these titles**. A Phase 0 planning README does not claim to meet the completed-algorithm documentation standard.

| Section | Required content |
| --- | --- |
| 1. Algorithm Name | Give the full name and common abbreviation; distinguish related variants. |
| 2. Overview | Introduce the primary purpose in clear language. |
| 3. Problem Statement | State the input, output, and exact computational task. |
| 4. Why Do We Need This Algorithm? | Explain the motivation and benefits under stated assumptions. |
| 5. Real-World Applications | Describe credible uses and why the method fits; do not invent deployments. |
| 6. Core Intuition | Explain the central idea before code and implementation details. |
| 7. Prerequisites | List the concepts needed, linking existing project material where appropriate. |
| 8. Step-by-Step Working Process | Explain each step, termination, and the invariant or reasoning supporting correctness. |
| 9. Pseudocode | Provide readable language-independent pseudocode matching the implemented variant. |
| 10. Dry Run | Trace a concrete input through intermediate states to the verified result. |
| 11. Time Complexity | Define every variable, justify bounds, and give best, average, and worst cases where meaningful. |
| 12. Space Complexity | Distinguish auxiliary memory, total storage, and recursion stack. |
| 13. Python Implementation | Explain the Python design and link to its actual working source. |
| 14. C++ Implementation | Explain the C++ design and link to its actual working source. |
| 15. Input and Output Examples | Provide correct, reproducible examples and exact run commands. |
| 16. Edge Cases | Explain relevant boundary conditions, invalid inputs, and failure behavior. |
| 17. Advantages | Discuss the practical benefits with their conditions. |
| 18. Disadvantages and Limitations | Explain weaknesses, assumptions, resource limits, and numerical limitations. |
| 19. When to Use It | Give concrete selection criteria. |
| 20. When Not to Use It | Explain cases where a different approach fits better. |
| 21. Comparison With Related Algorithms | Compare relevant alternatives; use a table when it clarifies tradeoffs. |
| 22. Interview Questions | Include questions that test understanding, correctness, and implementation choices. |
| 23. Practice Problems | Provide progressively harder exercises; verify any external problem links. |
| 24. References | Link credible, verifiable sources, preferably original papers and official documentation. Never invent a citation. |
| 25. Author Attribution | Link the project maintainer and repository contribution information without inventing personal details. |

The section numbering and order make documentation predictable. Fill sections with material specific to the implemented variant; a heading followed by generic text or a TODO is not complete documentation. Reference the MIT license and contribution policy where useful without repeating copyright boilerplate in every source file.

## Implementation expectations

Python code should follow PEP 8, expose reusable functions or classes, use type hints where helpful, and keep demonstrations from running at import time. Explain difficult logic with focused comments. Standard library facilities are welcome, but DSA contributions must demonstrate the named algorithm rather than delegate the entire task to a built-in equivalent.

C++ code should use C++17 or a documented C++20 requirement, descriptive names, standard library facilities, clear ownership, and safe boundary handling. Avoid nonstandard headers and compiler-specific assumptions unless a topic explicitly requires them. Document the exact command that builds and runs its example.

For ML topics, provide an educational from-scratch implementation and a practical library example when feasible. Label each honestly. Specify package versions or compatible ranges, installation commands, dataset shape, random seed, numeric precision, stopping conditions, and expected resource needs. C++ dependencies such as Eigen, LibTorch, or OpenCV need explicit build and link instructions. Add only dependencies actually required by that topic.

Keep advanced examples compact and reproducible. A miniature Transformer, diffusion example, or object detector must explain its scope and how it differs from a full production model. Do not automatically download large datasets or weights. If a requested implementation cannot be completed faithfully, record the blocked or in-progress status and exact limitation instead of presenting a fake working version.

## Test design

Use pytest for repository checks and appropriate Python tests. Future per-algorithm Python tests should exercise observable behavior and independently known answers. For deterministic DSA topics, compare Python and C++ results on shared cases where practical, but include independent expected values so agreement alone cannot hide a shared bug.

Choose boundary cases that fit the contract: empty and single-element inputs, repeated values, orderings, negative values, extreme values, invalid inputs, graph connectivity, or algorithm-specific constraints. Do not force irrelevant sorting cases onto another topic. Check mutation behavior, exception behavior, and return types when they are part of the API.

For numerical and ML topics, use small reproducible datasets and fixed seeds when applicable. Check mathematical properties, shapes, finite outputs, and basic model behavior with justified tolerances. Separate training cost from prediction cost. Expensive experiments must not enter default lightweight CI; describe any optional longer checks and their dependencies explicitly.

Compile and **execute** C++ tests with the shared pytest harness once a topic has an implementation. A successful compilation alone does not verify behavior. Keep build output in pytest temporary directories and place a timeout on execution. See [conftest.py](../conftest.py) for the shared fixture contract and the infrastructure tests for examples.

The `cpp_compile` fixture accepts a source `pathlib.Path` and optional keyword arguments `output_name="program"` and `extra_flags=()`. It returns the executable's temporary `Path`. The `cpp_standard` fixture parametrizes builds over `c++17` and `c++20`; `--cpp-standard=c++17` or `--cpp-standard=c++20` selects one standard. Use `subprocess.run` with explicit arguments, `capture_output=True`, `text=True`, `check=True`, and an appropriate timeout to verify the executable's result. A library topic may need an explicit test driver rather than compiling its source alone.

The harness honors `CXX`; otherwise it selects an available `g++` or `clang++`. On macOS, the `g++` command may invoke Apple Clang. `--require-cpp` makes a missing compiler a failure; without it, compiler-dependent checks can skip, and that skip must appear in the reported results. The default full smoke suite requires both language standards. A C++17-only selected run leaves C++20 unrun and must be reported that way. CI requires a compiler. For example, `CXX=clang++ .venv/bin/python -m pytest --require-cpp` selects Clang explicitly.

## Local checks and CI

Set up the environment using [Getting Started](getting-started.md), then run from the root:

```sh
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python -m pytest
```

The first command validates the catalog, documentation paths and links, and claims implied by statuses. The second checks that generated navigation and progress documents match the catalog; run it without `--check` after an intentional catalog change to regenerate them. Pytest checks the infrastructure and discovers future per-algorithm tests. The [GitHub Actions workflow](../.github/workflows/ci.yml) runs lightweight checks; it only runs remotely after an authorized publication and GitHub event.

Record the exact commands, observed outcomes, and any skipped or unavailable checks in each development summary. Never describe a test as passed because configuration exists. CI supports only its explicitly configured environments; success there does not establish compatibility with every Python version, compiler, platform, library, or hardware accelerator.

## Status and completion discipline

Update documentation, Python, C++, and test statuses in the catalog after each batch, and update [progress.md](progress.md) from the actual state. The supported statuses are `planned`, `in-progress`, `implemented`, `tested`, `reviewed`, and `blocked`. They describe evidence, not a promise.

- Use `planned` for work that has not started; a planning README is not completed algorithm documentation.
- Use `in-progress` for work actively underway and explain unfinished parts.
- Use `implemented` only when the corresponding deliverable exists and its described behavior is present.
- Use `tested` only after the relevant tests genuinely pass; record the commands and environment.
- Use `reviewed` only after actual review, with the same implementation and test evidence expected for completion.
- Use `blocked` when a concrete dependency, terminology issue, or other obstacle prevents faithful work, and state the resolution needed.

Do not mark an algorithm complete while either language, its tests, examples, documentation, or required dependencies remain unverified. `Dynamic Policy Optimization (DPO)` is a [terminology question](terminology-decisions.md) in the supplied syllabus; it must remain explicit until the maintainer clarifies the intended method. Do not silently replace it with Direct Preference Optimization.

## Batch handoff

Before requesting the next phase's approval, report the files changed, algorithms completed, actual checks and results, unresolved issues, catalog/progress changes, and next proposed batch. Keep the checkpoint reviewable and stop development until the maintainer approves the next phase. Do not set a Git commit identity from the maintainer's public email without explicit authorization, and do not push without permission.


## Review files and root organization

Future phase reports belong in `docs/reviews/<phase-name>/`; ZIPs, checksums and package JSON belong in `artifacts/review-packages/<phase-name>/`. Keep only essential project documentation, configuration and established source/infrastructure directories at the root. Update `development.completion_report`, live Markdown links, tracking checks and packaging paths whenever a report moves. Every completion report must exist, be nonempty, tracked and unignored.

The final review ZIP must contain the updated repository and required reports, excluding caches, virtual environments, secrets, binaries and unnecessary nested review archives/sidecars. Preserve genuine historical ZIPs and execution evidence; their internal snapshot paths/hashes remain historical. Do not force-add ignored artifacts. Existing phase-owner approval checkpoints remain mandatory; maintenance itself does not approve phases; the owner subsequently approved Phase 8 and authorized Phase 9. Do not commit, push or publish without explicit owner authorization.
