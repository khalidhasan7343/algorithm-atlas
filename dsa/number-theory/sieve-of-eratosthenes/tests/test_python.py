import json
import subprocess
import sys
import pytest


def test_independent_mathematics(python_algorithm, oracle, name):
    for args in oracle.vectors(name):
        oracle.check(name,args,python_algorithm.solve(*args))


def test_invalid(python_algorithm, oracle, name):
    for args in oracle.invalid_numeric(name):
        with pytest.raises(ValueError): python_algorithm.solve(*args)
    arity = oracle.FUNCTIONS[name][1]
    for position in range(arity):
        for value in (True,False,None,1.0,"1",[]):
            args = list(oracle.vectors(name)[0])
            args[position] = value
            with pytest.raises(ValueError): python_algorithm.solve(*args)


def test_boundaries(python_algorithm, oracle, name):
    oracle.boundaries(python_algorithm,name)


def test_cli(python_algorithm, oracle, name):
    for args in oracle.vectors(name)[:8]:
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=" ".join(map(str,args)),text=True,capture_output=True,timeout=10)
        assert result.returncode==0 and not result.stderr
        oracle.check(name,args,json.loads(result.stdout))
    for data in ("", "0x10", "+", "1.0", "９", "1 "*4, "0"*21):
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=data,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and result.stderr.startswith("error:") and not result.stdout
