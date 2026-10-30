import importlib.util
from pathlib import Path
import sys
import pytest
spec=importlib.util.spec_from_file_location('atlas_b5_support',Path(__file__).resolve().parents[2]/'unsupervised-learning/dimensionality-reduction/support.py')
support=sys.modules.get(spec.name)
if support is None:
    support=importlib.util.module_from_spec(spec);sys.modules[spec.name]=support;spec.loader.exec_module(support)
@pytest.fixture
def b5():
    return support
