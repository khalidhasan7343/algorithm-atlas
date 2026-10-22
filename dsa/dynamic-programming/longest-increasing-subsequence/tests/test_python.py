"""Independent oracles, documented domains, mutation and CLI checks."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm,cases):
    for args,expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert python_algorithm.lis_length(*args) == expected
        assert args==saved

def test_boundaries(python_algorithm):

    for values in [[True],[1.5],[10**9+1],[0]*1001]:
        with pytest.raises(ValueError):
            python_algorithm.lis_length(values)
    assert python_algorithm.lis_length(list(range(1000)))==1000
    assert python_algorithm.lis_length(list(range(1000,0,-1)))==1

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='8 10 9 2 5 3 7 101 18\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='4' and not result.stderr
    for text in ['', '-1', '1', '1 1 2', '1 true', '1 1000000001']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
