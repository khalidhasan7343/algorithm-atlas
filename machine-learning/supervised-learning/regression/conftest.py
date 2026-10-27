"""Import canonical Python modules without depending on hyphenated package names."""
import importlib.util
from pathlib import Path
import sys

import pytest


@pytest.fixture(scope="module")
def algorithm(request):
    folder = Path(request.node.path).parents[1]
    spec = importlib.util.spec_from_file_location("test_regression_" + folder.name.replace("-", "_"), folder / "python/solution.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
