"""Shared test-only API drivers; independent oracles live in algorithm tests."""

import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


@pytest.fixture(scope="module")
def python_algorithm(request):
    folder = Path(request.node.path).parents[1]
    spec = importlib.util.spec_from_file_location(
        "backtracking_" + folder.name.replace("-", "_"),
        folder / "python/solution.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def cpp_api(request, cpp_compile, tmp_path):
    """Compile a driver and execute a batch of test cases in one process."""
    source = Path(request.node.path).parents[1] / "cpp/solution.cpp"

    def build(body, extra=""):
        driver = tmp_path / "api_driver.cpp"
        driver.write_text(
            '#define ALGORITHM_ATLAS_NO_MAIN\n#include '
            + json.dumps(str(source.resolve())) + '\n' + DRIVER_IO
            + extra + '\nint main() {\n' + body + '\n}\n'
        )
        executable = cpp_compile(driver)

        def invoke(text):
            result = subprocess.run(
                [str(executable)], input=text, text=True, capture_output=True,
                timeout=30, check=True,
            )
            assert result.stderr == ""
            return [json.loads(line) for line in result.stdout.splitlines()]

        return invoke

    return build


@pytest.fixture
def cpp_cli(request, cpp_compile):
    source = Path(request.node.path).parents[1] / "cpp/solution.cpp"
    return cpp_compile(source)


DRIVER_IO = r'''
#include <cassert>
template <typename T> void emit(const std::vector<T>& value);
template <typename T> void emit(const std::optional<T>& value);
template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
void emit(T value) { std::cout << value; }
void emit(const std::string& value) { std::cout << std::quoted(value); }
template <typename T> void emit(const std::vector<T>& value) {
    std::cout << '[';
    for (std::size_t i = 0; i < value.size(); ++i) {
        if (i) { std::cout << ','; }
        emit(value[i]);
    }
    std::cout << ']';
}
template <typename T> void emit(const std::optional<T>& value) {
    if (value) { emit(*value); } else { std::cout << "null"; }
}
template <typename F> void reply(F action) {
    try { emit(action()); }
    catch (const std::invalid_argument&) {
        std::cout << R"({"error":"invalid_argument"})";
    }
    std::cout << '\n';
}
'''


@pytest.fixture(scope="module")
def cases(request):
    source = Path(request.node.path).parent / "cases.py"
    spec = importlib.util.spec_from_file_location("cases_" + source.parents[1].name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
