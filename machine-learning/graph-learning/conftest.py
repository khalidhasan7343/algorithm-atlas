import importlib.util
from pathlib import Path
import sys

import pytest
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b9_support', Path(__file__).parent / 'support.py')
b9_support = sys.modules.get(_spec.name)
if b9_support is None:
    b9_support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = b9_support
    _spec.loader.exec_module(b9_support)


@pytest.fixture(scope='session')
def b9():
    return b9_support


@pytest.fixture(autouse=True)
def preserve_test_rng_state():
    state = np.random.get_state()
    yield
    np.random.set_state(state)
