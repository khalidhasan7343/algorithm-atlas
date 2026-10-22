"""Contract and independent-oracle tests for this algorithm."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import pytest


def test_independent_cases_order_and_input_restoration(python_algorithm, cases):
    for value,expected in cases.valid_cases():
        before=copy.deepcopy(value)
        result=cases.call(python_algorithm,value)
        assert result==expected and value==before
        assert cases.call(python_algorithm,value)==expected
        if isinstance(result,list) and result:
            if isinstance(result[0],list):
                result[0].append(999)
            else:
                result.append("changed")
            assert value==before and cases.call(python_algorithm,value)==expected


def test_invalid_inputs(python_algorithm, cases):
    for value,error in cases.invalid_cases():
        before=copy.deepcopy(value)
        with pytest.raises(error):
            cases.call(python_algorithm,value)
        assert value==before


def test_cli_valid_and_invalid(cases):
    source=Path(__file__).parents[1]/"python/solution.py"
    for text,expected in cases.CLI_VALID:
        proc=subprocess.run([sys.executable,str(source)],input=text,text=True,
                            capture_output=True,timeout=20,check=True)
        assert proc.stdout==json.dumps(expected,separators=(",",":"))+"\n"
        assert proc.stderr==""
    for text in cases.CLI_INVALID:
        proc=subprocess.run([sys.executable,str(source)],input=text,text=True,
                            capture_output=True,timeout=20)
        assert proc.returncode!=0 and proc.stdout=="" and "error:" in proc.stderr


def test_arbitrary_precision_prefixes_and_early_match(python_algorithm):
    big=1<<4096
    assert python_algorithm.subset_sum_backtracking([big,1,-big],1)==[0,1,2]
    assert python_algorithm.subset_sum_backtracking([1,0],1)==[0]
    assert python_algorithm.subset_sum_backtracking([-1,1,0],0)==[]
    class Integer(int): pass
    with pytest.raises(TypeError): python_algorithm.subset_sum_backtracking([Integer(1)],0)
    with pytest.raises(TypeError): python_algorithm.subset_sum_backtracking([],Integer(0))
