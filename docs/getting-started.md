# Getting Started

Algorithm Atlas is an educational repository for Python and C++ implementations of DSA, machine learning, and artificial intelligence topics. **Phase 0 provides the catalog, documentation, and validation infrastructure. No algorithm implementations are available yet.** Canonical algorithm folders contain planning notes, and their catalog statuses remain planned or explicitly blocked.

Start with the [learning roadmap](learning-roadmap.md), browse the [complete algorithm index](algorithm-index.md), and consult the [progress tracker](progress.md) before choosing a topic. The [glossary](glossary.md) and [complexity cheat sheet](complexity-cheatsheet.md) explain terminology used throughout the project.

## Local prerequisites

- Python 3.11 or later with the `venv` module and pip. Check the project's [configuration](../pyproject.toml) and [CI workflow](../.github/workflows/ci.yml) for the environments that are actually exercised.
- A compiler supporting both C++17 and C++20, such as GCC's `g++` or Clang's `clang++`, for the full C++ infrastructure check. A C++17-only compiler can run a selected subset, as explained below. Individual topics will state their required standard.
- Git, if you intend to work on a local checkout or contribute changes.

The commands below use a POSIX shell from the repository root. On Windows, use the corresponding `.venv\Scripts\python.exe` path or a suitable development shell. A global Python package installation is unnecessary.

## Set up Python

If you already have a local checkout, enter its root directory. If you received a source archive, extract it first. The target GitHub URL in the root README identifies the intended repository; it is not a claim that publication has occurred.

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

The development requirements support repository checks and pytest. They do not install ML frameworks or download datasets. A future algorithm that needs additional packages must describe those dependencies and installation commands in its own README.

## Check C++ availability

```sh
g++ --version
```

An alternative compiler can be selected with `CXX`, as described in [development guidance](development.md). A compiler version banner alone does not prove that a future library or topic can build; its tests must compile and execute the relevant code.

## Validate the Phase 0 foundation

```sh
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python -m pytest
```

The validator checks the syllabus inventory, canonical locations, status consistency, and relative documentation links. The second command checks that generated navigation and progress documents match the catalog. Planned topics are allowed to lack implementation files; an implementation claim requires corresponding artifacts. Pytest exercises repository tooling and the C++ compilation harness. Passing these checks validates the foundation, not any unimplemented algorithm.

To require a compiler rather than allow compiler-dependent tests to skip when one is unavailable, use `.venv/bin/python -m pytest --require-cpp`. The default C++ infrastructure checks exercise both C++17 and C++20. Use `--cpp-standard=c++17` or `--cpp-standard=c++20` to select one standard, or `CXX=clang++ .venv/bin/python -m pytest --require-cpp` to select Clang explicitly. A selected C++17-only run does not check C++20; report the latter as unrun rather than passed.

If dependency installation or a check fails, preserve the exact error and identify the missing dependency or tool. Check the [development guide](development.md) for validation expectations and the [contribution guide](../CONTRIBUTING.md) before reporting a problem.

## Running examples after implementation

There are no algorithm examples to execute during Phase 0. After an algorithm is implemented and reviewed, follow the exact commands and input format in its README. The following paths illustrate the future convention and are not runnable files in Phase 0:

```text
<canonical-folder>/README.md
<canonical-folder>/python/solution.py
<canonical-folder>/cpp/solution.cpp
<canonical-folder>/tests/test_python.py
<canonical-folder>/tests/test_cpp.py
```

For a dependency-free topic with standalone example entry points, the future command pattern will be:

```text
.venv/bin/python <canonical-folder>/python/solution.py
g++ -std=c++17 -Wall -Wextra -Wpedantic <canonical-folder>/cpp/solution.cpp -o /tmp/atlas-example
/tmp/atlas-example
.venv/bin/python -m pytest <canonical-folder>/tests
```

Replace the angle-bracket path only when an implementation exists. Some topics will require extra compiler flags, libraries, data preparation, or a separate driver; their README must document those requirements accurately.

## Approval checkpoint

Phase 0 ends with maintainer review. Work on Phase 1, including Bubble Sort and the other sorting algorithms, must wait for the explicit instruction:

> Phase 0 Approved. Start Phase 1.

No push or publication is authorized by local setup or a passing test run. Review checkpoints apply between every later development phase as well.
