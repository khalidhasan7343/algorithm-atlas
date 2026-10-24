"""Load canonical modules and compile API drivers with the repository fixture."""
import importlib.util
import json
from pathlib import Path
import subprocess
import pytest


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def python_algorithm(request):
    folder = Path(request.node.path).parents[1]
    return load(folder/"python/solution.py", "window_"+folder.name)


@pytest.fixture(scope="module")
def oracle():
    return load(Path(__file__).parent/"oracles.py", "window_oracles")


@pytest.fixture(scope="module")
def name(request):
    return Path(request.node.path).parents[1].name


@pytest.fixture
def cpp_driver(request, cpp_compile, tmp_path):
    source = Path(request.node.path).parents[1]/"cpp/solution.cpp"
    def build(body):
        driver = tmp_path/"api.cpp"
        driver.write_text('#define ALGORITHM_ATLAS_NO_MAIN\n#include '+json.dumps(str(source.resolve()))+
                          '\nusing namespace atlas_window;\nint main() {\n'+body+'\n}\n')
        binary = cpp_compile(driver)
        def run(data):
            result = subprocess.run([str(binary)],input=data,text=True,capture_output=True,timeout=30)
            assert result.returncode == 0, result.stderr
            assert not result.stderr
            return [json.loads(line) for line in result.stdout.splitlines()]
        return run
    return build


@pytest.fixture
def cpp_cli(request, cpp_compile):
    return cpp_compile(Path(request.node.path).parents[1]/"cpp/solution.cpp")
