import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b11_support', Path(__file__).parent/'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)

import pytest

@pytest.fixture(scope='session')
def b11():
    return s

@pytest.fixture(autouse=True)
def global_rng_guard():
    before = np.random.get_state()
    yield
    after = np.random.get_state()
    assert before[0] == after[0] and np.array_equal(before[1], after[1]) and before[2:] == after[2:]
