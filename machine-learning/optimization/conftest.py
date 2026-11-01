import importlib.util
from pathlib import Path
import sys
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).parent/'support.py')
support=sys.modules.get(spec.name)
if support is None:
    support=importlib.util.module_from_spec(spec);sys.modules[spec.name]=support;spec.loader.exec_module(support)


@pytest.fixture(scope='session')
def b10():
    return support


@pytest.fixture(scope='session')
def objectives():
    spec=importlib.util.spec_from_file_location('atlas_b10_test_objectives',Path(__file__).parent/'tests/objectives.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def preserve_rng():
    state=np.random.get_state()
    yield
    np.random.set_state(state)
