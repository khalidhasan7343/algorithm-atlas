import copy
import json
import subprocess
import sys
import pytest


def test_independent_oracles(python_algorithm, oracle, name):
    for args in oracle.vectors(name):
        saved=copy.deepcopy(args)
        assert python_algorithm.solve(*args)==oracle.expected(name,args),args
        assert args==saved


def test_invalid(python_algorithm, oracle, name):
    for args in oracle.invalid(name):
        with pytest.raises(ValueError):python_algorithm.solve(*args)


def test_boundaries(python_algorithm, oracle, name):
    oracle.boundaries(python_algorithm,name)


def test_cli(python_algorithm, oracle, name):
    for args in oracle.vectors(name)[:8]:
        result=subprocess.run([sys.executable,python_algorithm.__file__],input=oracle.cli(args),text=True,capture_output=True,timeout=10)
        assert result.returncode==0 and not result.stderr
        assert json.loads(result.stdout)==oracle.expected(name,args)
    for data in oracle.invalid_cli(name):
        result=subprocess.run([sys.executable,python_algorithm.__file__],input=data,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and result.stderr.startswith('error:') and not result.stdout
