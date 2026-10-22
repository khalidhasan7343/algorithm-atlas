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
    for text in ['', '1', '1 2 3', '+ 2', '1.0 2', '1_0 2', '١ 2']:
        result=run([sys.executable,str(source)],text)
        assert result.returncode!=0 and result.stdout=="" and "error:" in result.stderr


def test_independent_builtin_multiplication_oracle(python_algorithm,cases):
    for a,b in cases.data():
        assert python_algorithm.karatsuba_multiplication(a,b)==a*b


@pytest.mark.parametrize("a,b",[(True,1),(1,False),(1.0,2),(None,1),("12",3)])
def test_invalid_types(python_algorithm,a,b):
    with pytest.raises(TypeError):python_algorithm.karatsuba_multiplication(a,b)
