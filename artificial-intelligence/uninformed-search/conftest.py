"""C1 fixtures: load canonical modules by path and build/run C++ API drivers and CLIs."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

CATEGORY = Path(__file__).resolve().parent


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(folder: str):
    return load(CATEGORY / folder / "python/solution.py", "c1_" + folder.replace("-", "_"))


@pytest.fixture(scope="module")
def algorithm(request):
    """The Python canonical module of the folder that owns the requesting test."""
    folder = Path(request.node.path).parents[1]
    return load(folder / "python/solution.py", "c1_test_" + folder.name.replace("-", "_"))


@pytest.fixture(scope="module")
def oracles():
    return load(CATEGORY / "tests/oracles.py", "c1_oracles")


@pytest.fixture(scope="module")
def encoding():
    return load(CATEGORY / "tests/encoding.py", "c1_encoding")


def multi_case_driver(kind: str) -> str:
    """C++ main() body: solve one token-grammar problem per input line."""
    return ("std::string line;\nwhile (std::getline(std::cin, line)) {\n"
            "    std::istringstream in(line);\n"
            f"    solve_{kind}_problem(parse_problem(in, \"{kind}\"), std::cout);\n}}")


@pytest.fixture
def cpp_cli(request, cpp_compile):
    return cpp_compile(Path(request.node.path).parents[1] / "cpp/solution.cpp")


@pytest.fixture
def cpp_api(request, cpp_compile, tmp_path):
    """Compile ``body`` as main() after including the canonical source without its CLI."""
    source = Path(request.node.path).parents[1] / "cpp/solution.cpp"

    def build(body: str):
        driver = tmp_path / "api.cpp"
        driver.write_text("#define ATLAS_UNINFORMED_NO_MAIN\n#include <sstream>\n#include " + json.dumps(str(source.resolve()))
                          + "\nusing namespace atlas_search;\nint main() {\n" + body + "\n}\n")
        executable = cpp_compile(driver, output_name="api")

        def run(text: str = "") -> list:
            result = subprocess.run([str(executable)], input=text, text=True, capture_output=True,
                                    check=True, timeout=60)
            assert not result.stderr
            return [json.loads(line) for line in result.stdout.splitlines()]
        return run
    return build


def run_cli(command: list[str], text: str) -> subprocess.CompletedProcess:
    return subprocess.run(command, input=text, text=True, capture_output=True, timeout=60)


@pytest.fixture(scope="session")
def case_driver():
    return multi_case_driver
