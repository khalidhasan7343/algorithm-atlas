"""Import standalone lessons and compile batched API drivers under both standards."""
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


@pytest.fixture(scope="module")
def python_algorithm(request):
    source = Path(request.node.path).parents[1] / "python/solution.py"
    spec = importlib.util.spec_from_file_location("dp_" + source.parents[1].name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def cases(request):
    source = Path(request.node.path).parent / "cases.py"
    spec = importlib.util.spec_from_file_location("dp_cases_" + source.parents[1].name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def cpp_api(request, cpp_compile, tmp_path):
    source = Path(request.node.path).parents[1] / "cpp/solution.cpp"

    def build(body):
        driver = tmp_path / "api.cpp"
        driver.write_text(
            '#define ALGORITHM_ATLAS_NO_MAIN\n#include '
            + json.dumps(str(source.resolve()))
            + '\n#include <iomanip>\n#include <cassert>\n'
            + 'using namespace atlas_dp;\nint main() {\n' + body + '\n}\n'
        )
        binary = cpp_compile(driver)

        def run(text):
            result = subprocess.run([str(binary)], input=text, text=True,
                                    capture_output=True, check=True, timeout=30)
            assert result.stderr == ""
            return [json.loads(line) for line in result.stdout.splitlines()]

        return run

    return build


@pytest.fixture
def cpp_cli(request, cpp_compile):
    return cpp_compile(Path(request.node.path).parents[1] / "cpp/solution.cpp")
