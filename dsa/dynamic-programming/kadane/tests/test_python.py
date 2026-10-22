"""Independent oracles, documented domains, mutation and CLI checks."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm,cases):
    for args,expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert python_algorithm.maximum_subarray(*args) == expected
        assert args==saved

def test_boundaries(python_algorithm):

    for values in [[True],[1.5],[10**9+1],[-10**9-1],[0]*10001]:
        with pytest.raises(ValueError):python_algorithm.maximum_subarray(values)

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='9 -2 1 -3 4 -1 2 1 -5 4\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='["6",3,7]' and not result.stderr
    for text in ['', '-1', '1', '1 true', '1 1000000001', '1 1 2']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')

def test_shared_domain_agrees_with_divide_conquer(python_algorithm,cases):
    import importlib.util
    source=Path(__file__).parents[3]/'divide-and-conquer/maximum-subarray-divide-and-conquer/python/solution.py'
    spec=importlib.util.spec_from_file_location('prior_divide_subarray',source)
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    for args,expected in cases.vectors():
        assert prior.maximum_subarray(*args)==expected
        assert python_algorithm.maximum_subarray(*args)==expected
