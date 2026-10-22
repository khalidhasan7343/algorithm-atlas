"""Canonical imports and executable C++ API/CLI fixtures."""
import importlib.util
import json
from pathlib import Path
import subprocess
import pytest


def load(source, prefix):
    spec = importlib.util.spec_from_file_location(prefix + source.parents[1].name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def python_algorithm(request):
    return load(Path(request.node.path).parents[1] / "python/solution.py", "tree_")


@pytest.fixture(scope="module")
def cases(request):
    return load(Path(request.node.path).parent / "cases.py", "tree_cases_")


@pytest.fixture
def cpp_api(request, cpp_compile, tmp_path):
    source = Path(request.node.path).parents[1] / "cpp/solution.cpp"
    def build(body):
        driver = tmp_path / "api.cpp"
        driver.write_text('#define ALGORITHM_ATLAS_NO_MAIN\n#include ' + json.dumps(str(source.resolve()))
                          + '\nusing namespace atlas_tree;\nint main() {\n' + body + '\n}\n')
        executable = cpp_compile(driver)
        def run(text):
            result = subprocess.run([str(executable)], input=text, text=True, capture_output=True, check=True, timeout=30)
            assert not result.stderr
            return [json.loads(line) for line in result.stdout.splitlines()]
        return run
    return build


@pytest.fixture
def cpp_cli(request, cpp_compile):
    return cpp_compile(Path(request.node.path).parents[1] / "cpp/solution.cpp")
