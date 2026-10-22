"""Independent oracles, documented domains, mutation and CLI checks."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm,cases):
    for args,expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert python_algorithm.matrix_chain_cost(*args) == expected
        assert args==saved

def test_boundaries(python_algorithm):

    for dims in [[2],[0,2],[-1,2],[2,True],[2,1.5],[100001,2],[1]*102,[(2,3),(4,5)]]:
        with pytest.raises(ValueError):
            python_algorithm.matrix_chain_cost(dims)

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='4 10 30 5 60\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='4500' and not result.stderr
    for text in ['', '1 5', '2 0 2', '2 -1 2', '2 100001 2', '3 1 2', '0 extra']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
