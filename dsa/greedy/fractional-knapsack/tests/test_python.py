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
        result=cases.normal(python_algorithm.fractional_knapsack(*args))
        assert result==expected
        assert args==before
        assert sum(Fraction(*f)*w for f,w in zip(result["fractions"],args[0]))<=args[2]

def test_api_boundaries(python_algorithm):

    invalid=[([0],[1],1),([-1],[1],1),([1],[-1],1),([1],[],1),([],[],-1),([],[],10**9+1),
             ([True],[1],1),([1],[True],1),([10**6+1],[1],1),([1],[10**6+1],1),([1]*10001,[1]*10001,0)]
    for args in invalid:
        with pytest.raises(ValueError):python_algorithm.fractional_knapsack(*args)
    value,fractions=python_algorithm.fractional_knapsack([3],[2],1)
    assert value==Fraction(2,3) and fractions==[Fraction(1,3)]
    assert isinstance(value,Fraction)

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='50 3 10 60 20 100 30 120\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='{"value":[240,1],"fractions":[[1,1],[1,1],[2,3]]}' and not result.stderr
    for text in ['', '-1 0', '0 -1', '1 1 0 1', '1 1 1 -1', '1 1 1', '1 0 extra', '1 1 1_0 2']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
