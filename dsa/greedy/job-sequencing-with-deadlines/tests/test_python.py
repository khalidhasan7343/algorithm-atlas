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
        result=python_algorithm.job_sequencing(*args)[0]
        assert result==expected
        assert args==before
        cases.validate(dict(zip(("profit","slots"),python_algorithm.job_sequencing(*args))),args,expected)

def test_api_boundaries(python_algorithm):

    for args in [([-1],[1]),([True],[1]),([1],[True]),([10**9+1],[1]),([1],[10**9+1]),([1],[-10**9-1]),([1],[]),([1]*10001,[1]*10001)]:
        with pytest.raises(ValueError):python_algorithm.job_sequencing(*args)
    assert python_algorithm.job_sequencing([1,1],[5,5])==(5,[0])
    assert python_algorithm.job_sequencing([2,2],[5,5])==(10,[1,0])
    assert python_algorithm.job_sequencing([2,2],[-1,0])==(0,[None,None])
    assert python_algorithm.job_sequencing([0],[100])==(0,[])

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='5 2 100 1 19 2 27 1 25 3 15\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='{"profit":142,"slots":[2,0,4]}' and not result.stderr
    for text in ['', '-1', '1 1', '1 -1 5', '1 1 true', '0 extra', '1 1000000001 1']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
