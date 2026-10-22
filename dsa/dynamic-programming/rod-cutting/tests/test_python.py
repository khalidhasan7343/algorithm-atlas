"""Independent expected values, input preservation, invalid/resource boundaries."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm, cases):
    for args, expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert python_algorithm.rod_cutting(*args) == expected
        assert args == saved

def test_invalid_and_numeric_boundaries(python_algorithm):

    for args in [([True],1),([10**9+1],1),([], -1),([],10001),([0]*1001,0),([1]*1000,2000)]:
        with pytest.raises(ValueError):
            python_algorithm.rod_cutting(*args)

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='4 4 2 5 7 8\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='10' and not result.stderr
    for text in ['', '-1 0', '1 -1', '1 1', '1 1 none', '1 0 extra']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
