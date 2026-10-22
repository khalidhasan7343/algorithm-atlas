import copy
import json
from pathlib import Path
import subprocess
import sys
import pytest


def test_independent_vectors(python_algorithm, cases):
    for case, expected in cases.vectors():
        saved=copy.deepcopy(case)
        assert python_algorithm.solve(**case)==expected, case
        assert case==saved


def test_invalid_contract(python_algorithm, cases):
    for case in cases.invalid():
        with pytest.raises((ValueError,TypeError)):
            python_algorithm.solve(**case)


def test_python_cli(python_algorithm, cases):
    case,expected=cases.vectors()[25]
    result=subprocess.run([sys.executable,python_algorithm.__file__],input=json.dumps(case),text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and json.loads(result.stdout)==expected and not result.stderr
    result=subprocess.run([sys.executable,python_algorithm.__file__],input='{"n":-1,"edges":[]}',text=True,capture_output=True,timeout=10)
    assert result.returncode==2 and result.stderr.startswith('error:')


def test_boundaries_and_invariants(python_algorithm, cases):
    cases.boundaries(python_algorithm)
