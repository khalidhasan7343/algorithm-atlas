# Contributing to Algorithm Atlas

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343) for learners studying DSA, machine learning, and artificial intelligence. Contributions should make the material accurate, understandable, and reproducible. Participation follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Current phase and approval

**Phase 1 (Sorting) is reviewed and owner-approved. Phase 2 authorizes Searching only**: Batch 1 — Linear, Binary, Jump; Batch 2 — Interpolation, Exponential, Ternary. Finish and validate each batch before automatically continuing. Preserve all Sorting implementations and tests. Save actual results in the [Searching checkpoint](docs/searching-checkpoints.md). After Searching, stop for explicit human review; every other category requires separate approval. Passing tests does not expand scope.

GitHub publishing, pushing, and changes to Git identity require separate authorization. Do not treat the public contact email as an authorized commit identity. No automation in this project commits or pushes changes.

## Prepare a development environment

Use Python 3.11+ and a compiler supporting C++17/C++20. From your checkout:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest
```

Windows activation and compiler details are in [getting started](docs/getting-started.md). Missing dependencies or a skipped compiler test must be reported explicitly; a skipped test is not evidence that C++ passed.

## Choose and scope a change

Check [catalog.yaml](catalog.yaml), the [algorithm index](docs/algorithm-index.md), and [progress](docs/progress.md) before starting. Work in small, reviewable batches for the current approved phase. Discuss ambiguous terminology, scope changes, or additional heavy dependencies before depending on them. The unresolved Dynamic Policy Optimization label remains blocked until clarified.

Each unique algorithm has one canonical location. Link to it from other syllabus categories instead of duplicating its implementation. Distinct variants need a documented reason for their own folder. Use lowercase kebab-case directory names.

## Documentation and implementation standards

Follow the [development guide](docs/development.md), including all 25 algorithm README sections. Explain intuition before code, define complexity variables, show correct dry runs and runnable examples, discuss relevant constraints, and use credible references. Do not invent deployments, citations, compatibility claims, or results. Planning READMEs are scheduling records and must be replaced with complete lessons in the appropriate approved phase.

Python code should use reusable functions/classes, descriptive names, PEP 8 formatting, and helpful type hints. C++ code should use C++17 or C++20, standard library facilities, safe ownership, and explicit boundary handling. DSA implementations must teach the algorithm itself. ML examples should distinguish from-scratch code from library usage, use small reproducible datasets, and disclose compute and dependency limits. Do not download large datasets or model weights automatically.

## Tests and honest status reporting

Add meaningful Python and C++ tests to each completed algorithm's `tests/` directory. Root pytest discovery includes these future tests. Use the shared C++ fixture described in [getting started](docs/getting-started.md). Choose edge cases that apply to the algorithm rather than copying irrelevant cases. Numerical and randomized methods need suitable tolerances and seeds; CI examples must stay small.

Update catalog statuses only when the corresponding work exists. Allowed statuses are `planned`, `in-progress`, `implemented`, `tested`, `reviewed`, and `blocked`. Keep documentation, Python, C++, and test status separate. Mark work `tested` only after actually running and passing the relevant tests. `reviewed` requires human review, and neither flag establishes phase approval.

Update catalog notes and regenerate the index/progress pages when appropriate:

```sh
python scripts/generate_catalog_docs.py
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest
```

The frozen [syllabus baseline](tests/fixtures/required_syllabus.json) is a completeness check against the original study roadmap. Do not edit it simply to make an accidental catalog omission pass. Intentional syllabus changes require an explained scope decision and review.

Static validation can verify files and consistency; it cannot prove that an algorithm is correct or that a claimed historical test run occurred. Include the actual command, environment, passed/failed/skipped results, and any checks not run in the pull request.

## Submit a reviewable change

Use a branch and a focused change description explaining the problem, resulting behavior, and validation. Suggested commit style includes `docs: initialize Algorithm Atlas documentation` and, after the relevant approval, `feat(dsa): implement basic sorting algorithms`. Do not create commits or push on behalf of the maintainer without authorization.

The [pull request template](.github/pull_request_template.md) records scope, checks, and unresolved issues. Fix known failures or explain the precise blocker before requesting review. Never include credentials, tokens, virtual environments, binaries, build caches, model checkpoints, or unnecessary datasets.

## Attribution and licensing

Contributions are distributed under the [MIT License](LICENSE). Preserve the project attribution to MD.Khalid Hasan and required notices for reused code or documentation; credit contributors accurately. Do not copy material whose license is incompatible or unclear. Repetitive copyright headers in every source file are unnecessary.

For project questions, contact [mdkhalidhasan7343@gmail.com](mailto:mdkhalidhasan7343@gmail.com). Do not publish private security information in an issue; follow [SECURITY.md](SECURITY.md).
