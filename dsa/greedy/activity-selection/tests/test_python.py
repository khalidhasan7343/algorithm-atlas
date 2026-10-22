"""Independent expected values, resource boundaries and standalone CLI behavior."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import pytest

def test_independent_vectors(python_algorithm,cases):
    for args,expected in cases.vectors():
        before=copy.deepcopy(args)
        result=python_algorithm.activity_selection(*args)
        assert result==expected
        assert args==before
        assert all(args[0][a][1]<=args[0][b][0] for a,b in zip(result,result[1:]))

def test_api_boundaries(python_algorithm):

    for intervals in [[(1,1)],[(2,1)],[(True,2)],[(0,1.5)],[(0,10**9+1)],[(1,)],[(0,1)]*10001]:
        with pytest.raises(ValueError):python_algorithm.activity_selection(intervals)
    assert python_algorithm.activity_selection([(0,2),(0,2),(2,3)])==[0,2]
    assert python_algorithm.activity_selection([(1,3),(0,3),(3,4)])==[1,2]

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='5 1 3 2 5 3 4 4 7 5 6\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='[0,2,4]' and not result.stderr
    for text in ['', '-1', '1 0', '1 1 1', '1 2 1', '1 0 true', '0 extra', '1 0 1000000001']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
