"""Canonical B4 imports without changing the global import path."""
import importlib.util
from pathlib import Path
import sys
import pytest

spec = importlib.util.spec_from_file_location('atlas_clustering_support', Path(__file__).with_name('support.py'))
support = sys.modules.get(spec.name)
if support is None:
    support = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = support
    spec.loader.exec_module(support)


@pytest.fixture
def clustering_support():
    return support
