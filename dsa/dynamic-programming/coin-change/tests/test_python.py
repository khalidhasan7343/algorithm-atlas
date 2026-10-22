"""Independent expected values, input preservation, invalid/resource boundaries."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm, cases):
    for args, expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert [python_algorithm.minimum_coins(*args), python_algorithm.count_combinations(*args)] == expected
        assert args == saved

def test_invalid_and_numeric_boundaries(python_algorithm):

    for args in [([0],1), ([-1],0), ([True],1), ([1],-1), ([1],10001), ([1]*1001,0), ([1]*1000,2000)]:
        for function in [python_algorithm.minimum_coins, python_algorithm.count_combinations]:
            with pytest.raises(ValueError):
                function(*args)
    with pytest.raises(OverflowError):
        python_algorithm.count_combinations(list(range(1,501)),500)
    assert python_algorithm.minimum_coins([1],10000) == 10000
    assert python_algorithm.count_combinations([1],10000) == 1

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='6 3 1 3 4\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='[2,4]' and not result.stderr
    for text in ['', '-1 0', '1 1 0', '1 1 -2', '1 2 1', '1 0 extra']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
