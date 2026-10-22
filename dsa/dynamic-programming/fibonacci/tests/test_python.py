"""Independent expected values, input preservation, invalid/resource boundaries."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm, cases):
    for args, expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert python_algorithm.fibonacci(*args) == expected
        assert args == saved

def test_invalid_and_numeric_boundaries(python_algorithm):

    for n in [-1, True, 1.5, "3"]:
        with pytest.raises(ValueError):
            python_algorithm.fibonacci(n)
    with pytest.raises(OverflowError):
        python_algorithm.fibonacci(93)
    assert python_algorithm.fibonacci(92) == 7540113804746346429

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='10\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='55' and not result.stderr
    for text in ['', '-1', '93', '2 3', '1_0', 'true']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
