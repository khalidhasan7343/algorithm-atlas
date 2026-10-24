from collections import Counter
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest


def test_recursive_oracle_and_input(python_algorithm, oracle):
    for values in oracle.subset_vectors():
        saved = list(values)
        actual = python_algorithm.solve(values)
        assert actual == oracle.recursive_subsets(values)
        assert len(actual) == 2**len(values)
        assert values == saved


def test_existing_power_set_and_duplicate_rows(python_algorithm):
    source = Path(__file__).resolve().parents[3]/"recursion-and-backtracking/power-set-generation/python/solution.py"
    spec = importlib.util.spec_from_file_location("bit_reference_backtracking",source)
    reference = importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
    for values in ([],[1,1],[2,-1,2],[-2147483648,0,2147483647],[0]*8):
        actual = python_algorithm.solve(values)
        expected = reference.power_set_generation(values)
        assert Counter(map(tuple,actual)) == Counter(map(tuple,expected))
    assert python_algorithm.solve([1,1]) == [[],[1],[1],[1,1]]
    assert python_algorithm.solve([10,20]) == [[],[10],[20],[10,20]]
    rows = python_algorithm.solve((1,2))
    rows[0].append(999)
    assert rows[1:] == [[1],[2],[1,2]]


def test_invalid(python_algorithm):
    for values in (None,True,1,"1",{1},[True],[1.0],[2147483648],[-2147483649],[0]*17,[0]*32):
        with pytest.raises(ValueError): python_algorithm.solve(values)


def test_cli(python_algorithm, oracle):
    for values in oracle.subset_vectors()[:6]:
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=" ".join(map(str,values)),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.recursive_subsets(values)
    for text in ("2147483648", "-2147483649", "0x10", "1.0", "true", "+", "0"*12, " ".join(["0"]*17)):
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout
