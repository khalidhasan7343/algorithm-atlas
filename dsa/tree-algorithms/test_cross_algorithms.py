"""Persist the full independent cross-algorithm matrix in the regression suite."""
import importlib.util
from pathlib import Path

def test_tree_cross_matrix():
    path=Path(__file__).resolve().parents[2]/'scripts/verify_tree_cross_algorithms.py'
    spec=importlib.util.spec_from_file_location('tree_cross_matrix',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.verify(5,write_evidence=False)
    assert result['failures']==0 and len(result['comparisons'])==5
