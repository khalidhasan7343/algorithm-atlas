import importlib.util
from pathlib import Path
import sys
import numpy as np
import pytest

p=Path(__file__).parent/'support.py'
spec=importlib.util.spec_from_file_location('atlas_b13_support',p)
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)

@pytest.fixture
def b13():return s

@pytest.fixture(autouse=True)
def global_rng_guard():
    before=np.random.get_state()
    yield
    after=np.random.get_state()
    assert before[0]==after[0] and np.array_equal(before[1],after[1]) and before[2:]==after[2:]
