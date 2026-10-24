"""Shared loaders and batched C++ API drivers for the nine canonical lessons."""
import importlib.util
import json
from pathlib import Path
import subprocess
import pytest


def load(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def python_algorithm(request):
    return load(Path(request.node.path).parents[1]/"python/solution.py",
                "string_"+Path(request.node.path).parents[1].name)


@pytest.fixture(scope="module")
def oracle():
    return load(Path(__file__).parent/"string_oracles.py","string_oracles")


@pytest.fixture(scope="module")
def name(request):
    return Path(request.node.path).parents[1].name


@pytest.fixture(scope="module")
def kind(name):
    return "palindrome" if name == "manacher" else "multi" if name == "aho-corasick" else "match"


@pytest.fixture
def cpp_driver(request, cpp_compile, tmp_path):
    source = Path(request.node.path).parents[1]/"cpp/solution.cpp"
    def build(body):
        driver = tmp_path/"driver.cpp"
        driver.write_text('#define ALGORITHM_ATLAS_NO_MAIN\n#include '+json.dumps(str(source.resolve()))+
                          '\nusing namespace atlas_string;\nint main() {\n'+body+'\n}\n')
        executable = cpp_compile(driver)
        def run(data):
            result = subprocess.run([str(executable)],input=data,text=True,capture_output=True,timeout=30)
            assert result.returncode == 0, result.stderr
            assert not result.stderr
            return [json.loads(line) for line in result.stdout.splitlines()]
        return run
    return build


@pytest.fixture
def cpp_cli(request, cpp_compile):
    return cpp_compile(Path(request.node.path).parents[1]/"cpp/solution.cpp")


@pytest.fixture(scope="module")
def structure():
    return load(Path(__file__).parent/"structure_oracles.py","string_structures")
