import json
from pathlib import Path
import subprocess
import sys
import pytest


def run(command,text):
    return subprocess.run(command,input=text,text=True,capture_output=True,timeout=30)


def test_python_cli(cases):
    source=Path(__file__).parents[1]/"python/solution.py"
    for text,expected in cases.CLI_VALID:
        result=run([sys.executable,str(source)],text)
        assert result.returncode==0 and result.stderr==""
        assert json.loads(result.stdout)==expected
    for text in ['x', '+', '1 2x', '1.0', '١']:
        result=run([sys.executable,str(source)],text)
        assert result.returncode!=0 and result.stdout=="" and "error:" in result.stderr


def test_exhaustive_oracle_ties_extremes_and_no_mutation(python_algorithm,cases):
    for values in cases.data():
        before=values.copy();expected=cases.oracle(values)
        assert python_algorithm.maximum_subarray(values)==expected
        assert values==before
        assert python_algorithm.maximum_subarray(tuple(values))==expected


@pytest.mark.parametrize("value",[True,1.0,None,"1"])
def test_invalid_types(python_algorithm,value):
    with pytest.raises(TypeError):python_algorithm.maximum_subarray([value])


def test_python_unbounded_sum(python_algorithm):
    huge=1<<4096
    assert python_algorithm.maximum_subarray([huge,huge,-1])==(2*huge,0,2)
