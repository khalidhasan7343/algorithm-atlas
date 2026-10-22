import copy
import json
from pathlib import Path
import subprocess
import sys
import pytest


def test_independent_oracles_and_no_mutation(python_algorithm,cases):
    for value in cases.data():
        before=copy.deepcopy(value)
        expected=cases.oracle(*value)
        result=python_algorithm.strassen_multiply(*value)
        assert result==expected and value==before
        assert python_algorithm.strassen_multiply(*value)==expected
        if result and isinstance(result[0],list):
            result[0].append(999)
            assert value==before and python_algorithm.strassen_multiply(*value)==expected


def test_invalid_types_shapes_bounds(python_algorithm,cases):
    for value,error in cases.invalid():
        before=copy.deepcopy(value)
        with pytest.raises(error):python_algorithm.strassen_multiply(*value)
        assert value==before


def test_cli(cases):
    source=Path(__file__).parents[1]/"python/solution.py"
    for text,expected in cases.CLI_VALID:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=30)
        assert result.returncode==0 and result.stderr=="" and json.loads(result.stdout)==expected
    for text in cases.CLI_INVALID:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=30)
        assert result.returncode!=0 and result.stdout=="" and "error:" in result.stderr
