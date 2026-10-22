"""Independent oracles, documented domains, mutation and CLI checks."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm,cases):
    for args,expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert python_algorithm.subset_sum(*args) == expected
        assert args==saved

def test_boundaries(python_algorithm):

    for args in [([-1],0),([True],1),([10**9+1],0),([],True),([],-1),([],10001),([0]*1001,0),([1]*1000,2000)]:
        with pytest.raises(ValueError):python_algorithm.subset_sum(*args)
    assert type(python_algorithm.subset_sum([],0)) is bool

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='9 6 3 34 4 12 5 2\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='true' and not result.stderr
    for text in ['', '-1 0', '0 1 -1', '1 1 true', '2 2 1', '1 0 extra']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
